# Talon module for NLP calendar scheduling
from talon import Module, actions, app
import subprocess
import os

mod = Module()

@mod.action_class
class Actions:
    def schedule_event(text: str):
        """Send a natural language calendar request to our Python script"""
        flake_dir = os.path.dirname(__file__)

        try:
            # Use nix run to execute with proper dependencies
            cmd = ["nix", "run", f"{flake_dir}", "--", text]
            # Pass through environment variables (including OPENAI_API_KEY)
            env = os.environ.copy()
            # Run in background
            subprocess.Popen(cmd, env=env)
            app.notify("Scheduling calendar event...")
        except Exception as e:
            app.notify(f"Calendar scheduling failed: {e}")

