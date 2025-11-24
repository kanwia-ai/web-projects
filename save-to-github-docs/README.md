# Save-to-GitHub Command

A shell-based automation system for Claude Code that automatically categorizes and saves projects to topic-based GitHub repositories.

## What It Does

The save-to-github command analyzes your project, determines what category it belongs to (web projects, data projects, automation, or Python scripts), and automatically pushes it to the appropriate GitHub repository with generated metadata and documentation.

## Quick Start

```bash
# In Claude Code
/save-to-github

# Or from command line
~/.claude/scripts/save-to-github.sh /path/to/project
```

## Features

- **Automatic Categorization**: Analyzes project content and assigns to appropriate repository
- **Metadata Tracking**: Creates `.claude-metadata.json` with timestamps and session history
- **Auto-Documentation**: Generates README.md if one doesn't exist
- **Topic-Based Organization**: Groups related projects in four repositories:
  - `python-scripts` - General Python utilities
  - `web-projects` - Web scrapers, monitors, API integrations
  - `data-projects` - Data analysis and processing
  - `automation` - Task automation and workflows

## How It Works

1. Analyzes project directory or file
2. Scans content for keywords to determine category
3. Creates/verifies GitHub repository exists
4. Generates metadata and README (if needed)
5. Commits and pushes to appropriate repository
6. Reports success with repository URL

## Development Process Reflections

### What Made This Project Successful

**1. Detailed Planning First**

I created comprehensive implementation plans before writing code:
- 10-12 tasks broken down into discrete steps
- Each step included expected outputs
- Verification steps after each task
- Clear file paths and code examples

This upfront planning made execution straightforward and reduced backtracking.

**2. Modular Design**

Each script has a single, clear responsibility:
- `categorize-project.sh` - Content analysis only
- `generate-metadata.sh` - Metadata creation only
- `save-to-github.sh` - Orchestration only

This made testing easier and allowed components to be developed independently.

**3. Config-Driven Behavior**

Centralizing repository definitions in `github-repos.json` meant:
- No code changes to add new categories
- Easy customization for different users
- Clear separation of data and logic
- Simple to understand what categories exist

**4. Incremental Testing**

Testing at multiple levels caught issues early:
- Unit tests for each script
- Integration tests with test directories
- End-to-end tests with real projects

**5. User Experience Focus**

The slash command interface makes the system accessible:
- Single command to save any project
- Clear progress messages
- Error handling with helpful output
- No manual configuration needed

### Key Learnings

**Start with the Plan**

Writing detailed plans with verification steps created a roadmap that:
- Reduced decision fatigue during implementation
- Provided clear checkpoints for progress
- Made it easy to resume after breaks
- Served as documentation of intent

**Shell Scripts Are Powerful**

For development tooling, shell scripts offer:
- Direct access to system tools (git, gh)
- Fast iteration without compile cycles
- Easy to read and debug
- Natural fit for file operations

**Configuration Over Code**

The `github-repos.json` approach proved valuable:
- Users can customize without touching code
- Easy to add new categories
- Clear contract between scripts
- Testable with different configs

**Non-Destructive By Default**

Design choices that preserved existing work:
- Never overwrite existing READMEs
- Check before creating repositories
- Temp directories for git operations

This made the tool safe to use repeatedly.

### Process Template for Future Projects

This project established a reusable pattern:

1. **Define the Goal** - Clear, specific outcome
2. **Design the Architecture** - Components and interactions
3. **Create Implementation Plan** - Task breakdown with verification
4. **Build Modularly** - One component at a time
5. **Test Incrementally** - Unit → Integration → E2E
6. **Create User Interface** - Make it accessible (slash command)
7. **Document** - Architecture and usage

### What I'd Do Differently

**Add More Validation**

Earlier validation would catch issues before operations:
- Check GitHub auth before starting
- Verify disk space for clones
- Validate config file format on startup

**Better Error Messages**

More specific failure descriptions:
- What went wrong
- Where it happened
- How to fix it

**Logging System**

Persistent logs for troubleshooting:
- Timestamp all operations
- Log decisions (why this category?)
- Capture errors for later analysis

**Interactive Mode**

Allow manual overrides:
- Choose category if auto-detection is wrong
- Select private vs public repository
- Edit generated README before push

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design, data flow, and component documentation.

## Installation

```bash
~/.claude/scripts/install-save-to-github.sh
```

This will:
- Install dependencies (jq, gh CLI)
- Authenticate with GitHub
- Set up configuration
- Make scripts executable

## Usage Examples

### Save Current Directory
```bash
cd my-project
/save-to-github
```

### Save Specific Project
```bash
~/.claude/scripts/save-to-github.sh ~/projects/my-script
```

### Save Single File
```bash
~/.claude/scripts/save-to-github.sh script.py
```

## Project Structure

After saving, projects are organized like this:

```
github.com/username/python-scripts/
├── script-1/
│   ├── .claude-metadata.json
│   ├── README.md
│   └── main.py
├── script-2/
│   ├── .claude-metadata.json
│   ├── README.md
│   └── app.py
...
```

Each project gets its own subdirectory within the category repository.

## Extending the System

### Add a New Category

1. Edit `~/.claude/config/github-repos.json`:
```json
{
  "repositories": {
    "new-category": {
      "name": "new-category",
      "description": "Description here",
      "patterns": ["*.ext"],
      "keywords": ["keyword1", "keyword2"]
    }
  }
}
```

2. Add detection logic to `~/.claude/scripts/categorize-project.sh`

### Customize Metadata

Edit `~/.claude/scripts/generate-metadata.sh` to add fields:
```bash
cat > "$PROJECT_PATH/.claude-metadata.json" << EOF
{
  "name": "$PROJECT_NAME",
  "custom_field": "value",
  ...
}
EOF
```

## Related Files

- Implementation plans in `~/docs/plans/`
  - `2024-11-23-save-to-github-command.md` - Initial plan
  - `2025-11-24-complete-save-to-github.md` - Completion plan

## Meta: This Project Saved Itself

This documentation was created and saved to GitHub using the save-to-github system itself - a fitting demonstration of the tool's capabilities.
