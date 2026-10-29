"""
config.py
Loads configuration from environment variables (via a local .env file).
No secrets are hardcoded here. The .env file itself is never committed.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file sitting next to this file, if present.
load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "loco_info")
HHP_DB_NAME = os.environ.get("HHP_DB_NAME", "hhp_loco_info")

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "dev-only-change-me":
    raise ValueError("CRITICAL: SECRET_KEY environment variable is missing or set to unsafe default. Application startup aborted.")

if DB_PASSWORD == "":
    print("WARNING: DB_PASSWORD is empty. Check that your .env file exists "
          "and is loaded correctly before trusting any DB connection result.")