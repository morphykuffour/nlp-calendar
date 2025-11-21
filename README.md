# NLP Calendar

Create calendar events using natural language, integrated with [Talon](https://talonvoice.com/) voice control.

## Usage

### Voice Command (Talon)

```
schedule event meeting with John tomorrow at 3pm for 1 hour
```

### CLI

```bash
nix run . -- "lunch with Sarah on Friday at noon"
```

## Setup

1. Create config directory and add your OpenAI API key:

```bash
mkdir -p ~/.config/nlp-calendar
echo 'OPENAI_API_KEY="sk-..."' > ~/.config/nlp-calendar/env
```

2. Allow direnv (if using):

```bash
direnv allow
```

## How It Works

1. Natural language input is sent to OpenAI (gpt-4o-mini) for parsing
2. The parsed event is converted to an ICS file
3. On macOS, the ICS file is automatically opened in Calendar

## Requirements

- Nix (with flakes enabled)
- OpenAI API key
- Talon (for voice commands)
