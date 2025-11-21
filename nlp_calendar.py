#!/usr/bin/env python3
import os
import sys
import json
import uuid
import datetime as dt
import subprocess

from openai import OpenAI

SYSTEM_PROMPT_TEMPLATE = """
You are a calendar event parser. Today's date is {today}.

Given a natural language instruction, extract a single event and return JSON with this exact schema:

{{
  "title": "short title string",
  "description": "optional description string",
  "timezone": "IANA timezone string, e.g. America/New_York",
  "start_datetime": "YYYY-MM-DDTHH:MM:SS",
  "end_datetime": "YYYY-MM-DDTHH:MM:SS",
  "recurrence": null OR {{
    "freq": "DAILY|WEEKLY|MONTHLY|YEARLY",
    "count": integer or null,
    "until": "YYYY-MM-DD" or null,
    "by_day": ["MO","TU","WE","TH","FR","SA","SU"] or []
  }}
}}

Rules:
- Assume timezone America/New_York if not specified.
- If end time is missing, default to 30 minutes after start.
- If user mentions "for N weeks" with a weekly pattern, use freq=WEEKLY and count=N occurrences.
- Use the first natural occurrence that matches the pattern. For example, for "every Friday at 7 PM for 8 weeks starting from the week of Mon Nov 24 2025", start on the first Friday on or after that Monday.
- Return JSON only, with no comments or extra text.
"""

def parse_event_with_openai(text: str) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")

    client = OpenAI(api_key=api_key)

    # Include today's date in the system prompt
    today = dt.date.today().strftime("%A, %B %d, %Y")
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(today=today)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )

    raw = response.choices[0].message.content  # plain text from the model
    try:
        event = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Could not parse JSON from model: {e}\nRaw output:\n{raw}")

    return event


def build_ics(event: dict) -> str:
    """
    Build a simple single VEVENT VCALENDAR string from parsed event dict.
    """
    uid = str(uuid.uuid4())
    dtstamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    tz = event.get("timezone", "America/New_York")

    start = dt.datetime.fromisoformat(event["start_datetime"])
    end = dt.datetime.fromisoformat(event["end_datetime"])

    dtstart = start.strftime("%Y%m%dT%H%M%S")
    dtend = end.strftime("%Y%m%dT%H%M%S")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//NLP Calendar Helper//EN",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;TZID={tz}:{dtstart}",
        f"DTEND;TZID={tz}:{dtend}",
        f"SUMMARY:{event.get('title','Untitled event')}",
    ]

    description = event.get("description")
    if description:
        # Basic escaping for commas and semicolons
        desc = description.replace(",", "\\,").replace(";", "\\;")
        lines.append(f"DESCRIPTION:{desc}")

    recur = event.get("recurrence")
    if recur:
        parts = [f"FREQ={recur.get('freq','WEEKLY')}"]
        if recur.get("count") is not None:
            parts.append(f"COUNT={int(recur['count'])}")
        if recur.get("until"):
            # until is date only YYYY-MM-DD
            until_date = dt.date.fromisoformat(recur["until"])
            parts.append(until_date.strftime("UNTIL=%Y%m%dT235959Z"))
        by_day = recur.get("by_day") or []
        if by_day:
            parts.append("BYDAY=" + ",".join(by_day))
        rrule = "RRULE:" + ";".join(parts)
        lines.append(rrule)

    lines.extend([
        "END:VEVENT",
        "END:VCALENDAR",
        ""
    ])

    return "\r\n".join(lines)


def main():
    if len(sys.argv) > 1:
        nl_text = " ".join(sys.argv[1:])
    else:
        print("Enter event description (end with Ctrl+D):")
        nl_text = sys.stdin.read().strip()

    if not nl_text:
        print("No text provided")
        sys.exit(1)

    print("Parsing event with OpenAI...")
    event = parse_event_with_openai(nl_text)

    ics_content = build_ics(event)

    # Basic filename using start date and title
    start_date = event["start_datetime"].split("T")[0]
    safe_title = "".join(c for c in event.get("title","event") if c.isalnum() or c in (" ", "_", "-"))
    filename = f"{start_date}_{safe_title.replace(' ', '_')}.ics"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(ics_content)

    print(f"ICS file written to {filename}")

    # On macOS, open in Calendar automatically
    if sys.platform == "darwin":
        try:
            subprocess.run(["open", filename], check=False)
            print("Opened ICS file. Apple Calendar should prompt you to add the event.")
        except Exception as e:
            print(f"Could not open file automatically: {e}")

    print("Import this ICS file into Google Calendar if you want it there.")


if __name__ == "__main__":
    main()

