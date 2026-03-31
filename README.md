# mySpellChecker Telegram Bot

A Telegram bot that spell-checks Myanmar text using [mySpellChecker](https://myspellchecker.com/).

Send any Myanmar text and get corrections back instantly.

## Features

- **Spell checking** — send any Myanmar text, get corrections with a diff
- **Word segmentation** — `/segment` to see word boundaries with POS tags
- **Zawgyi detection** — `/zawgyi` to detect and convert Zawgyi to Unicode
- **Inline mode** — type `@botname <text>` in any chat to get corrected text

## Setup

### 1. Create a Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token
4. (Optional) Send `/setinline` to enable inline mode for your bot

### 2. Build the Dictionary

```bash
pip install "myspellchecker[build]"
myspellchecker build --sample
```

This creates `mySpellChecker-default.db` in the current directory. You can also build from your own corpus:

```bash
myspellchecker build -i corpus.txt -o mySpellChecker-default.db
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env and add your bot token
```

You can set a custom database path via the `MYSPELLCHECKER_DB` environment variable.

### 4. Run

**With Docker (recommended):**

```bash
docker-compose up --build -d
```

**Without Docker:**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m bot.main
```

## Usage

| Action | How |
|--------|-----|
| Spell check | Send any Myanmar text directly |
| Segment words | `/segment မြန်မာစာသား` or reply to a message with `/segment` |
| Zawgyi check | `/zawgyi ျမန္မာ` or reply to a message with `/zawgyi` |
| Inline mode | Type `@yourbotname မြနမ်ာ` in any chat |

## Powered by

[mySpellChecker](https://myspellchecker.com/) — Myanmar Language Text Intelligence Library

```bash
pip install myspellchecker
```

[Documentation](https://docs.myspellchecker.com/) · [GitHub](https://github.com/thettwe/myspellchecker)
