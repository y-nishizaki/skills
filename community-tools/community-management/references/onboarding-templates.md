# Onboarding Templates for Open Source Contributors

This reference provides templates and checklists for effectively onboarding new contributors to open source projects.

## New Contributor Welcome Message Template

```markdown
Welcome to [PROJECT NAME]! 🎉

Thank you for your interest in contributing. We're excited to have you here!

### Getting Started

1. **Read our documentation**:
   - [Code of Conduct](link) - Our community standards
   - [Contributing Guide](link) - How to contribute
   - [Development Setup](link) - Get your environment ready

2. **Join the community**:
   - [Chat/Slack/Discord](link) - Ask questions and connect
   - [Forum/Mailing List](link) - Longer discussions
   - [Community Meetings](link) - Weekly/monthly calls

3. **Find your first contribution**:
   - Browse [good first issues](link)
   - Check [help wanted](link) labels
   - Improve [documentation](link)

### Need Help?

Don't hesitate to ask! You can:
- Ask in [#newcomers channel](link)
- Tag @mentors in discussions
- Attend [new contributor office hours](link)

We're here to help you succeed!

---
*This message was automated. Reply with questions and a maintainer will assist.*
```

## CONTRIBUTING.md Template

```markdown
# Contributing to [PROJECT NAME]

Thank you for considering contributing! This document guides you through the contribution process.

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports:
- **Check the issue tracker** - Someone may have already reported it
- **Verify the bug** - Can you reproduce it consistently?
- **Check documentation** - Is this intended behavior?

**Good bug reports include**:
- **Clear title** - Summarize the problem
- **Steps to reproduce** - Detailed reproduction steps
- **Expected vs. actual behavior** - What should happen vs. what does happen
- **Environment** - OS, version, configuration
- **Screenshots/logs** - Visual aids if applicable

Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Features

Feature suggestions are welcome! Include:
- **Use case** - What problem does this solve?
- **Proposed solution** - How should it work?
- **Alternatives** - Other approaches considered
- **Impact** - Who benefits from this feature?

Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Contributing Code

#### Before You Start

1. **Check existing issues** - Avoid duplicate work
2. **Discuss significant changes** - Open an issue first for major features
3. **Review the roadmap** - Ensure alignment with project direction

#### Development Workflow

1. **Fork the repository** and clone your fork
2. **Create a branch** - Use descriptive names: `fix/issue-123` or `feature/new-capability`
3. **Set up development environment** - See [DEVELOPMENT.md](DEVELOPMENT.md)
4. **Make your changes**:
   - Follow [style guide](#style-guide)
   - Write/update tests
   - Update documentation
5. **Test thoroughly** - Run full test suite
6. **Commit your changes** - Use [clear commit messages](#commit-messages)
7. **Push to your fork**
8. **Open a Pull Request** - Use our [PR template](.github/PULL_REQUEST_TEMPLATE.md)

#### Style Guide

- **Code formatting**: Run `[formatter command]` before committing
- **Linting**: Pass all linter checks (`[linter command]`)
- **Naming conventions**: [Describe conventions]
- **Comments**: Explain *why*, not *what*
- **Documentation**: Update relevant docs with code changes

#### Commit Messages

Follow this format:

```
type(scope): brief description

Detailed explanation of the change and its motivation.

Fixes #123
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(api): add user authentication endpoint

Implements JWT-based authentication for API access.
Includes token refresh mechanism.

