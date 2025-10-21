# Claude Code Skills Repository

> **日本語版**: [README.ja.md](README.ja.md) をご覧ください

A curated collection of reusable skills for [Claude Code](https://claude.com/claude-code), extending its capabilities with specialized expertise and workflows.

## What Are Claude Code Skills?

Skills are modular capabilities that extend Claude Code's functionality. Each skill packages domain expertise into a discoverable capability that Claude can autonomously invoke when relevant to your request.

**Key characteristics:**
- **Model-invoked**: Claude automatically decides when to use skills based on context
- **Modular**: Each skill focuses on a specific capability or workflow
- **Shareable**: Easily distributed across teams through git or plugins
- **Configurable**: Tool restrictions ensure safe execution in sensitive contexts

## Repository Structure

```
skills/
├── README.md
├── LICENSE
└── [skill-name]/
    ├── SKILL.md          # Required: Skill definition and instructions
    ├── reference.md      # Optional: Reference documentation
    ├── examples.md       # Optional: Usage examples
    ├── scripts/          # Optional: Helper scripts
    └── templates/        # Optional: File templates
```

## Quick Start

### Prerequisites

- [Claude Code](https://claude.com/claude-code) installed
- Basic understanding of YAML and Markdown

### Installing Skills

#### For Personal Use

Clone skills to your personal skills directory:

```bash
# Clone individual skills
git clone https://github.com/y-nishizaki/skills.git
cd skills
cp -r [skill-name] ~/.claude/skills/
```

#### For Team/Project Use

Add skills directly to your project:

```bash
# In your project directory
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/y-nishizaki/skills.git
# Copy desired skills to .claude/skills/
cp -r skills/[skill-name] .
```

Commit the `.claude/skills/` directory to your repository. Team members will automatically have access after pulling changes.

## Creating Your Own Skills

### Basic Skill Structure

Every skill requires a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: Your Skill Name
description: Brief description with trigger terms that help Claude know when to use this skill
---

# Your Skill Name

## Purpose
Explain what this skill does and when it should be used.

## Instructions
Step-by-step instructions for Claude to follow.

## Examples
Concrete usage scenarios.
```

### Best Practices

**1. Write Specific Descriptions**
- Include trigger terms users might mention
- Be explicit about when the skill should activate
- Avoid vague or overly broad descriptions

**2. Keep Skills Focused**
- One skill = one capability
- Split complex workflows into multiple complementary skills

**3. Use Tool Restrictions When Appropriate**
```yaml
---
name: Code Reviewer
description: Reviews code for best practices and potential issues
allowed-tools: Read, Grep, Glob
---
```

**4. Provide Clear Examples**
- Show realistic usage scenarios
- Include both input and expected behavior
- Document edge cases

**5. Use Forward Slashes in Paths**
- Ensures cross-platform compatibility
- Always use `/` even on Windows

**6. Progressive Documentation**
- Start with essential info in SKILL.md
- Move detailed reference to separate files
- Claude loads additional context as needed

### Testing Your Skills

1. **Local testing**: Place skill in `~/.claude/skills/` and test with Claude Code
2. **Description validation**: Verify Claude activates the skill with natural requests
3. **Team validation**: Have colleagues test before committing to project
4. **YAML validation**: Check syntax with a YAML linter

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-skill`
3. **Follow the skill structure** outlined above
4. **Test thoroughly** with Claude Code
5. **Document clearly** in SKILL.md
6. **Submit a pull request** with:
   - Clear description of the skill's purpose
   - Example use cases
   - Any dependencies or requirements

### Contribution Checklist

- [ ] SKILL.md includes complete frontmatter (name, description)
- [ ] Description contains specific trigger terms
- [ ] Instructions are clear and actionable
- [ ] Examples demonstrate realistic usage
- [ ] Forward slashes used in all file paths
- [ ] Tested locally with Claude Code
- [ ] No sensitive information in files
- [ ] License compatible (MIT)

## Available Skills

### Skill Creator

**Location**: `skill-creator/`

A meta-skill that helps you create new Claude Code skills following best practices and proper structure.

**Features**:
- Generates complete skill directory structure
- Creates SKILL.md with proper YAML frontmatter
- Includes validation and best practices guidance
- Provides basic and advanced templates
- Comprehensive reference documentation

**Usage**: Ask Claude to "create a new skill" or "build a skill for [purpose]"

**Installation**:
```bash
cp -r skill-creator ~/.claude/skills/
```

**Files**:
- `SKILL.md` - Main skill definition and creation process
- `reference.md` - Detailed technical reference and specifications
- `templates/basic-skill-template.md` - Simple skill template
- `templates/advanced-skill-template.md` - Complex skill template

## Debugging Common Issues

### Claude doesn't use my skill
- **Check description specificity**: Add clearer trigger terms
- **Verify file location**: Ensure skill is in `~/.claude/skills/` or `.claude/skills/`
- **Test activation**: Try explicit requests matching your trigger terms

### YAML parsing errors
- Verify opening and closing `---` markers
- Check for tabs (use spaces only)
- Validate indentation
- Use a YAML linter

### Conflicts with other skills
- Use distinct trigger terms in descriptions
- Narrow the scope of when skills activate
- Consider combining overlapping skills

## Resources

- [Official Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills.md)
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [GitHub Issues](https://github.com/y-nishizaki/skills/issues) - Report bugs or request features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for [Claude Code](https://claude.com/claude-code) by Anthropic
- Inspired by the Claude Code community and best practices

---

**Note**: This is an unofficial community repository. For official Claude Code documentation and support, visit [docs.claude.com](https://docs.claude.com).
