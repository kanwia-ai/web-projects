# Superpowers Skills for Claude

A collection of 20 Claude Agent Skills from the [Superpowers plugin](https://github.com/superpowers-marketplace), reorganized with the proper folder structure for importing into the **Claude web app**.

## How to Import

1. Download the zip file for the skill you want (or zip the skill folder yourself)
2. Go to [claude.ai](https://claude.ai)
3. Navigate to **Settings > Capabilities > Skills**
4. Upload the zip file
5. The skill will be available across your conversations

## Folder Structure

Each skill follows the standard Claude Skills structure:

```
skill-name/
├── SKILL.md          # Core instructions (required)
├── scripts/          # Executable code (Python/Bash/TypeScript)
├── references/       # Documentation loaded into context as needed
└── assets/           # Templates and files used in output
```

## Skills Included

### Development Workflow
| Skill | Description |
|-------|-------------|
| **test-driven-development** | Write tests first, watch them fail, write minimal code to pass |
| **systematic-debugging** | Four-phase debugging: root cause, pattern analysis, hypothesis testing, implementation |
| **verification-before-completion** | Run verification commands before claiming work is complete |
| **root-cause-tracing** | Trace bugs backward through call stack to find original trigger |

### Code Quality
| Skill | Description |
|-------|-------------|
| **testing-anti-patterns** | Avoid testing mock behavior, production pollution, mocking without understanding |
| **condition-based-waiting** | Replace arbitrary timeouts with condition polling for reliable async tests |
| **defense-in-depth** | Validate at every layer to make bugs structurally impossible |
| **receiving-code-review** | Require technical rigor when receiving feedback, not blind implementation |
| **requesting-code-review** | Dispatch code reviewer subagent to verify work meets requirements |

### Planning & Execution
| Skill | Description |
|-------|-------------|
| **brainstorming** | Refine rough ideas into designs through collaborative questioning |
| **writing-plans** | Create detailed implementation plans with exact file paths and code examples |
| **executing-plans** | Load plans, review critically, execute in batches with review checkpoints |
| **subagent-driven-development** | Dispatch fresh subagent for each task with code review between tasks |
| **dispatching-parallel-agents** | Investigate 3+ independent failures concurrently with multiple agents |

### Git & Version Control
| Skill | Description |
|-------|-------------|
| **using-git-worktrees** | Create isolated git worktrees for feature work |
| **finishing-a-development-branch** | Guide completion with options for merge, PR, or cleanup |
| **sharing-skills** | Contribute skills upstream via pull request |

### Skills Development
| Skill | Description |
|-------|-------------|
| **writing-skills** | Apply TDD to skill documentation - test before writing |
| **testing-skills-with-subagents** | Verify skills work under pressure using RED-GREEN-REFACTOR cycle |
| **using-superpowers** | Establish mandatory workflows for finding and using skills |

## Skills with Additional Resources

| Skill | scripts/ | references/ | assets/ |
|-------|----------|-------------|---------|
| condition-based-waiting | `example.ts` | - | - |
| requesting-code-review | - | `code-reviewer.md` | - |
| root-cause-tracing | `find-polluter.sh` | - | - |
| systematic-debugging | - | 5 test scenario files | - |
| testing-skills-with-subagents | - | `CLAUDE_MD_TESTING.md` | - |
| writing-skills | - | `anthropic-best-practices.md`, `persuasion-principles.md` | `graphviz-conventions.dot` |

## Zip Files (Ready to Upload)

Pre-packaged zip files are available in the `../superpowers-skills-zips/` directory. These are ready to upload directly to Claude's Skills section.

**Important**: Skills must be uploaded as zip files. If downloading individual skill folders from this repo, zip them first before uploading.

## Source

These skills are from the Superpowers plugin for Claude Code, reorganized for Claude web app compatibility.
