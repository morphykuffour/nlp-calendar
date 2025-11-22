# NLP Calendar voice commands
mode: command
-
# Dictate a calendar instruction and hand it to our Python action.
schedule event <user.text>:
    user.schedule_event(text)

