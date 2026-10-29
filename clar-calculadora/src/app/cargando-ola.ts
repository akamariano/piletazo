import { Component, input } from '@angular/core';

/** Indicador de carga: un tren de olas de mar con cresta que avanza dentro de una cápsula. */
@Component({
  selector: 'app-cargando-ola',
  template: `
    <span class="tanque" aria-hidden="true">
      <svg class="o fondo" viewBox="0 0 120 30" preserveAspectRatio="none">
        <path d="M0 18 C10 14 20 14 30 18 S50 22 60 18 S80 14 90 18 S110 22 120 18 V30 H0Z" />
      </svg>
      <svg class="o frente" viewBox="0 0 120 30" preserveAspectRatio="none">
        <!-- dos olas con cresta curvada por periodo de 60 -->
        <path
          d="M0 22 C8 22 14 18 19 12 C22 8 27 6 31 9 C33 11 32 14 29 13 C33 18 40 22 60 22
             C68 22 74 18 79 12 C82 8 87 6 91 9 C93 11 92 14 89 13 C93 18 100 22 120 22 V30 H0Z"
        />
        <path
          class="espuma"
          d="M19 12 C22 8 27 6 31 9 C33 11 32 14 29 13 M79 12 C82 8 87 6 91 9 C93 11 92 14 89 13"
        />
      </svg>
    </span>
    @if (texto()) {
      <span class="texto">{{ texto() }}</span>
    }
  `,
  host: { role: 'status', '[attr.aria-label]': 'texto() || "Cargando"' },
  styles: `
    :host { display: inline-flex; align-items: center; gap: 10px; color: var(--texto-2); font-size: 13px; }
    .tanque {
      position: relative; width: 64px; height: 24px; border-radius: 999px; overflow: hidden;
      border: 1px solid rgb(56 189 248 / 0.5);
      background: linear-gradient(180deg, #0a1a3f, #0d1117);
      box-shadow: inset 0 1px 3px rgb(1 4 9 / 0.6);
    }
    .o { position: absolute; left: 0; bottom: 0; width: 200%; height: 100%; }
    .fondo { fill: rgb(29 78 216 / 0.75); animation: avanzar 2.2s linear infinite reverse, mecer 1.1s ease-in-out infinite alternate; }
    .frente { animation: avanzar 1.3s linear infinite, mecer 0.9s ease-in-out infinite alternate-reverse; }
    .frente path:first-child { fill: #22b8e6; }
    .espuma { fill: none; stroke: #ecfeff; stroke-width: 2.2; stroke-linecap: round; }
    @keyframes avanzar { to { transform: translateX(-50%); } }
    @keyframes mecer { to { bottom: -3px; } }
    @media (prefers-reduced-motion: reduce) { .o { animation-duration: 5s; } }
  `,
})
export class CargandoOla {
  readonly texto = input('');
}
