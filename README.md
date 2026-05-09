# Gmail Cleaner Pro

A **powerful**, privacy-focused Gmail cleanup tool with dark mode, email preview, smart filters, and scheduled rules. Bulk unsubscribe, delete, mark as read, and organize your inbox — all running 100% on your machine.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)
![Gmail API](https://img.shields.io/badge/Gmail-API-EA4335?style=flat-square&logo=gmail)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen?style=flat-square)

> **Free Forever — No Subscription, No Data Collection**

## What's New in v2.0

| Feature | Description |
|---------|-------------|
| 🌙 **Dark Mode** | Automatic detection + manual toggle, persisted preference |
| 👁️ **Email Preview** | Preview email content before deleting — see subjects, dates, and body text |
| 🎯 **Better Filters** | Inbox-only scope, has/no-attachment filter, spam+trash inclusion |
| 📅 **Cleanup Rules** | Save recurring cleanup rules for senders you always want to delete |
| ⌨️ **Keyboard Shortcuts** | Power user shortcuts for navigation, scanning, and selection |
| 🐛 **Bug Fixes** | Fixed token save failures, Docker OAuth mismatch, auth errors |

## All Features

| Feature | Description |
|---------|-------------|
| **Bulk Unsubscribe** | Find newsletters and unsubscribe with one click |
| **Delete by Sender** | Scan and see who sends you the most emails, delete in bulk |
| **Bulk Delete Multiple Senders** | Delete emails from multiple senders simultaneously with progress tracking |
| **Mark as Read** | Bulk mark thousands of unread emails as read |
| **Archive Emails** | Archive emails from selected senders (remove from inbox) |
| **Label Management** | Create, delete, and apply/remove labels to emails from specific senders |
| **Mark Important** | Mark or unmark emails from selected senders as important |
| **Email Download** | Download email metadata for selected senders as CSV |
| **Email Preview** | Preview email content before taking destructive actions |
| **Smart Filters** | Filter by date range, size, category, sender, labels, attachments, inbox scope |
| **Cleanup Rules** | Save persistent rules to auto-delete/archive from specific senders |
| **Keyboard Shortcuts** | Ctrl+1/2/3 for views, Ctrl+K for filters, Ctrl+S to scan, Ctrl+A select all |
| **Dark Mode** | System-aware with manual override, persisted in localStorage |
| **Privacy First** | Runs locally — your data never leaves your machine |
| **Super Fast** | Gmail API with batch requests (100 emails per API call) |

## Quick Start

### Option A: Docker (Recommended)

```bash
# 1. Get Google OAuth credentials (see Setup below)
# 2. Clone and setup
git clone https://github.com/GadatheGod/gmail-cleaner-pro.git
cd gmail-cleaner-pro
# Place credentials.json in the project folder

# 3. Run
docker compose pull && docker compose up
```

Open http://localhost:8766 in your browser.

### Option B: Python (Local)

```bash
# Prerequisites: Python 3.9+ and uv (https://docs.astral.sh/uv/)
git clone https://github.com/GadatheGod/gmail-cleaner-pro.git
cd gmail-cleaner-pro
uv sync
uv run python main.py
```

## Setup Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → Enable **Gmail API**
3. Go to **OAuth consent screen** → Configure (External, add your email as test user)
4. Go to **Credentials** → Create OAuth client:
   - **Local/Python**: Desktop app
   - **Docker**: Web app with redirect `http://localhost:8767/`
5. Download JSON → rename to `credentials.json` → place in project folder

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + 1` | Switch to Unsubscribe view |
| `Ctrl/Cmd + 2` | Switch to Delete Emails view |
| `Ctrl/Cmd + 3` | Switch to Mark as Read view |
| `Ctrl/Cmd + K` | Toggle filter bar |
| `Ctrl/Cmd + S` | Start scan |
| `Ctrl/Cmd + A` | Select all results |
| `Escape` | Clear all filters |

## Smart Filters

- **Date Range**: Preset (7d, 30d, 90d, 6mo, 1yr) or custom range picker
- **Size**: Filter by minimum email size (1MB, 5MB, 10MB, 25MB)
- **Category**: Promotions, Social, Updates, Forums, Primary
- **Sender**: Filter by specific email or domain
- **Label**: Filter by Gmail label
- **Attachment**: Has attachment / No attachment (NEW)
- **Scope**: All mail / Inbox only (NEW)

## Keyboard Shortcuts

## Cleanup Rules

Save persistent rules to automate cleanup:

1. Scan for senders → select senders
2. Click "Add Rule" button
3. Choose action: Delete, Archive, Mark Read, or Label
4. Set schedule: Manual, Daily, Weekly, Monthly
5. Run rules on-demand or let them persist for future use

## Security & Privacy

- **100% Local** — No external servers, no data collection
- **Open Source** — Inspect all the code yourself
- **Minimal Permissions** — Only requests read + modify scope
- **Your Credentials** — You control your own Google OAuth app
- **Gitignored Secrets** — `credentials.json` and `token.json` never committed

## Advanced Configuration

### Custom Domain / Remote Server

```yaml
environment:
  - WEB_AUTH=true
  - OAUTH_HOST=gmail.example.com
  - OAUTH_EXTERNAL_PORT=18767
```

### Custom Port Mapping

```yaml
ports:
  - "18766:8766"
  - "18767:8767"
environment:
  - OAUTH_EXTERNAL_PORT=18767
```

## Troubleshooting

### Token save fails (Docker)

Files in `./data/` are owned by root. Fix with:
```bash
sudo chown -R $USER:$USER ./data/
```

### OAuth redirect_uri_mismatch

Ensure your Google Cloud Console redirect URI matches your setup:
- Local Python: No redirect URI needed (Desktop app)
- Docker localhost: `http://localhost:8767/`
- Custom domain: `http://YOUR_DOMAIN:8767/`

### "Google hasn't verified this app" warning

This is **expected and safe** — click **Continue**. It appears because you created your own OAuth app.

## FAQ

**Q: Why create my own Google Cloud project?**
Because this app accesses your Gmail. Using your own OAuth credentials means you have full control and trust no third party.

**Q: Is this safe?**
Yes! Open source, local-only processing. Your emails never leave your machine.

**Q: Can I use multiple Gmail accounts?**
Yes! Sign out and sign in with a different account. Add each account as a test user in Google Cloud Console.

**Q: Can I recover deleted emails?**
Yes! Emails go to Trash and are recoverable for 30 days from Gmail's Trash folder.

## Contributing

PRs welcome! Areas for contribution:
- UI improvements and accessibility
- New filter options
- IMAP support for non-Gmail providers
- Scheduled rule automation engine
- Windows installation docs

## License

MIT — See [LICENSE](LICENSE) file.

---

**Built with** FastAPI · Gmail API · Docker · Vanilla JS · CSS

Made to help you escape email hell 🧹