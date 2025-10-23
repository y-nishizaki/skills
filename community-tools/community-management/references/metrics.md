# Community Health Metrics and Measurement Strategies

This reference provides frameworks and metrics for assessing and improving open source community health.

## Overview

Community health metrics help answer critical questions:
- Is the community growing or declining?
- Are new contributors becoming sustained contributors?
- Is the project healthy and sustainable?
- Where should we focus improvement efforts?

## Core Metric Categories

### 1. Contribution Metrics

**New Contributors**
- **Definition**: Unique individuals making their first contribution in a time period
- **Measurement**: Count distinct authors of merged PRs who have no prior contributions
- **Target**: Steady or increasing trend
- **Signals**:
  - Increasing: Project is attracting newcomers
  - Decreasing: Onboarding barriers may exist
  - Stable: Healthy replacement rate

**Contribution Frequency**
- **Definition**: How often contributions occur
- **Measurement**:
  - Commits per week/month
  - PRs opened per week/month
  - Issues created per week/month
- **Breakdowns**: By contributor type (new, occasional, regular, core)
- **Healthy Pattern**: Consistent activity without extreme spikes or valleys

**Contribution Distribution**
- **Definition**: How contributions are distributed across contributors
- **Measurement**:
  - Percentage of contributions from top 10 contributors
  - Gini coefficient of contribution distribution
- **Signals**:
  - High concentration (>80% from top 10): Bus factor risk
  - Broad distribution: Healthy, diverse community
- **Target**: <70% of contributions from top 20% of contributors

**Types of Contributions**
Track beyond code:
- Code contributions (commits, PRs)
- Issue triage and management
- Documentation improvements
- Code reviews performed
- Community support (forum answers, chat help)
- Event organization
- Marketing and advocacy

### 2. Engagement Metrics

**Contributor Retention**
- **Definition**: Percentage of contributors who continue contributing over time
- **Measurement**:
  - % of new contributors who make 2nd contribution within 90 days
  - % of contributors active in current period who were active in previous period
- **Cohort Analysis**: Track cohorts of contributors over time
- **Healthy Ranges**:
  - 30-50% of newcomers make 2nd contribution
  - 60-80% of regular contributors remain active quarter-over-quarter

**Response Times**
- **Issue Response Time**: Time from issue creation to first response
  - Target: <48 hours for 80% of issues
- **PR Response Time**: Time from PR submission to first review
  - Target: <72 hours for 80% of PRs
- **Resolution Time**: Time from issue/PR creation to closure
  - Varies by complexity; track by label/category

**Community Activity**
- Forum/chat messages per week
- Meeting attendance
- Event participation
- Documentation views

**Engagement Depth**
- Single-contribution vs. multi-contribution authors
- Progression through contribution ladder
- Time to second, fifth, tenth contribution

### 3. Diversity and Inclusion Metrics

**Geographic Diversity**
- Contributors by country/timezone
- Event attendance by region
- Language diversity in communications

**Organizational Diversity**
- Contributors by employer/affiliation
- Company concentration risk
- Independent contributor percentage

**Demographic Diversity** (if data available)
- Self-reported gender, race/ethnicity
- Career stage (student, early career, experienced, retired)
- Professional background

**Inclusion Indicators**
- Code of Conduct reports and resolution times
- Sentiment in community channels
- Newcomer welcome rate (% of new contributors who receive welcoming response)
- Participation in governance by diverse groups

### 4. Project Health Metrics

**Issue Management**
- Open issue count and trend
- Issue age distribution
- Issues closed per month
- Issue close rate (closed / opened ratio)
- Ratio of bugs to feature requests
- Healthy Patterns:
  - Stable or decreasing backlog
  - >80% of issues receive response within 1 week
  - Close rate matches or exceeds open rate

**Pull Request Health**
- PR merge rate (% of PRs ultimately merged)
- PR rejection rate and reasons
- Time to merge
- Abandoned PR rate (no activity for 30+ days)
- Healthy Patterns:
  - >60% merge rate
  - <20% abandoned rate
  - Decreasing time to merge

**Code Quality**
- Test coverage percentage
- Linter violation trends
- Technical debt metrics
- Security vulnerability reports and fix times
- Documentation coverage

**Release Cadence**
- Time between releases
- Release planning transparency
- Breaking change frequency
- Healthy Pattern: Predictable, regular release schedule

### 5. Sustainability Metrics

