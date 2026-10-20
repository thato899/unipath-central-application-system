#!/usr/bin/env python
"""UniPath Django management entry point."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unipath_project.settings")

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line()
