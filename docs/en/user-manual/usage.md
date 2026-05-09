# Daily usage

Once installed and configured, here is how to **live with Jarvis on a daily basis**.

## The three interaction modes

| Mode | When | How |
|---|---|---|
| 🗨️ **Chat** | Complex tasks, reasoning, research | Web UI or mobile app |
| 🎙️ **Voice** | On the move, hands-free, smartwatch | Wake-word "Hey Jarvis" |
| 👆 **Quick action** | Single commands, automations | Push notification, watch gesture, OS shortcut |

## Cross-device conversations

The conversation **is not bound to the device**: it is bound to you.

Example:

1. 9:00 — at your PC you ask "find me articles on the November Claude model"
2. 13:00 — at the restaurant, you ask your phone: "send me those two articles for tonight"
3. 22:00 — on the couch, on the tablet: "read me the first one, summarise it"

Jarvis knows it is the **same conversation** and keeps the context.

## Automatic routing

Jarvis picks the device best suited to the context:

| Situation | Picked device | Reason |
|---|---|---|
| You are running | Smartwatch | hands-free, haptic |
| You are driving | Car / mobile + glasses | TTS + AR overlay |
| You are at PC | Desktop | complex tasks, IDE |
| You are sleeping | None | Do Not Disturb |
| You are in a meeting | Notifications suppressed | Focus mode |

You can force routing with `@desktop`, `@mobile`, `@watch`.

## Daily features

### Daily briefing

Ask in the morning: *"give me the briefing"*. You will receive:

- 📰 Top 3 news stories (see [News](../features/news.md))
- 📅 Agenda with events and priorities
- 💼 Financial stat (balance, significant changes)
- 🏃 Health status (recovery, sleep score)
- ⏰ Reminders and upcoming deadlines

### Personal memory

Everything you say to Jarvis is remembered (with your consent).

```
You: "Remember that my birthday is March 15"
Jarvis: "Stored in long-term."

[months later]
You: "When is my birthday?"
Jarvis: "March 15. Want me to suggest activities?"
```

To forget:

```
You: "Forget my preferences on vegetarian restaurants"
```

### Questions about your documents (RAG)

If you connected Obsidian / Notion / Drive (see [RAG](../features/rag.md)):

```
You: "When did I take those notes on serverless architectures?"
Jarvis: "You have a note from March 12 in your Obsidian vault, folder 'work/architecture'."
```

### Useful voice commands

- "Hey Jarvis, **remind me** to call the doctor at 4 pm"
- "Hey Jarvis, **timer** 25 minutes"
- "Hey Jarvis, **living room lights** to 30%"
- "Hey Jarvis, **translate** 'have a nice day' to French"
- "Hey Jarvis, **how did I sleep** last night?"
- "Hey Jarvis, **what is my crypto net worth**?"

## Privacy and control

- 🔇 **Total mute**: triple-tap on the logo in the app — Jarvis stops listening until you re-enable
- 🌙 **Night mode**: no notifications from 10 pm to 7 am
- 🚫 **Guest mode**: new devices cannot be paired
- 🗑️ **Right to be forgotten**: "Delete everything" button in settings

## Advanced configurations

- [Plugin marketplace](../features/developer.md) — install specific skills
- [Smart home](../integrations/other-systems.md) — enable Home Assistant
- [Maker](../features/maker.md) — connect Blender and 3D printers

> Got issues? Go to → [Troubleshooting](troubleshooting.md)