**Bus Factor**
- **Definition**: Number of contributors who could leave before project is at risk
- **Measurement**: Minimum number of contributors accounting for 50% of contributions
- **Target**: >3 (ideally >5)
- **Mitigation**: Knowledge sharing, documentation, distributed ownership

**Contributor Pipeline**
Track movement through contributor ladder:
- Users → First-time contributors: Conversion rate
- First-time → Occasional: Retention rate
- Occasional → Regular: Progression rate
- Regular → Committer: Promotion rate

**Financial Sustainability** (if applicable)
- Sponsorship/donation trends
- Grant funding secured
- Commercial support revenue
- Runway (months of funding remaining)

**Organizational Health**
- Number of active maintainers
- Maintainer workload distribution
- Succession planning status
- Documented project knowledge

## Measurement Tools and Platforms

### GitHub/GitLab Analytics

**Built-in Metrics**:
- Insights → Contributors: Contribution graphs
- Insights → Community: Community profile checklist
- Pulse: Recent activity summary
- Traffic: Repository traffic and clones

**Limitations**: Limited historical data, basic metrics only

### CHAOSS Metrics

**CHAOSS Project** (Community Health Analytics Open Source Software)
- Provides standard metric definitions
- Open source measurement tools
- Focus areas: Growth, Maturity, Decline, Diversity, Risk

**Key CHAOSS Metrics**:
- Change Requests: PR/MR activity and efficiency
- Code Development: Commits, lines changed, reviews
- Issue Resolution: Issue lifecycle and resolution
- Community Growth: New contributors, retention
- Organizational Diversity: Company participation distribution

**Tools**: GrimoireLab, Augur

### Open Source Dashboards

**LFX Insights** (Linux Foundation)
- Comprehensive metrics dashboard
- Email domain analysis for organizational diversity
- Geographic diversity tracking
- Time-series analysis

**Orbit** (Community Platform)
- Activity tracking across platforms
- Member profiles and contribution history
- Engagement scoring

**Bitergia Analytics**
- Based on CHAOSS metrics
- Custom dashboards
- Cross-platform aggregation

### Custom Analytics

**Data Sources**:
- Git history: `git log` analysis
- GitHub/GitLab API: Issues, PRs, comments
- Chat platforms: Slack/Discord APIs
- Forum: Discourse API
- Mailing lists: Archive analysis

**Analysis Tools**:
- Python: pandas, matplotlib for custom analysis
- SQL: Query structured data
- Jupyter notebooks: Interactive exploration

## Setting Up Metrics Collection

### 1. Define Goals

What do you want to improve?
- Growing contributor base
- Improving retention
- Reducing response times
- Increasing diversity
- Ensuring sustainability

### 2. Select Metrics

Choose 5-10 key metrics aligned with goals:
- Leading indicators (predict future state)
- Lagging indicators (measure past performance)
- Mix of quantitative and qualitative

### 3. Establish Baselines

Measure current state:
- Historical trends (if data available)
- Current snapshot
- Industry benchmarks (if available)

### 4. Set Targets

Define success:
- Absolute targets (e.g., 50 new contributors per quarter)
- Relative targets (e.g., 20% increase in retention)
- Maintain targets (e.g., keep bus factor >3)

### 5. Implement Collection

Automate where possible:
- Scheduled scripts to gather data
- Dashboard tools for visualization
- Regular export and archival

### 6. Regular Review

Establish rhythm:
- Weekly: Operational metrics (response times, PR queue)
- Monthly: Contribution and engagement trends
- Quarterly: Strategic metrics (retention, diversity, sustainability)
- Annually: Comprehensive health assessment

## Interpreting Metrics

### Context Matters

Consider external factors:
- **Seasonality**: Holidays, academic calendars, conference schedules
- **Project Lifecycle**: Maturity stage affects expected patterns
- **Major Events**: Releases, security issues, leadership changes
- **Industry Trends**: General shifts in technology adoption

### Correlated Metrics

Look for relationships:
- Decreased PR merge rate + increased response time = reviewer bottleneck
- Increased new contributors + decreased retention = onboarding issues
- Concentrated contributions + low bus factor = sustainability risk

### Qualitative Context

Numbers don't tell the whole story:
- Conduct periodic surveys
- Hold listening sessions
- Monitor sentiment in discussions
- Gather contributor stories

## Acting on Metrics

### Response Times Too High

**Actions**:
- Recruit more reviewers/triagers
- Implement PR size limits
- Create triage guidelines
- Set up automated labeling
- Establish response time SLAs

