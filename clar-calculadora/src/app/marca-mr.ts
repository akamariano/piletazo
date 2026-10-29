import { Component } from '@angular/core';

let contador = 0;

// Monograma "MR" de akamariano.github.io (assets/favicon.svg).
@Component({
  selector: 'app-marca-mr',
  template: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Mariano Rac">
    <defs>
      <linearGradient [attr.id]="id" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#0071e3" />
        <stop offset="100%" stop-color="#7b5cff" />
      </linearGradient>
    </defs>
    <rect width="64" height="64" rx="16" [attr.fill]="'url(#' + id + ')'" />
    <text
      x="32"
      y="42"
      text-anchor="middle"
      font-family="-apple-system, Helvetica, Arial, sans-serif"
      font-size="28"
      font-weight="700"
      fill="#ffffff"
    >
      MR
    </text>
  </svg>`,
  styles: `
    :host { display: inline-flex; width: 1em; height: 1em; flex-shrink: 0; }
    svg { width: 100%; height: 100%; display: block; }
  `,
})
export class MarcaMr {
  protected readonly id = `mr-degradado-${++contador}`;
}
