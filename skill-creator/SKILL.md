---
name: skill-creator
description: Create new Claude Code skills. Use this when the user wants to create a new skill, build a custom skill, generate a skill, or asks about skill creation. Keywords - skill creation, new skill, create skill, build skill, generate skill.
version: 1.0.0
---

# Skill Creator

## Purpose

This skill helps users create new Claude Code skills by generating the proper directory structure, SKILL.md file with YAML frontmatter, and supporting documentation files following best practices.

## When to Use This Skill

Use this skill when:
- User requests to create a new skill
- User asks "create a skill for..."
- User mentions "skill creation" or "build a skill"
- User wants to generate a custom Claude Code capability

## Skill Creation Process

### Step 1: Gather Requirements

Ask the user for the following information if not already provided:

1. **Skill Name**:
   - Use lowercase with hyphens (e.g., "code-reviewer", "api-tester")
   - Must be descriptive and unique
   - Maximum 64 characters

2. **Skill Description**:
   - Explain what the skill does
   - Include trigger keywords that users might mention
   - Specify when Claude should activate this skill
   - Maximum 200 characters
   - Example: "Review code for best practices and potential issues. Use when reviewing code, checking code quality, or analyzing code patterns."

3. **Skill Purpose**:
   - Detailed explanation of the skill's functionality
   - What problems does it solve?
   - What are the expected outcomes?

4. **Instructions**:
   - Step-by-step process Claude should follow
   - Specific tools or approaches to use
   - Edge cases to handle

5. **Examples** (optional but recommended):
   - Real-world usage scenarios
   - Input/output examples
   - Common use cases

6. **Dependencies** (optional):
   - Required software packages (e.g., "python>=3.8", "node>=18")
   - External tools needed

### Step 2: Create Directory Structure

Create the skill directory with this structure:

```
[skill-name]/
├── SKILL.md          # Required: Main skill definition
├── reference.md      # Optional: Detailed reference documentation
├── examples.md       # Optional: Extended examples
├── templates/        # Optional: Template files
└── scripts/          # Optional: Helper scripts
```

### Step 3: Generate SKILL.md

Create the SKILL.md file with the following structure:

```yaml
---
name: [skill-name]
description: [Brief description with trigger keywords]
version: 1.0.0
dependencies: [Optional: list dependencies]
---

# [Skill Name]

## Purpose
[Detailed explanation of what this skill does and when to use it]

## Instructions

### [Step 1 Title]
[Detailed instructions for this step]

### [Step 2 Title]
[Detailed instructions for this step]

[Continue with additional steps as needed]

## Examples

### Example 1: [Scenario Name]
**User Request**: "[Example user input]"

**Expected Behavior**:
[What Claude should do]

### Example 2: [Another Scenario]
[Additional examples]

## Best Practices
- [Best practice 1]
- [Best practice 2]
[etc.]

## Error Handling
- [How to handle common errors]
- [Edge cases to consider]
```

### Step 4: Create Supporting Files (if needed)

**reference.md**: For detailed technical specifications, API references, or extensive documentation that doesn't belong in the main SKILL.md.

**examples.md**: For extended examples, tutorials, or demonstration scenarios.

**templates/**: For file templates the skill might use to generate code or documentation.

**scripts/**: For helper scripts that support the skill's functionality.

### Step 5: Validate the Skill

Before finalizing, check:

1. **YAML Frontmatter Validation**:
   - Verify opening and closing `---` markers
   - Check for proper indentation (spaces only, no tabs)
   - Ensure required fields (name, description) are present
   - Validate field values are within limits

2. **Description Quality**:
   - Contains specific trigger keywords
   - Clearly explains when to use the skill
   - Under 200 characters

3. **Instruction Clarity**:
   - Steps are clear and actionable
   - Includes concrete examples
   - Covers edge cases

4. **Path Formatting**:
   - All file paths use forward slashes (/)
   - No platform-specific paths

### Step 6: Output Location

By default, create the skill in the current directory. If the user wants to install it:

- **Personal use**: `~/.claude/skills/[skill-name]/`
- **Project use**: `./.claude/skills/[skill-name]/`

Ask the user where they want to create the skill if unclear.

## Tool Restrictions

When creating skills, prefer using:
- **Write** for creating new files
- **Bash** only for directory creation (mkdir)
- **Read** to verify created files

## Important Notes

1. **Keep Skills Focused**: One skill should do one thing well. Complex workflows should be split into multiple complementary skills.

2. **Progressive Documentation**: Start with essential information in SKILL.md. Move detailed reference material to separate files.

3. **Test Recommendations**: Suggest the user test the skill by:
   - Placing it in `~/.claude/skills/`
   - Making requests that match the trigger keywords
   - Verifying Claude activates the skill appropriately

4. **Avoid Conflicts**: Check if the skill name might conflict with existing skills or be too similar to built-in capabilities.

## Common Patterns

### Simple Skill
For straightforward tasks, just SKILL.md is sufficient.

### Complex Skill
For complex workflows, include:
- SKILL.md (core instructions)
- reference.md (technical details)
- examples.md (extended examples)

### Template-Based Skill
For skills that generate files:
- SKILL.md (instructions)
- templates/ directory (file templates)

## Error Handling

If the user's requirements are unclear:
1. Ask specific questions to clarify
2. Provide examples of similar skills
3. Suggest simplifications if the skill seems too broad

If the skill name already exists:
1. Alert the user
2. Suggest an alternative name
3. Ask if they want to overwrite

## Output Format

After creating the skill, provide:
1. Summary of what was created
2. File locations
3. Next steps for testing
4. Installation instructions

Example output:
```
Created skill: code-reviewer
Location: ./code-reviewer/

Files created:
- SKILL.md (main definition)
- reference.md (coding standards reference)
- examples.md (review examples)

Next steps:
1. Review the generated files
2. Test the skill: cp -r code-reviewer ~/.claude/skills/
3. Try it: "Please review this code file"
```
