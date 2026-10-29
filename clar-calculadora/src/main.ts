import { bootstrapApplication } from '@angular/platform-browser';
import { inject } from '@vercel/analytics';
import { appConfig } from './app/app.config';
import { App } from './app/app';

// Vercel Web Analytics: visitas anónimas, sin cookies. En local no envía nada.
inject({ mode: location.hostname.endsWith('vercel.app') || !location.hostname.includes('localhost') ? 'production' : 'development' });

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
