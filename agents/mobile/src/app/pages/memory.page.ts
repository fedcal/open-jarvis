import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import {
  IonContent, IonHeader, IonToolbar, IonTitle, IonList, IonItem, IonLabel,
  IonItemSliding, IonItemOptions, IonItemOption, IonInput, IonButton, IonNote,
  IonIcon
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { trash } from 'ionicons/icons';

import { MemoryService } from '../core/memory.service';
import { MemoryItemPublic } from '../core/api.types';

@Component({
  selector: 'oj-memory-mobile',
  standalone: true,
  imports: [
    FormsModule, DatePipe,
    IonContent, IonHeader, IonToolbar, IonTitle, IonList, IonItem, IonLabel,
    IonItemSliding, IonItemOptions, IonItemOption, IonInput, IonButton, IonNote,
    IonIcon
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ion-header><ion-toolbar><ion-title>Memoria</ion-title></ion-toolbar></ion-header>
    <ion-content class="ion-padding">
      <ion-item>
        <ion-input [(ngModel)]="newItem" name="newItem" placeholder="Aggiungi un ricordo…"></ion-input>
        <ion-button slot="end" (click)="add()" [disabled]="!newItem.trim() || busy()">Salva</ion-button>
      </ion-item>

      @if (items().length === 0) {
        <ion-note color="medium">Nessun ricordo.</ion-note>
      }
      <ion-list>
        @for (item of items(); track item.id) {
          <ion-item-sliding>
            <ion-item lines="full">
              <ion-label>
                <h3>{{ item.content }}</h3>
                <p>{{ item.kind }} · {{ item.created_at | date:'short' }}</p>
              </ion-label>
            </ion-item>
            <ion-item-options side="end">
              <ion-item-option color="danger" (click)="forget(item)">
                <ion-icon name="trash" slot="icon-only"></ion-icon>
              </ion-item-option>
            </ion-item-options>
          </ion-item-sliding>
        }
      </ion-list>
    </ion-content>
  `
})
export class MemoryPage implements OnInit {
  private readonly memory = inject(MemoryService);

  newItem = '';
  busy = signal(false);
  items = signal<MemoryItemPublic[]>([]);

  constructor() {
    addIcons({ trash });
  }

  async ngOnInit(): Promise<void> {
    await this.refresh();
  }

  async refresh(): Promise<void> {
    try { this.items.set(await this.memory.list()); } catch { /* ignore */ }
  }

  async add(): Promise<void> {
    const text = this.newItem.trim();
    if (!text) return;
    this.busy.set(true);
    try {
      await this.memory.record(text);
      this.newItem = '';
      await this.refresh();
    } finally {
      this.busy.set(false);
    }
  }

  async forget(item: MemoryItemPublic): Promise<void> {
    await this.memory.forget(item.id);
    await this.refresh();
  }
}
