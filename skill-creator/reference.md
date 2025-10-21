# Skill Creator Reference Documentation

## Table of Contents

1. [YAML Frontmatter Specification](#yaml-frontmatter-specification)
2. [File Structure Patterns](#file-structure-patterns)
3. [Description Writing Guide](#description-writing-guide)
4. [Instruction Writing Best Practices](#instruction-writing-best-practices)
5. [Tool Usage Guidelines](#tool-usage-guidelines)
6. [Testing and Validation](#testing-and-validation)
7. [Common Pitfalls](#common-pitfalls)
8. [Advanced Patterns](#advanced-patterns)

---

## YAML Frontmatter Specification

### Required Fields

#### name
- **Type**: String
- **Max Length**: 64 characters
- **Format**: Lowercase with hyphens (kebab-case)
- **Example**: `skill-creator`, `code-reviewer`, `api-tester`
- **Validation**: Must be unique, alphanumeric with hyphens only

#### description
- **Type**: String
- **Max Length**: 200 characters
- **Purpose**: Helps Claude decide when to activate the skill
- **Must Include**:
  - What the skill does
  - When to use it
  - Trigger keywords
- **Example**: "Create new Claude Code skills with proper structure and best practices. Use when building skills, generating capabilities, or creating custom tools."

### Optional Fields

#### version
- **Type**: String (Semantic Versioning)
- **Format**: `MAJOR.MINOR.PATCH`
- **Example**: `1.0.0`, `2.1.3`
- **Purpose**: Track skill iterations and changes

#### dependencies
- **Type**: String or Array
- **Format**: Package specifications
- **Example**:
  - Single: `python>=3.8`
  - Multiple: `python>=3.8, node>=18, docker`
- **Purpose**: Document required software/tools

### YAML Syntax Rules

1. **Delimiters**: Must start and end with `---` on separate lines
2. **Spacing**: Use spaces only, never tabs
3. **Indentation**: 2 spaces per level
4. **Quotes**: Use quotes for values containing special characters
5. **Lists**: Use `-` prefix with space for array items

### Valid YAML Example

```yaml
---
name: example-skill
description: This is an example skill that demonstrates proper YAML formatting and required fields.
version: 1.0.0
dependencies: python>=3.8
---
```

### Invalid YAML Examples

```yaml
# Missing closing delimiter
---
name: example-skill
description: Missing closing delimiter

# Using tabs (invisible here but causes errors)
---
name:→example-skill
description:→Bad formatting

# Name too long
---
name: this-is-an-extremely-long-skill-name-that-exceeds-sixty-four-characters-limit
description: This will fail validation
```

---

## File Structure Patterns

### Minimal Skill (Simple Task)

```
skill-name/
└── SKILL.md
```

**Use When**:
- Simple, straightforward functionality
- No external dependencies
- Minimal documentation needed
- Examples fit in main file

### Standard Skill (Most Common)

```
skill-name/
├── SKILL.md
├── reference.md
└── examples.md
```

**Use When**:
- Moderate complexity
- Needs extended examples
- Technical specifications beneficial
- API or format references needed

### Complex Skill (Advanced Workflows)

```
skill-name/
├── SKILL.md
├── reference.md
├── examples.md
├── templates/
│   ├── template1.md
│   └── template2.json
└── scripts/
    ├── helper.py
    └── validator.sh
```

**Use When**:
- Complex multi-step processes
- Generates files from templates
- Requires helper scripts
- Multiple configuration options
- Domain-specific knowledge

### Template-Focused Skill

```
skill-name/
├── SKILL.md
└── templates/
    ├── basic.md
    ├── advanced.md
    └── config.yaml
```

**Use When**:
- Primary function is generating files
- Multiple template variations
- Scaffolding or boilerplate generation
- Project initialization

---

## Description Writing Guide

### Purpose of Description

The description field serves two critical functions:
1. Helps Claude determine when to activate the skill
2. Provides context about the skill's capabilities

### Description Formula

```
[What it does] + [When to use] + [Trigger keywords]
```

### Good Description Examples

```yaml
description: "Review code for bugs, performance issues, and best practices. Use when reviewing code, checking quality, or analyzing patterns. Keywords: code review, check code, review PR."
```

**Why it's good**:
- Clear functionality
- Specific use cases
- Explicit trigger keywords
- Under 200 characters

```yaml
description: "Generate API documentation from code comments and type definitions. Use when documenting APIs, creating references, or updating docs. Keywords: API docs, documentation, generate docs."
```

**Why it's good**:
- Precise action
- Context for activation
- User-language keywords

### Bad Description Examples

```yaml
description: "A skill for code"
```

**Problems**:
- Too vague
- No trigger keywords
- Unclear when to use
- Minimal context

```yaml
description: "This incredibly comprehensive skill handles all aspects of code review including syntax checking, semantic analysis, performance optimization suggestions, security vulnerability detection, and best practices enforcement."
```

**Problems**:
- Too long
- Overly complex
- Tries to do too much
- Should be split into multiple skills

### Trigger Keyword Strategy

**Include These Types**:
1. **Action verbs**: create, build, generate, review, analyze, test
2. **Domain terms**: API, database, frontend, backend, DevOps
3. **User phrases**: "help me...", "create a...", "review my..."
4. **Abbreviations**: PR, CI/CD, API, DB

**Example Keyword Lists**:
```yaml
# Code Review Skill
Keywords: review, check, analyze, PR, pull request, code quality

# Database Migration Skill
Keywords: migrate, migration, database, schema, DB

# Component Generator Skill
Keywords: component, generate, create, scaffold, boilerplate
```

---

## Instruction Writing Best Practices

### Structure Your Instructions

Use a hierarchical structure:

```markdown
## Instructions

### Phase 1: Preparation
#### Step 1.1: Analyze Request
- Substep details
- What to check
- How to validate

#### Step 1.2: Gather Resources
- What resources
- Where to find them
- How to verify

### Phase 2: Execution
[Continue pattern...]
```

### Be Specific and Actionable

**Bad**:
```markdown
## Instructions
Review the code and provide feedback.
```

**Good**:
```markdown
## Instructions

### Step 1: Code Analysis
1. Read the entire file using the Read tool
2. Identify the primary language and framework
3. Check for:
   - Syntax errors
   - Unused variables
   - Potential null pointer exceptions
   - Performance anti-patterns

### Step 2: Generate Feedback
1. Create a structured report with:
   - Critical issues (must fix)
   - Warnings (should fix)
   - Suggestions (nice to have)
2. For each issue, provide:
   - Line number
   - Issue description
   - Suggested fix
   - Code example
```

### Use Conditional Logic

```markdown
### Step 3: Language-Specific Checks

**If Python**:
- Check PEP 8 compliance
- Verify type hints
- Check for common pitfalls (mutable defaults, etc.)

**If JavaScript/TypeScript**:
- Check ESLint rules
- Verify async/await usage
- Check for promise handling

**If Go**:
- Check gofmt compliance
- Verify error handling
- Check for goroutine leaks
```

### Include Edge Cases

```markdown
### Error Handling

**If file is empty**:
- Alert user
- Ask if they want to create template content
- Provide options

**If file is too large** (>10,000 lines):
- Ask user to specify sections to review
- Offer to review in chunks
- Suggest automated tools

**If language is not recognized**:
- Ask user to specify language
- Attempt generic review
- Focus on structural patterns
```

---

## Tool Usage Guidelines

### Preferred Tools by Task

| Task | Preferred Tool | Avoid |
|------|---------------|-------|
| Read files | `Read` | `cat`, `head`, `tail` |
| Search content | `Grep` | `grep`, `rg` |
| Find files | `Glob` | `find`, `ls` |
| Edit files | `Edit` | `sed`, `awk` |
| Create files | `Write` | `echo >`, `cat > EOF` |
| Run commands | `Bash` | (appropriate use) |
| Web requests | `WebFetch` | `curl`, `wget` |

### Tool Usage in Skills

**Specify tools explicitly**:
```markdown
## Instructions

### Step 1: Find Configuration Files
Use the **Glob** tool to search for config files:
- Pattern: `**/*.config.js`
- Look in project root
- Check for common locations

### Step 2: Read Configuration
Use the **Read** tool to examine each config:
- Read entire file
- Parse JSON/YAML structure
- Extract relevant settings
```

**Explain why to use specific tools**:
```markdown
### Tool Selection

Use **Grep** instead of manual file reading when:
- Searching across many files
- Pattern matching needed
- Only need to find occurrences

Use **Read** instead of Grep when:
- Need full context
- Analyzing structure
- Understanding relationships
```

---

## Testing and Validation

### Pre-Creation Validation Checklist

Before creating a skill, verify:

- [ ] Skill name is unique and descriptive
- [ ] Name follows kebab-case convention
- [ ] Name is under 64 characters
- [ ] Description is clear and specific
- [ ] Description includes trigger keywords
- [ ] Description is under 200 characters
- [ ] Skill has single, focused purpose
- [ ] Instructions are actionable
- [ ] Examples are realistic
- [ ] All paths use forward slashes
- [ ] YAML syntax is valid
- [ ] No tabs in YAML (spaces only)

### Post-Creation Testing

**1. YAML Validation**
```bash
# Use a YAML linter
yamllint SKILL.md

# Or Python
python -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"
```

**2. Installation Test**
```bash
# Copy to personal skills directory
cp -r skill-name ~/.claude/skills/

# Verify file structure
ls -la ~/.claude/skills/skill-name/
```

**3. Activation Test**

Try requests that should trigger the skill:
- Use exact trigger keywords
- Use natural language variations
- Test edge cases

**4. Functionality Test**

Verify the skill:
- Produces expected output
- Handles errors gracefully
- Works with various inputs
- Completes successfully

### Validation Script Template

```bash
#!/bin/bash
# validate-skill.sh

SKILL_DIR=$1

echo "Validating skill: $SKILL_DIR"

# Check required files
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "ERROR: SKILL.md not found"
    exit 1
fi

# Check YAML syntax
python3 -c "
import yaml
import sys

with open('$SKILL_DIR/SKILL.md') as f:
    content = f.read()
    parts = content.split('---')
    if len(parts) < 3:
        print('ERROR: Invalid YAML frontmatter format')
        sys.exit(1)
    try:
        yaml.safe_load(parts[1])
        print('✓ YAML syntax valid')
    except Exception as e:
        print(f'ERROR: YAML parsing failed: {e}')
        sys.exit(1)
"

# Check required fields
python3 -c "
import yaml

with open('$SKILL_DIR/SKILL.md') as f:
    content = f.read()
    frontmatter = yaml.safe_load(content.split('---')[1])

    if 'name' not in frontmatter:
        print('ERROR: Missing required field: name')
        exit(1)

    if 'description' not in frontmatter:
        print('ERROR: Missing required field: description')
        exit(1)

    if len(frontmatter['name']) > 64:
        print('ERROR: Name exceeds 64 characters')
        exit(1)

    if len(frontmatter['description']) > 200:
        print('ERROR: Description exceeds 200 characters')
        exit(1)

    print('✓ Required fields present and valid')
"

echo "✓ Validation complete"
```

---

## Common Pitfalls

### 1. Overly Broad Skills

**Problem**: Skill tries to do too many things

**Example**:
```yaml
name: web-development
description: Handle all web development tasks including frontend, backend, database, DevOps, testing, and deployment
```

**Solution**: Split into focused skills
```yaml
# Better approach
name: frontend-component-generator
description: Generate React/Vue components with tests. Use when creating UI components.

name: api-endpoint-creator
description: Create REST API endpoints with validation. Use when building APIs.
```

### 2. Vague Descriptions

**Problem**: Description doesn't help Claude know when to activate

**Example**:
```yaml
description: A helpful skill for developers
```

**Solution**: Be specific
```yaml
description: Review Pull Requests for code quality, best practices, and potential bugs. Use for PR review, code review, or quality checks. Keywords: review PR, check code.
```

### 3. Incorrect YAML Formatting

**Problem**: Tabs instead of spaces, missing delimiters

**Example**:
```yaml
---
name:	skill-name
	description: Bad formatting
```

**Solution**: Use spaces, proper structure
```yaml
---
name: skill-name
description: Good formatting with spaces
---
```

### 4. Platform-Specific Paths

**Problem**: Using backslashes or platform-specific paths

**Example**:
```markdown
Check files in: C:\Users\Project\src\
```

**Solution**: Use forward slashes
```markdown
Check files in: /project/src/
Use relative paths: ./src/
```

### 5. Unclear Instructions

**Problem**: Instructions are too high-level

**Example**:
```markdown
## Instructions
Analyze the code and make it better.
```

**Solution**: Provide specific steps
```markdown
## Instructions

### Step 1: Analyze Code Structure
1. Read the file using Read tool
2. Identify language and framework
3. Map out function/class structure
4. Note dependencies

### Step 2: Check for Issues
1. Syntax errors
2. Unused variables
3. Potential bugs
4. Performance issues

### Step 3: Generate Report
1. List issues by severity
2. Provide line numbers
3. Suggest specific fixes
4. Include code examples
```

### 6. Missing Examples

**Problem**: No concrete usage examples

**Solution**: Always include realistic examples
```markdown
## Examples

### Example 1: Basic Code Review

**User Request**: "Please review this Python file"

**Expected Process**:
1. Read the file
2. Check for PEP 8 compliance
3. Look for common Python pitfalls
4. Generate structured feedback

**Expected Output**:
```
Code Review for file.py:

CRITICAL:
- Line 23: Potential division by zero
- Line 45: SQL injection vulnerability

WARNINGS:
- Line 12: Unused import 'sys'
- Line 34: Variable name doesn't follow PEP 8

SUGGESTIONS:
- Consider using type hints
- Add docstrings to functions
```
```

---

## Advanced Patterns

### Multi-Stage Skills

For complex workflows with distinct phases:

```markdown
## Instructions

### Stage 1: Discovery
[Discovery steps]

**Checkpoint**: Before proceeding, verify:
- [ ] All files found
- [ ] Dependencies identified
- [ ] Configuration valid

### Stage 2: Analysis
[Analysis steps]

**Checkpoint**: Validate analysis:
- [ ] Data structured correctly
- [ ] Edge cases identified
- [ ] Requirements clear

### Stage 3: Execution
[Execution steps]

**Final Validation**:
- [ ] Output meets requirements
- [ ] No errors occurred
- [ ] User confirmation received
```

### Conditional Skills

Skills that branch based on context:

```markdown
## Instructions

### Step 1: Detect Context

**If in Git repository**:
- Check git status
- Identify current branch
- Follow git-aware workflow

**If not in Git repository**:
- Use file system operations
- Follow standalone workflow

### Step 2: Process Based on Language

Use Grep to detect language, then:

**For compiled languages** (Java, C++, Rust):
1. Check for build files
2. Run compilation checks
3. Execute type checking

**For interpreted languages** (Python, JavaScript):
1. Check for syntax validity
2. Run linters
3. Execute tests

**For markup languages** (HTML, Markdown):
1. Validate structure
2. Check links
3. Verify formatting
```

### Iterative Skills

Skills that work in loops:

```markdown
## Instructions

### Iterative Processing

For each file in the target directory:

1. **Read** the file
2. **Analyze** according to criteria
3. **Collect** results
4. **Continue** to next file

After all files processed:

1. **Aggregate** results
2. **Sort** by priority
3. **Generate** summary report
4. **Present** to user

### Loop Controls

- Maximum iterations: 100 files
- Skip if: file size > 1MB
- Break if: critical error found
- Continue if: file type unsupported
```

### Meta-Skills

Skills that work with other skills:

```markdown
## Instructions

### Skill Coordination

This meta-skill coordinates multiple specialized skills:

1. **Identify** which skills are needed
2. **Sequence** skill execution order
3. **Pass** context between skills
4. **Aggregate** results
5. **Present** unified output

### Example Workflow

For "Analyze and improve codebase":

1. Activate `code-analyzer` skill
2. Collect analysis results
3. Activate `code-improver` skill with analysis
4. Verify improvements with `code-tester` skill
5. Generate final report

### Inter-Skill Communication

- Use consistent data formats
- Document expected inputs/outputs
- Handle skill failures gracefully
- Provide rollback if needed
```

---

## Skill Naming Conventions

### Recommended Patterns

| Pattern | Example | Use Case |
|---------|---------|----------|
| `[action]-[target]` | `review-code`, `test-api` | Action-focused skills |
| `[domain]-[role]` | `frontend-developer`, `devops-engineer` | Role-based skills |
| `[tool]-[integration]` | `docker-compose`, `git-workflow` | Tool-specific skills |
| `[format]-[converter]` | `json-to-yaml`, `markdown-to-pdf` | Conversion skills |

### Names to Avoid

- Too generic: `helper`, `utils`, `tools`
- Too long: `comprehensive-full-stack-development-assistant`
- With numbers: `skill-v2`, `helper-2024`
- With special chars: `skill_name`, `skill.helper`

---

## Version Management

### Semantic Versioning Guidelines

**MAJOR version** (1.0.0 → 2.0.0):
- Breaking changes to instruction flow
- Incompatible changes to expected inputs/outputs
- Removal of features

**MINOR version** (1.0.0 → 1.1.0):
- New features added
- New optional steps
- Enhanced functionality

**PATCH version** (1.0.0 → 1.0.1):
- Bug fixes
- Documentation updates
- Small improvements

### Changelog Format

```markdown
## Versioning

### Version 1.2.1 (2025-10-21)
- Fixed: YAML parsing error on multi-line descriptions
- Updated: Examples with latest API patterns
- Improved: Error messages for missing dependencies

### Version 1.2.0 (2025-10-15)
- Added: Support for TypeScript projects
- Added: Integration with ESLint
- Enhanced: Performance for large codebases

### Version 1.1.0 (2025-10-01)
- Added: Python type hint checking
- Improved: Error reporting format

### Version 1.0.0 (2025-09-15)
- Initial release
- Core code review functionality
```

---

This reference documentation provides comprehensive technical details for creating robust, well-structured Claude Code skills. Refer to SKILL.md for the step-by-step creation process and templates for ready-to-use starting points.
