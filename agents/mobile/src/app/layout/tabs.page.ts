import { ChangeDetectionStrategy, Component } from '@angular/core';
import { IonTabBar, IonTabButton, IonTabs, IonIcon, IonLabel } from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { chatbubbles, library, settings } from 'ionicons/icons';

@Component({
  selector: 'oj-tabs',
  standalone: true,
  imports: [IonTabs, IonTabBar, IonTabButton, IonIcon, IonLabel],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ion-tabs>
      <ion-tab-bar slot="bottom">
        <ion-tab-button tab="chat" href="/chat">
          <ion-icon name="chatbubbles"></ion-icon>
          <ion-label>Chat</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="memory" href="/memory">
          <ion-icon name="library"></ion-icon>
          <ion-label>Memoria</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="settings" href="/settings">
          <ion-icon name="settings"></ion-icon>
          <ion-label>Impostazioni</ion-label>
        </ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>
  `
})
export class TabsPage {
  constructor() {
    addIcons({ chatbubbles, library, settings });
  }
}
