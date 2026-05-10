import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  IonContent, IonHeader, IonToolbar, IonTitle, IonItem, IonLabel,
  IonInput, IonButton, IonSegment, IonSegmentButton, IonText, IonNote,
  IonIcon
} from '@ionic/angular/standalone';

import { AuthService } from '../core/auth.service';
import { setApiBaseUrl, loadApiBaseUrl } from '../core/config';

type Mode = 'login' | 'register';

@Component({
  selector: 'oj-login',
  standalone: true,
  imports: [
    FormsModule,
    IonContent, IonHeader, IonToolbar, IonTitle, IonItem, IonLabel,
    IonInput, IonButton, IonSegment, IonSegmentButton, IonText, IonNote
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ion-header><ion-toolbar><ion-title>Open-Jarvis</ion-title></ion-toolbar></ion-header>
    <ion-content class="ion-padding">
      <ion-segment [value]="mode()" (ionChange)="mode.set($any($event.detail.value))">
        <ion-segment-button value="login"><ion-label>Accedi</ion-label></ion-segment-button>
        <ion-segment-button value="register"><ion-label>Registrati</ion-label></ion-segment-button>
      </ion-segment>

      <ion-item>
        <ion-label position="stacked">Server URL</ion-label>
        <ion-input [(ngModel)]="apiUrl" name="apiUrl" placeholder="http://192.168.1.42:8090" />
      </ion-item>
      <ion-note color="medium" class="ion-padding-horizontal">
        L'IP del PC dove gira il server, oppure il dominio della tua VPS.
      </ion-note>

      @if (mode() === 'register') {
        <ion-item>
          <ion-label position="stacked">Nome</ion-label>
          <ion-input [(ngModel)]="displayName" name="displayName" />
        </ion-item>
      }

      <ion-item>
        <ion-label position="stacked">Email</ion-label>
        <ion-input [(ngModel)]="email" name="email" type="email" autocomplete="email" />
      </ion-item>

      <ion-item>
        <ion-label position="stacked">Password</ion-label>
        <ion-input [(ngModel)]="password" name="password" type="password" autocomplete="current-password" />
      </ion-item>

      @if (errorMessage()) {
        <ion-text color="danger" class="ion-padding-start"><p>{{ errorMessage() }}</p></ion-text>
      }

      <ion-button expand="block" (click)="submit()" [disabled]="loading()" class="ion-margin-top">
        {{ loading() ? 'Attendi…' : (mode() === 'login' ? 'Accedi' : 'Registrati e accedi') }}
      </ion-button>
    </ion-content>
  `
})
export class LoginPage {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  mode = signal<Mode>('login');
  apiUrl = '';
  email = '';
  password = '';
  displayName = '';
  loading = signal(false);
  errorMessage = signal<string | null>(null);

  constructor() {
    void loadApiBaseUrl().then((v) => (this.apiUrl = v));
  }

  async submit(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set(null);
    try {
      await setApiBaseUrl(this.apiUrl);
      if (this.mode() === 'register') {
        await this.auth.register(this.email, this.password, this.displayName);
      }
      const r = await this.auth.login(this.email, this.password);
      if ('mfa_required' in r) {
        this.errorMessage.set('MFA richiesto: il flow arriverà nella prossima release.');
        return;
      }
      this.router.navigateByUrl('/');
    } catch (err: unknown) {
      this.errorMessage.set(this.parseError(err));
    } finally {
      this.loading.set(false);
    }
  }

  private parseError(err: unknown): string {
    if (err && typeof err === 'object' && 'error' in err) {
      const body = (err as { error?: { detail?: unknown } }).error;
      if (body && typeof body === 'object' && 'detail' in body) {
        const d = (body as { detail: unknown }).detail;
        if (typeof d === 'string') return d;
      }
    }
    return 'Errore inatteso. Verifica server URL e credenziali.';
  }
}