### Low Contributor Retention

**Actions**:
- Improve first-time contributor experience
- Implement mentorship program
- Create "good first issue" pipeline
- Gather exit feedback from departed contributors
- Recognize contributions publicly

### High Contribution Concentration

**Actions**:
- Identify domain experts to elevate
- Document tribal knowledge
- Distribute subsystem ownership
- Implement succession planning
- Recruit in underserved areas

### Declining Contributor Growth

**Actions**:
- Marketing and outreach campaigns
- Conference presence
- Improve documentation
- Reduce barriers to entry
- Showcase compelling use cases

### Diversity Gaps

**Actions**:
- Partner with diversity-focused organizations
- Sponsor underrepresented contributors
- Review language and imagery for inclusivity
- Implement blind review processes
- Ensure accessible communication tools

## Metric Pitfalls to Avoid

### Vanity Metrics

**Avoid Focusing On**:
- Total stars/forks (popularity ≠ health)
- Total download count (usage ≠ community)
- Commit count alone (quantity ≠ quality)

**Instead Focus On**:
- Contributor retention and growth
- Contribution quality and impact
- Community engagement depth

### Gaming Metrics

When metrics become targets, people optimize for the metric rather than the goal:
- **Problem**: Counting commits leads to commit spam
- **Solution**: Measure meaningful changes, not commit count

- **Problem**: Rewarding issue closure leads to premature closes
- **Solution**: Measure issue resolution quality, gather feedback

### Metric Obsession

Remember:
- Metrics are indicators, not goals
- Qualitative feedback matters
- Community health is multifaceted
- Some important factors resist quantification

## Reporting and Transparency

### Public Health Reports

Share metrics with community:
- Monthly/quarterly blog posts
- Annual state of the community report
- Real-time dashboards (where appropriate)

**Benefits**:
- Transparency builds trust
- Attracts contributors who value health
- Enables community-driven improvements
- Demonstrates commitment to sustainability

### Private Analysis

Some metrics remain internal:
- Individual contributor performance (avoid public ranking)
- Sensitive organizational data
- Pre-decision strategic planning

## Example Metrics Dashboard

### Weekly Operational View

```
Community Health - Week of [Date]

🚀 Contributions
- PRs opened: 45 (↑ 12% vs. last week)
- PRs merged: 38 (↓ 5% vs. last week)
- Issues opened: 23 (→ same as last week)
- Issues closed: 27 (↑ 17% vs. last week)

⏱️ Response Times
- Issue first response: 18 hours median (target: <24h) ✅
- PR first review: 36 hours median (target: <48h) ✅
- PR merge time: 5.2 days median

👥 Contributors
- Active contributors: 67
- First-time contributors: 8 (👏)
- Returning contributors: 12

⚠️ Attention Needed
- 15 PRs awaiting review >5 days
- 8 issues with no response >48 hours
- Reviewer @alice approaching burnout (20 reviews this week)
```

### Quarterly Strategic View

```
Q2 2025 Community Health Report

📈 Growth
- New contributors: 89 (+15% vs. Q1)
- Retention (2+ contributions): 42% (target: 40%) ✅
- Total active contributors: 234 (+8% vs. Q1)

🌍 Diversity
- Geographic: 42 countries represented
- Organizational: 78 organizations (+12 vs. Q1)
- Top company contribution: 35% (target: <40%) ✅

💪 Sustainability
- Bus factor: 7 (target: >5) ✅
- Maintainer count: 12 (stable)
- Avg maintainer tenure: 2.3 years

📊 Project Health
- Issue close rate: 1.2 (closing more than opening) ✅
- PR merge rate: 73% (target: >70%) ✅
- Test coverage: 82% (+3% vs. Q1)
- Avg response time: 24 hours (target: <48h) ✅

🎯 Goals for Q3
1. Increase newcomer retention to 50%
2. Launch mentorship program
3. Improve documentation coverage to 90%
4. Reduce PR merge time to <4 days
```

## Resources

- CHAOSS Metrics: https://chaoss.community/metrics/
- LFX Insights: https://insights.lfx.linuxfoundation.org/
- GitHub Community Insights: https://docs.github.com/en/communities
- "Measuring Open Source Community Health" (O'Reilly): https://www.oreilly.com/library/view/measuring-open-source/
- Mozilla's Open Source Archetypes: https://blog.mozilla.org/opendesign/open-source-archetypes/