Closes #456
```

#### Testing

- Write tests for new features
- Update tests for changed behavior
- Ensure all tests pass: `[test command]`
- Aim for [coverage target]% code coverage

#### Pull Request Process

1. **Update documentation** - README, API docs, etc.
2. **Pass CI checks** - All automated tests must pass
3. **Request review** - Tag relevant maintainers
4. **Address feedback** - Respond to review comments
5. **Squash commits** (if requested) - Clean up history before merge
6. **Celebrate!** - Your contribution is merged 🎉

**Pull Request Guidelines**:
- One feature/fix per PR
- Keep changes focused and minimal
- Provide context in PR description
- Link related issues
- Update CHANGELOG.md (if applicable)

### Contributing Documentation

Documentation improvements are highly valued!

- Fix typos and clarify wording
- Add examples and tutorials
- Improve API documentation
- Translate documentation
- Create diagrams and visualizations

Documentation follows the same PR process as code.

### Other Ways to Contribute

- **Triage issues** - Help categorize and prioritize
- **Review pull requests** - Provide constructive feedback
- **Answer questions** - Help others in chat/forums
- **Write blog posts** - Share your experience
- **Give talks** - Present at meetups/conferences
- **Improve tooling** - CI, build systems, dev tools

## Recognition

Contributors are recognized through:
- [CONTRIBUTORS.md](CONTRIBUTORS.md) listing
- Release notes acknowledgments
- Annual contributor highlights
- Swag for significant contributions (if applicable)
- Speaking opportunities at project events

## Getting Help

Stuck? Reach out:
- **Chat**: [Link to chat] - Fastest for quick questions
- **Forum**: [Link] - For longer discussions
- **Office Hours**: [Schedule] - Live help from maintainers
- **Mentorship**: Tag @mentors for guidance

## License

By contributing, you agree that your contributions will be licensed under the [PROJECT LICENSE].
```

## New Contributor Onboarding Checklist

### For Project Maintainers

When a new contributor appears:

- [ ] Welcome them warmly (use template above)
- [ ] Point to contributing guide and code of conduct
- [ ] Suggest appropriate first issues based on their background
- [ ] Introduce them to mentors or relevant team members
- [ ] Add them to newcomer chat channel
- [ ] Invite to next community meeting
- [ ] Follow up after one week to check progress
- [ ] Celebrate their first merged contribution publicly

### For New Contributors

- [ ] Read Code of Conduct
- [ ] Review Contributing Guide
- [ ] Set up development environment
- [ ] Join community chat
- [ ] Introduce yourself in newcomer channel
- [ ] Attend community meeting (if available)
- [ ] Pick a good first issue
- [ ] Ask questions when stuck
- [ ] Submit first pull request
- [ ] Respond to code review feedback
- [ ] Celebrate merged contribution!

## Mentorship Program Template

### Program Structure

**Duration**: 3-6 months

**Commitment**:
- **Mentor**: 2-4 hours per month
- **Mentee**: 4-8 hours per month on project contributions

**Pairing**:
- Match based on interests and availability
- Consider timezone compatibility
- Prefer complementary skill sets

### Mentor Responsibilities

- Schedule regular check-ins (bi-weekly recommended)
- Help mentee select appropriate issues/features
- Review code and provide detailed, constructive feedback
- Introduce mentee to community members
- Share project context and tribal knowledge
- Advocate for mentee's contributions
- Help navigate project processes

### Mentee Expectations

- Commit to regular contributions
- Communicate proactively with mentor
- Ask questions and seek feedback
- Attend community meetings when possible
- Document learning and share with community
- Help future newcomers once proficient

### Success Metrics

Track mentee progress:
- [ ] Completed development environment setup
- [ ] First issue/PR merged
- [ ] Three contributions merged
- [ ] Attended community meeting
- [ ] Helped another newcomer
- [ ] Considered for committer/maintainer role

### Monthly Check-in Template

```markdown
# Mentorship Check-in - [Month Year]

**Mentor**: [Name]
**Mentee**: [Name]

## Progress This Month
- Contributions: [List PRs/issues]
- Skills developed: [List]
- Challenges encountered: [List]

## Goals for Next Month
- [ ] [Specific goal 1]
- [ ] [Specific goal 2]
- [ ] [Specific goal 3]

## Questions/Discussion Topics
- [Topic 1]
- [Topic 2]

## Action Items
- [ ] Mentor: [Action]
- [ ] Mentee: [Action]
```

## Good First Issue Template

Label issues appropriately for newcomers:

