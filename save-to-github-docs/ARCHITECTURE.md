# Save-to-GitHub Architecture

## Overview

The save-to-github system is a shell-based automation tool that automatically categorizes, documents, and pushes Claude Code projects to topic-based GitHub repositories. It provides both a command-line interface and a Claude Code slash command for seamless integration into development workflows.

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│  /save-to-github           ~/.claude/scripts/               │
│  (slash command)            save-to-github.sh                │
│                            (CLI interface)                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  Orchestration Layer                         │
├─────────────────────────────────────────────────────────────┤
│              save-to-github.sh (main)                        │
│  • Path resolution (file vs directory)                       │
│  • Workflow coordination                                     │
│  • Error handling and cleanup                                │
│  • User feedback and status reporting                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┼───────────┬──────────────┐
       │           │           │              │
┌──────▼─────┐ ┌──▼────┐ ┌────▼────┐ ┌──────▼────────┐
│Categorizer │ │Metadata│ │ README  │ │ GitHub Repo   │
│   Module   │ │Generator│ │Generator│ │   Manager     │
└────────────┘ └─────────┘ └─────────┘ └───────────────┘
       │           │           │              │
┌──────▼───────────▼───────────▼──────────────▼────────┐
│              Data/Config Layer                        │
├───────────────────────────────────────────────────────┤
│  ~/.claude/config/github-repos.json                   │
│  • Repository definitions                             │
│  • Category patterns and keywords                     │
│  • User configuration (GitHub username)               │
└───────────────────────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────────────┐
│            External Services Layer                    │
├───────────────────────────────────────────────────────┤
│  • GitHub API (via gh CLI)                            │
│  • Git (version control operations)                   │
└───────────────────────────────────────────────────────┘
```

## Core Components

### 1. Main Orchestrator (`save-to-github.sh`)

**Responsibility:** Coordinates the entire save workflow

**Flow:**
1. Accept path (file or directory) as input
2. Normalize to project directory structure
3. Invoke categorizer
4. Fetch repository config
5. Ensure GitHub repository exists
6. Generate metadata and README
7. Clone/initialize local repo copy
8. Copy project files
9. Commit and push to GitHub
10. Cleanup temporary files

**Key Features:**
- Handles both single files and directories
- Creates temporary project structure for single files
- Uses color-coded output for user feedback
- Implements cleanup on success or failure

### 2. Project Categorizer (`categorize-project.sh`)

**Responsibility:** Analyze project content and determine appropriate category

**Algorithm:**
1. Check for web-related keywords (highest priority)
   - Keywords: monitor, scraper, api, web, amtrak
   - Category: `web-projects`

2. Check for data-related keywords
   - Keywords: qr, data, csv, json, decode, analysis
   - Category: `data-projects`

3. Check for automation keywords
   - Keywords: automate, workflow, task, schedule
   - Category: `automation`

4. Default to python-scripts
   - If contains .py files
   - Category: `python-scripts`

**Design Decision:** Priority-based matching ensures specific categories (web, data) take precedence over generic (python-scripts)

### 3. Metadata Generator (`generate-metadata.sh`)

**Responsibility:** Create tracking metadata for projects

**Output Format:**
```json
{
  "name": "project-name",
  "category": "web-projects",
  "created": "2025-11-24T12:00:00Z",
  "last_updated": "2025-11-24T12:00:00Z",
  "description": "",
  "tags": [],
  "claude_sessions": [
    {
      "date": "2025-11-24T12:00:00Z",
      "summary": "Initial creation and upload"
    }
  ]
}
```

### 4. README Generator (`generate-readme.sh`)

**Responsibility:** Auto-generate documentation for projects without README

**Behavior:**
- Checks if README.md exists (non-destructive)
- Lists Python files in project
- Creates standard structure with placeholders
- Adds attribution to Claude Code

### 5. GitHub Repository Manager (`manage-github-repo.sh`)

**Responsibility:** Ensure target repository exists on GitHub

**Flow:**
1. Read GitHub username from config
2. Check if repository exists
3. Create repository if missing
4. Return repository URL

### 6. Installation Script (`install-save-to-github.sh`)

**Responsibility:** Setup dependencies and configuration

## Configuration System

### Repository Configuration (`github-repos.json`)

**Defined Categories:**
1. **python-scripts** - General Python utilities
2. **web-projects** - Web scrapers, monitors, API integrations
3. **data-projects** - Data analysis and processing
4. **automation** - Task automation and workflows

## Design Decisions

### 1. Shell-Based Architecture

**Rationale:**
- Native integration with git and gh CLI
- No runtime dependencies beyond standard tools
- Easy to debug and modify
- Fast execution

### 2. Topic-Based Repository Organization

**Rationale:**
- Groups related projects together
- Easier to browse by domain
- Reduces repository sprawl
- Maintains clean GitHub profile

### 3. Content-Based Categorization

**Rationale:**
- Intelligent default behavior
- No user input required
- Consistent categorization logic

### 4. Non-Destructive Operations

**Design Philosophy:**
- Never overwrite existing READMEs
- Check before creating repositories
- Preserve user customizations

### 5. Temporary Directory Strategy

**Rationale:**
- Isolates git operations from working directory
- Prevents conflicts with existing repos
- Enables atomic operations
- Clean failure modes

## File Locations

```
~/.claude/
├── commands/
│   └── save-to-github.md         # Slash command
├── config/
│   └── github-repos.json         # Configuration
└── scripts/
    ├── categorize-project.sh      # Categorizer
    ├── generate-metadata.sh       # Metadata
    ├── generate-readme.sh         # README
    ├── manage-github-repo.sh      # GitHub ops
    ├── save-to-github.sh          # Main script
    └── install-save-to-github.sh  # Installer
```

## Dependencies

- bash (4.0+)
- git (2.0+)
- gh (GitHub CLI 2.0+)
- jq (1.6+)
- rsync (for file copying)
