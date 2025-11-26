# src/clients.py
"""Extract client folder names from Enterprise/Clients."""

import os
import re
from pathlib import Path
from config import CLIENTS_FOLDER

def get_client_folders() -> list[str]:
    """
    Get list of client folder names from Enterprise/Clients.
    Excludes files (only returns directories).
    """
    clients = []
    for item in os.listdir(CLIENTS_FOLDER):
        item_path = CLIENTS_FOLDER / item
        if item_path.is_dir():
            clients.append(item)
    return sorted(clients)


def build_client_variations(clients: list[str]) -> dict[str, str]:
    """
    Build a mapping of normalized client name variations to folder names.

    For example:
    - "AB InBev" -> variations include "ab inbev", "abinbev", "ab-inbev"
    - "e.l.f. Beauty" -> variations include "elf", "e.l.f."

    Returns: dict mapping lowercase variation -> original folder name
    """
    variations = {}

    for client in clients:
        # Original (lowercase)
        lower = client.lower()
        variations[lower] = client

        # Remove spaces
        no_spaces = lower.replace(" ", "")
        variations[no_spaces] = client

        # Replace spaces with common separators
        variations[lower.replace(" ", "-")] = client
        variations[lower.replace(" ", "_")] = client

        # Remove punctuation (for e.l.f. -> elf)
        no_punct = re.sub(r'[^\w\s]', '', lower)
        variations[no_punct] = client
        variations[no_punct.replace(" ", "")] = client

    return variations


if __name__ == "__main__":
    clients = get_client_folders()
    print(f"Found {len(clients)} client folders:")
    for c in clients[:10]:
        print(f"  - {c}")
    print("  ...")