```markdown
**Description**
[Clear description of what needs to be done]

**Context**
[Why is this needed? How does it fit into the project?]

**Proposed Solution**
[Suggestion for how to approach this, if applicable]

**Acceptance Criteria**
- [ ] [Specific requirement 1]
- [ ] [Specific requirement 2]
- [ ] Tests added/updated
- [ ] Documentation updated

**Getting Started**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Resources**
- Relevant code: [Link to file/function]
- Related issues: #123, #456
- Documentation: [Link]

**Estimated Difficulty**: [Easy/Medium]
**Estimated Time**: [Hours/Days]

**Mentorship Available**: Yes - tag @mentor-name with questions

---
*This is marked as a good first issue. New contributors are encouraged to take this on!*
```

## First PR Congratulations Template

```markdown
🎉 Congratulations on your first merged contribution to [PROJECT NAME], @username!

This is an exciting milestone. Thank you for:
- [Specific positive aspect of their contribution]
- [Another positive aspect]

### What's Next?

Now that you're a contributor:
- ⭐ Star the repo if you haven't already
- 📢 Share your contribution on social media (tag us!)
- 🔍 Find your next contribution: [Link to issues]
- 👥 Join us at the next community meeting: [Link]
- 📝 Add yourself to CONTRIBUTORS.md: [Link]

We're excited to see your continued involvement!

---
*Want to help more newcomers? Join our mentorship program: [Link]*
```

## Development Environment Setup Guide Template

```markdown
# Development Environment Setup

This guide helps you set up [PROJECT NAME] for local development.

## Prerequisites

Install these before starting:
- [Tool 1] - version X.Y or higher - [Installation link]
- [Tool 2] - version X.Y or higher - [Installation link]
- [Tool 3] - version X.Y or higher - [Installation link]

**Verify installation**:
```bash
[tool1] --version
[tool2] --version
```

## Clone the Repository

```bash
git clone https://github.com/[org]/[project].git
cd [project]
```

## Set Up Development Environment

### Option 1: Using [Tool/Script]

```bash
./scripts/setup-dev-env.sh
```

This script will:
- Install dependencies
- Set up configuration
- Initialize database (if applicable)
- Run initial tests

### Option 2: Manual Setup

1. **Install dependencies**:
   ```bash
   [package manager command]
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Initialize database** (if applicable):
   ```bash
   [database setup commands]
   ```

4. **Verify setup**:
   ```bash
   [test command]
   ```

## Running the Project

**Development mode**:
```bash
[dev command]
```

Access at: http://localhost:[port]

**Run tests**:
```bash
[test command]
```

**Run linter**:
```bash
[lint command]
```

**Format code**:
```bash
[format command]
```

## Common Issues

### Issue 1: [Common problem]
**Error**: [Error message]
**Solution**: [How to fix]

### Issue 2: [Common problem]
**Error**: [Error message]
**Solution**: [How to fix]

## Next Steps

- Read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Browse [good first issues](link)
- Join [community chat](link)

## Getting Help

If you encounter issues:
1. Check [troubleshooting docs](link)
2. Search [existing issues](link)
3. Ask in [chat channel](link)
4. Open a new issue with full details
```

## Contribution Recognition System

### Levels of Recognition

**1. First Contribution**
- Public thanks in PR
- Add to CONTRIBUTORS.md
- Welcome badge in chat (if applicable)

**2. Regular Contributor (3+ merged PRs)**
- Mention in release notes
- Invitation to contributors-only channels
- "Contributor" badge

**3. Sustained Contribution (6+ months active)**
- Featured in blog post/newsletter
- Invitation to contributor calls
- Project swag (if available)
- Potential committer nomination

**4. Committer/Maintainer**
- Listed in MAINTAINERS.md
- Write access to repository
- Voice in governance decisions
- Speaking opportunities

### Recognition Ceremonies

**Monthly Recognition**:
- Highlight top contributors in newsletter
- Social media shoutouts
- Community meeting acknowledgments

**Annual Recognition**:
- Year-end contributor report
- Special thanks in major releases
- Contributor awards (if applicable)

## Resources

- Mozilla's Contribution Ladder: https://wiki.mozilla.org/Commit_Access_Policy
- GitHub's Open Source Guides: https://opensource.guide/
- Google Season of Docs: https://developers.google.com/season-of-docs
