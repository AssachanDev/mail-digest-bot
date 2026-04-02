<div align="center">

# Mail Digest Bot

**A Gmail summarizer bot for Telegram.**

Automatically monitors your Gmail inbox, summarizes new emails using a local LLM (Ollama), and delivers concise bullet-point digests straight to your Telegram.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram_Bot-v20+-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-llama3.1:8b-black?style=flat-square&logo=ollama&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

</div>

---

## ✨ Features

- **Auto-polling** — checks Gmail every 2 minutes in the background
- **AI summaries** — sends emails to a local Ollama instance (llama3.1:8b) and returns bullet-point digests
- **History** — view the last 5 summaries at any time via a single keyboard button
- **Remote Ollama support** — bot and Ollama can run on different servers

---

## 🔧 Stack

| | Tool |
|-|------|
| Language | Python 3.10+ |
| Telegram | [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v20+ |
| Gmail | Google Gmail API + OAuth 2.0 |
| LLM | [Ollama](https://ollama.com) — llama3.1:8b (recommended) |
| Scheduler | `job_queue` (built into python-telegram-bot) |

---

## 📁 Project Structure

```
mail-digest-bot/
├── main.py                      # Entry point, bot init, polling scheduler
├── handlers/
│   ├── command_handlers.py      # Reply keyboard, snooze callbacks, history
│   └── polling_handler.py       # Background email polling task
├── services/
│   ├── base_mail_service.py     # Abstract base class
│   ├── gmail_service.py         # Gmail API integration
│   ├── ollama_service.py        # HTTP client for Ollama
│   ├── prompt_builder.py        # Prompt formatting for LLM
│   └── state_manager.py         # Persist polling state, history, snooze
├── credentials.json             # Gmail OAuth (gitignored)
├── gmail_token.json             # Gmail token cache (gitignored)
├── state.json                   # Runtime state (gitignored)
├── .env                         # Secrets (gitignored)
├── .env.example                 # Template
└── requirements.txt
```

---

## 🚀 Setup

<details>
<summary><b>1. Telegram Bot</b></summary>

<br>

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. `/newbot` → follow prompts → copy the bot token
3. Get your personal User ID by messaging [@userinfobot](https://t.me/userinfobot)

</details>

<details>
<summary><b>2. Gmail API (Google Cloud Console)</b></summary>

<br>

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. "Mail Digest Bot")
3. Enable **Gmail API** — search for it under APIs & Services
4. Go to **Credentials** → Create Credentials → **OAuth 2.0 Client ID**
   - Application type: **Desktop app**
   - Download the JSON → save as `credentials.json` in the project root
5. Go to **OAuth consent screen** → scroll down to **Test users** → **+ Add Users** → add your Gmail address → Save
6. Run `auth.py` on your **local machine** (requires a browser) to generate the token:

```bash
python auth.py
```

A browser window will open → sign in → allow access → `gmail_token.json` will be created.

7. If the bot runs on a remote server, copy the token there:

```bash
scp gmail_token.json user@your-server:/path/to/mail-digest-bot/
```

> **Scope used:** `gmail.readonly` — read only, no send or delete access

</details>

<details>
<summary><b>3. Ollama (LLM Server)</b></summary>

<br>

**If Ollama runs on the same server as the bot:**
```bash
ollama serve
ollama pull llama3.1:8b
```

**Recommended models** (CPU-only, no GPU required):

| Model | RAM | Quality | Speed |
|-------|-----|---------|-------|
| llama3.1:8b *(recommended)* | ~5GB | Great | Medium |
| llama3.2:3b | ~2GB | Fair | Fast |

> To switch models, update `OLLAMA_MODEL` in `.env` and pull the new model with `ollama pull <model>`.

**If Ollama runs on a separate server (Server A) and the bot runs on Server B:**

On Server A — bind to all interfaces:
```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

Or configure via systemd on Server A:
```bash
sudo systemctl edit ollama
```
Add the following (leave everything else untouched):
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```
Then reload:
```bash
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

Restrict access via firewall (allow only Server B):
```bash
ufw allow from <SERVER_B_IP> to any port 11434
```

Then in `.env` on Server B:
```env
OLLAMA_HOST=http://<SERVER_A_IP>:11434
```

</details>

<details>
<summary><b>4. Environment Variables</b></summary>

<br>

```bash
cp .env.example .env
```

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_user_id

# Gmail
GMAIL_CREDENTIALS_FILE=credentials.json

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Bot
POLLING_INTERVAL_SECONDS=120
```

</details>

<details>
<summary><b>5. Install & Run</b></summary>

<br>

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

</details>

<details>
<summary><b>6. Run as systemd Service (auto-start on boot)</b></summary>

<br>

**Step 1 — Find your paths**

```bash
whoami        # your username
pwd           # run inside the project folder to get the full path
```

**Step 2 — Create the service file**

```bash
sudo nano /etc/systemd/system/mail-digest-bot.service
```

Paste this (replace `your_user` and paths):

```ini
[Unit]
Description=Mail Digest Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/your_user/mail-digest-bot
ExecStart=/home/your_user/mail-digest-bot/venv/bin/python3 main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Step 3 — Enable and start**

```bash
sudo systemctl daemon-reload                       # reload after creating/editing service file
sudo systemctl enable mail-digest-bot.service      # auto-start on boot
sudo systemctl start mail-digest-bot.service       # start now
```

**Step 4 — Verify it's running**

```bash
sudo systemctl status mail-digest-bot.service
```

You should see `Active: active (running)`.

**Useful commands**

```bash
# View live logs
sudo journalctl -u mail-digest-bot.service -f

# Restart after code changes
sudo systemctl restart mail-digest-bot.service

# Stop the bot
sudo systemctl stop mail-digest-bot.service

# Disable auto-start on boot
sudo systemctl disable mail-digest-bot.service
```

</details>

---

## 🎛️ Interface

The bot uses a **persistent Reply Keyboard** — no typing required.

```
[ 📋 History ]  [ 🗑 Clear History ]
```

| Button | Description |
|--------|-------------|
| 📋 History | View last 5 email summaries |
| 🗑 Clear History | Clear all stored summaries |

---

## 📬 Summary Format

When new emails arrive, the bot sends:

```
📮 New emails — Gmail

Monthly Performance Review
• 3 actions due: review Node-04 thermal logs, verify dataset, firmware update by Apr 5
• Thermal spike 82.4°C on Gateway-Node-04 — needs ZRAM swap + fan threshold fix

GitHub Authentication Code
• Verify identity with code 66694264 — expires in 15 min
```

- Subject line per email, followed by 1–2 bullet points
- Prioritizes action items and deadlines over general info

---

## 🛠️ Troubleshooting

<details>
<summary><b>Bot starts but no emails are coming through</b></summary>

<br>

1. Check that `TELEGRAM_USER_ID` is correct — the bot only sends to this ID
2. Send `/start` to the bot to verify it's alive and see the keyboard
3. Press ℹ️ Status to confirm polling is active and see last poll time
4. Check logs: `sudo journalctl -u mail-digest-bot.service -f`

</details>

<details>
<summary><b>Gmail auth fails on first run</b></summary>

<br>

Run `auth.py` on a local machine (with a browser) to generate `gmail_token.json`, then copy it to the server. The browser prompt will not appear again.

```bash
python auth.py
scp gmail_token.json user@your-server:/path/to/mail-digest-bot/
```

</details>

<details>
<summary><b>Ollama timeout or connection refused</b></summary>

<br>

- Verify Ollama is running: `curl http://<OLLAMA_HOST>:11434/api/tags`
- If on a remote server, ensure port 11434 is open and Ollama is bound to `0.0.0.0`
- Check that the model is pulled: `ollama list`

</details>

---

## 📄 License

MIT
