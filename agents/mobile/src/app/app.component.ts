import { ChangeDetectionStrategy, Component } from '@angular/core';
import { IonApp, IonRouterOutlet } from '@ionic/angular/standalone';

@Component({
  selector: 'oj-root',
  standalone: true,
  imports: [IonApp, IonRouterOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<ion-app><ion-router-outlet /></ion-app>`
})
export class AppComponent {}
