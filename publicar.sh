#!/usr/bin/env bash
# Publica Piletazo en un repositorio público de GitHub.
#
# Uso:  ./publicar.sh [nombre-del-repo] [mensaje del commit]
#       ./publicar.sh                       # repo "piletazo", mensaje por defecto
#
# Requisitos: git y GitHub CLI (gh) con sesión iniciada (`gh auth login`).
#
# © 2026 Mariano Roberto Rac Noguera. Todos los derechos reservados.

set -euo pipefail

REPO="${1:-piletazo}"
MENSAJE="${2:-Piletazo: tu camino al cierre de pensum en Ingeniería en Ciencias y Sistemas USAC}"
DESCRIPCION="Piletazo: avance en el pensum CLAR 2022 de Ingeniería en Ciencias y Sistemas USAC, traslado desde el pensum anterior y rutas para cerrar pensum."
SITIO="https://akamariano.github.io/"
TEMAS="usac,ingenieria,ciencias-y-sistemas,pensum,clar-2022,angular,fastapi,python"

# Archivos con datos personales que nunca deben subirse.
PERSONALES=(
  "creditos Mariano.txt"
  "creditos_Mariano.txt"
  "2021/FIUSAC.html"
  "2021/FIUSAC_files_Mariano"
  "clar-calculadora/src/fixtures"
)

rojo()  { printf '\033[31m%s\033[0m\n' "$*"; }
verde() { printf '\033[32m%s\033[0m\n' "$*"; }
info()  { printf '\033[36m→ %s\033[0m\n' "$*"; }

cd "$(dirname "$0")"

# ---------- Requisitos ----------
command -v git >/dev/null || { rojo "Falta git."; exit 1; }
command -v gh  >/dev/null || { rojo "Falta GitHub CLI: brew install gh"; exit 1; }
gh auth status >/dev/null 2>&1 || { rojo "Inicia sesión primero: gh auth login"; exit 1; }

NOMBRE="$(git config user.name || true)"
CORREO="$(git config user.email || true)"
if [[ -z "$NOMBRE" || -z "$CORREO" ]]; then
  rojo "Configura tu identidad de git:"
  echo '  git config --global user.name  "Tu nombre"'
  echo '  git config --global user.email "tu@correo.com"'
  exit 1
fi
USUARIO="$(gh api user --jq .login)"
info "Publicando como $NOMBRE <$CORREO> en github.com/$USUARIO/$REPO"

# ---------- Repositorio local ----------
if [[ ! -d .git ]]; then
  info "Inicializando git"
  git init -q -b main
fi

git add -A

# ---------- Revisiones de seguridad antes del commit ----------
# 1. Ningún archivo personal en el área de preparación.
for ruta in "${PERSONALES[@]}"; do
  if git diff --cached --name-only | grep -qiF "$ruta"; then
    rojo "Se iba a subir un archivo personal: $ruta"
    rojo "Revisa .gitignore. No se hizo ningún cambio en GitHub."
    git reset -q
    exit 1
  fi
done

# También cualquier archivo con "creditos" y "mariano" en el nombre.
if git diff --cached --name-only | grep -qiE 'creditos.*mariano'; then
  rojo "Se iba a subir un archivo personal de créditos. Revisa .gitignore."
  git reset -q
  exit 1
fi

# 2. Ninguna mención a asistentes de IA en los archivos ni en el mensaje.
# (las palabras se arman por partes para que este archivo no las contenga literalmente)
PATRON="$(printf '%s|%s|%s|%s' 'cl''aude' 'anth''ropic' 'co-''authored-by' 'gene''rated with')"
if git grep --cached -I -n -i -E "$PATRON" >/tmp/piletazo-menciones.txt 2>/dev/null; then
  rojo "Hay menciones que no deben publicarse:"
  cat /tmp/piletazo-menciones.txt
  git reset -q
  exit 1
fi
if grep -qiE "$PATRON" <<<"$MENSAJE"; then
  rojo "El mensaje del commit contiene una mención no permitida."
  git reset -q
  exit 1
fi

# 3. Ningún archivo pesado por accidente (más de 20 MB).
while IFS= read -r archivo; do
  if [[ -f "$archivo" ]] && (( $(wc -c <"$archivo") > 20000000 )); then
    rojo "Archivo demasiado grande para el repositorio: $archivo"
    git reset -q
    exit 1
  fi
done < <(git diff --cached --name-only)

# ---------- Commit ----------
if git diff --cached --quiet; then
  info "No hay cambios nuevos para guardar"
else
  # Solo el mensaje indicado: sin trailers ni coautores.
  git commit -q --no-verify -m "$MENSAJE"
  verde "Commit creado: $(git log -1 --format='%h %s')"
fi

# ---------- GitHub ----------
if git remote get-url origin >/dev/null 2>&1; then
  info "Subiendo a $(git remote get-url origin)"
  git push -u origin main
elif gh repo view "$USUARIO/$REPO" >/dev/null 2>&1; then
  info "El repositorio ya existe; conectándolo y subiendo"
  git remote add origin "https://github.com/$USUARIO/$REPO.git"
  git push -u origin main
else
  info "Creando repositorio público github.com/$USUARIO/$REPO"
  gh repo create "$USUARIO/$REPO" --public --source=. --remote=origin --push \
    --description "$DESCRIPCION" --homepage "$SITIO"
fi

gh repo edit "$USUARIO/$REPO" --add-topic "$TEMAS" >/dev/null 2>&1 || true

verde "Listo: https://github.com/$USUARIO/$REPO"
echo
echo "Siguiente paso: publicar en Vercel"
echo "  1. Entra a https://vercel.com/new"
echo "  2. Importa $USUARIO/$REPO y pulsa Deploy (la configuración ya está en vercel.json)."
