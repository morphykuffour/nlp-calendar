# ~/.talon/user/nlp-calendar/calendar.talon
mode: command

# Dictate a calendar instruction and hand it to our Python action.
schedule event <user.text>:
    user.schedule_event(text)

