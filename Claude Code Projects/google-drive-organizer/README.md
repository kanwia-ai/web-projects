# Google Drive Organizer

Organizes files from My Drive into Enterprise/Clients folders based on filename patterns.

## Usage

```bash
# Step 1: Generate preview
python3 organize.py preview

# Step 2: Review CSV, mark approved moves with 'Y'

# Step 3: Dry run
python3 organize.py execute output/preview_TIMESTAMP.csv

# Step 4: Execute for real
python3 organize.py execute output/preview_TIMESTAMP.csv --execute

# If needed: Undo
python3 src/undo.py output/executed_TIMESTAMP.csv --execute
```
