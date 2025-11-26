# src/config.py
"""Configuration constants for Google Drive Organizer."""

from pathlib import Path

# Google Drive paths
GDRIVE_ROOT = Path("/Users/kyraatekwana/Library/CloudStorage/GoogleDrive-katekwana@sectionai.com")
MY_DRIVE = GDRIVE_ROOT / "My Drive"
CLIENTS_FOLDER = GDRIVE_ROOT / "Shared drives/Enterprise/Clients"

# Project paths
PROJECT_DIR = Path("/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer")
OUTPUT_DIR = PROJECT_DIR / "output"

# Bracket prefixes that are NOT client names (should be ignored)
NON_CLIENT_PREFIXES = [
    "ARCHIVED",
    "INTERNAL",
    "OLD",
    "CUSTOMIZATION TEMPLATE",
    "MAKE A COPY",
    "NEW",
    "PUBLIC",
    "SECTION VERSION",
    "SPEAKER",
    "KYRA'S NOTES",
    "OLD DO NOT USE",
]
