import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  IonContent, IonHeader, IonToolbar, IonTitle, IonList, IonItem, IonLabel,
  IonInput, IonButton, IonNote, IonRadioGroup, IonRadio, IonText
} from '@ionic/angular/standalone';

import { AuthService } from '../core/auth.service';
import { LlmService } from '../core/llm.service';
import { BackendInfo, OllamaModel } from '../core/api.types';
import { loadApiBaseUrl, setApiBaseUrl } from '../core/config';

@Component({
  selector: 'oj-settings-mobile',
  standalone: true,
  imports: [
    FormsModule,
    IonContent, IonHeader, IonToolbar, IonTitle, IonList, IonItem, IonLabel,
    IonInput, IonButton, IonNote, IonRadioGroup, IonRadio, IonText
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ion-header><ion-toolbar><ion-title>Impostazioni</ion-title></ion-toolbar></ion-header>
    <ion-content class="ion-padding">
      <h2>Server</h2>
      <ion-item>
        <ion-input [(ngModel)]="apiUrl" name="apiUrl" />
      </ion-item>
      <ion-button (click)="saveApi()">Salva URL</ion-button>

      <h2 class="ion-padding-top">Modelli LLM</h2>
      <ion-list>
        @for (b of backends(); track b.name) {
          <ion-item>
            <ion-label>
              <h3>{{ b.name }} {{ b.is_local ? '🟢 locale' : '☁️ cloud' }}</h3>
              <p>{{ b.model }}</p>
            </ion-label>
          </ion-item>
        }
      </ion-list>

      <h2 class="ion-padding-top">Ollama</h2>
      @if (ollamaError()) {
        <ion-text color="warning"><p>{{ ollamaError() }}</p></ion-text>
      } @else {
        <ion-list>
          @for (m of ollamaModels(); track m.name) {
            <ion-item>
              <ion-label>
                <h3>{{ m.name }}</h3>
                <p>{{ m.parameter_size ?? '?' }} · {{ humanSize(m.size) }}</p>
              </ion-label>
            </ion-item>
          }
        </ion-list>
      }

      <ion-button color="danger" expand="block" (click)="logout()" class="ion-margin-top">
        Esci
      </ion-button>
    </ion-content>
  `
})
export class SettingsPage implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly llm = inject(LlmService);

  apiUrl = '';
  backends = signal<BackendInfo[]>([]);
  ollamaModels = signal<OllamaModel[]>([]);
  ollamaError = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    this.apiUrl = await loadApiBaseUrl();
    try {
      const b = await this.llm.listBackends();
      this.backends.set(b.backends);
    } catch { /* ignore */ }
    try {
      const o = await this.llm.listOllamaModels();
      if (!o.reachable) {
        this.ollamaError.set(`Ollama non raggiungibile su ${o.base_url}`);
      } else {
        this.ollamaModels.set(o.models);
      }
    } catch {
      this.ollamaError.set('Errore richiesta');
    }
  }

  async saveApi(): Promise<void> {
    await setApiBaseUrl(this.apiUrl);
    location.reload();
  }

  logout(): void {
    void this.auth.logout();
  }

  humanSize(bytes: number): string {
    const mb = bytes / 1024 / 1024;
    if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
    return `${mb.toFixed(0)} MB`;
  }
}
