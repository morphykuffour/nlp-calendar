# Talon module for NLP calendar scheduling
from talon import Module, actions, app
import subprocess
import os
import logging

mod = Module()
logger = logging.getLogger(__name__)

# Full path to nix since Talon GUI apps don't inherit shell PATH
NIX_PATH = "/nix/var/nix/profiles/default/bin/nix"

@mod.action_class
class Actions:
    def schedule_event(text: str):
        """Send a natural language calendar request to our Python script"""
        flake_dir = os.path.dirname(__file__)
        logger.info(f"schedule_event called with: {text}")
        logger.info(f"flake_dir: {flake_dir}")

        try:
            cmd = [NIX_PATH, "run", flake_dir, "--", text]
            logger.info(f"Running command: {cmd}")

            # Pass through environment variables (including OPENAI_API_KEY)
            env = os.environ.copy()
            # Add nix paths to PATH in case nix run needs them
            env["PATH"] = f"/nix/var/nix/profiles/default/bin:{env.get('PATH', '')}"

            # Run in background
            subprocess.Popen(cmd, env=env)
            app.notify("Scheduling calendar event...")
        except Exception as e:
            logger.error(f"Calendar scheduling failed: {e}")
            app.notify(f"Calendar scheduling failed: {e}")

