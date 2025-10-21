# Research Skill - Technical Reference

## Research Methodology Framework

This reference document provides detailed technical specifications, methodological guidelines, and advanced research techniques to supplement the main SKILL.md.

## Research Quality Dimensions

### 1. Rigor

**Definition**: The systematic and thorough application of research methods.

**Key Principles**:
- Follow established methodologies consistently
- Apply appropriate validation techniques
- Maintain objectivity throughout the process
- Document methods and decisions transparently

**Implementation**:
- Use structured information gathering protocols
- Apply consistent evaluation criteria across sources
- Maintain audit trail of research decisions
- Validate findings through multiple methods

### 2. Credibility

**Definition**: The trustworthiness and believability of research findings.

**Source Credibility Hierarchy**:

**Tier 1 - Highest Credibility**:
- Official technical documentation
- Peer-reviewed academic publications
- Standards organizations (W3C, IEEE, ISO, etc.)
- Official government sources (for relevant topics)
- Original research data

**Tier 2 - High Credibility**:
- Established industry publications
- Well-known technical books
- Recognized expert blogs/articles
- Conference proceedings
- Reputable news organizations (for current events)

**Tier 3 - Moderate Credibility**:
- Community documentation (well-maintained)
- Technical forums (Stack Overflow, with high votes)
- Corporate blogs (from relevant companies)
- Tutorial sites (established platforms)

**Tier 4 - Lower Credibility** (use with caution):
- Personal blogs (unknown authors)
- Unverified community posts
- Social media comments
- Undated or very old content

**Credibility Assessment Criteria**:
- Author expertise and credentials
- Publication or platform reputation
- Peer review or editorial process
- Citation of sources
- Transparency about methodology
- Recency and maintenance
- Potential conflicts of interest

### 3. Impact

**Definition**: The usefulness and applicability of research findings.

**Maximizing Impact**:
- Align research depth with user needs
- Provide actionable insights
- Include practical examples
- Explain real-world applications
- Highlight key takeaways clearly

## Information Source Evaluation

### CRAAP Test (Adapted for Technical Research)

**Currency**:
- When was information published/updated?
- Is it current enough for the topic?
- Have practices/technologies changed since publication?
- Are links and references still working?

**Relevance**:
- Does it address the research question?
- Is it at the appropriate technical level?
- Is it specific enough to be useful?
- Is it too general or too specific?

**Authority**:
- Who is the author/publisher?
- What are their credentials/expertise?
- Is it from an official or recognized source?
- Is there editorial oversight?

**Accuracy**:
- Is information verifiable?
- Can you confirm it from other sources?
- Are there citations/references?
- Is it free from obvious errors?

**Purpose**:
- Why was this information created?
- Is it educational, commercial, persuasive?
- Are there potential biases?
- Is the perspective balanced?

## Research Patterns and Anti-Patterns

### Patterns (Good Practices)

**1. Triangulation**
- Gather information from multiple independent sources
- Use different types of sources (official docs, community, examples)
- Verify key facts across sources
- Investigate discrepancies thoroughly

**2. Progressive Refinement**
- Start with broad overview
- Identify key concepts and terminology
- Drill down into specific areas
- Revisit broader context if needed

**3. Source Documentation**
- Track which source provided which information
- Note publication dates and authors
- Maintain citations for key claims
- Enable traceability of findings

**4. Critical Evaluation**
- Question extraordinary claims
- Look for supporting evidence
- Consider alternative explanations
- Assess source credibility systematically

**5. Iterative Validation**
- Cross-check facts as you gather them
- Update findings as new information emerges
- Revisit earlier conclusions if needed
- Maintain flexibility in interpretation

### Anti-Patterns (Avoid These)

**1. Single Source Dependency**
- ❌ Relying on only one source
- ✅ Verify from multiple independent sources

**2. Confirmation Bias**
- ❌ Only seeking information that confirms initial assumptions
- ✅ Actively seek diverse perspectives and contrary evidence

**3. Outdated Information**
- ❌ Using old sources without checking for updates
- ✅ Verify information is current for the topic

**4. Authority Worship**
- ❌ Accepting claims uncritically from "expert" sources
- ✅ Verify even expert claims when possible

**5. Scope Creep**
- ❌ Expanding research beyond original question indefinitely
- ✅ Maintain focus on defined objectives, note related topics separately

**6. Analysis Paralysis**
- ❌ Gathering information indefinitely without synthesis
- ✅ Set reasonable completion criteria and synthesize findings

**7. Citation-Free Presentation**
- ❌ Presenting facts without sources
- ✅ Provide references for key claims and findings

## Research Strategies by Context

### Time-Constrained Research

When speed is important:

1. **Prioritize High-Quality Sources**:
   - Start with official documentation
   - Use recognized authoritative sources
   - Skip lower-quality sources unless necessary

2. **Focus Scope Tightly**:
   - Answer specific question only
   - Don't explore tangential topics
   - Provide focused, concise findings

3. **Use Efficient Tools**:
   - WebSearch for quick overview
   - Direct WebFetch to known authoritative sources
   - Grep/Glob for quick code searches

4. **Set Clear Stopping Point**:
   - Define "good enough" criteria
   - Stop when core question is answered
   - Note areas for deeper research if needed

### Comprehensive Research

When depth is important:

1. **Systematic Coverage**:
   - Cover all major aspects of topic
   - Explore related concepts and context
   - Investigate alternative approaches

2. **Deep Source Analysis**:
   - Read complete articles/documentation
   - Follow references and citations
   - Examine original sources when possible

3. **Thorough Verification**:
   - Cross-check all major claims
   - Investigate discrepancies fully
   - Verify understanding through examples

4. **Rich Documentation**:
   - Detailed citations and references
   - Explanation of reasoning and decisions
   - Comprehensive coverage of caveats and limitations

### Uncertainty Resolution

When information is conflicting or unclear:

1. **Identify Nature of Conflict**:
   - Are sources talking about different things?
   - Has information changed over time?
   - Are there legitimate different approaches?

2. **Seek Authoritative Arbitration**:
   - Check official standards or documentation
   - Look for expert consensus
   - Examine recent authoritative sources

3. **Experimental Verification**:
   - For code/technical topics, test if possible
   - Verify through actual implementation
   - Document results of testing

4. **Transparent Presentation**:
   - Explain the conflict clearly
   - Present multiple perspectives
   - Recommend most likely accurate information
   - Acknowledge remaining uncertainty

## Tool-Specific Research Techniques

### WebSearch Best Practices

**Effective Query Construction**:
- Include relevant technical terms
- Add year (e.g., "2025") for current information
- Use "best practices" for methodology questions
- Add "official" or "documentation" for authoritative sources
- Use "vs" or "comparison" to understand options

**Result Evaluation**:
- Prioritize official documentation in results
- Check publication dates prominently
- Look for recognized authority sources
- Cross-reference multiple search results
- Note consensus across results

**Common Uses**:
- Getting overview of topics
- Finding current best practices
- Discovering recent developments
- Identifying authoritative sources
- Understanding landscape of solutions

### WebFetch Best Practices

**When to Use**:
- Reading specific known documentation
- Accessing complete articles
- Getting detailed content from URLs
- Following up on WebSearch results

**Effective Usage**:
- Use specific prompts to extract needed information
- Request summaries for long content
- Ask for specific sections or aspects
- Verify source credibility (check URL, author, date)

**Common Uses**:
- Reading official documentation pages
- Accessing specific blog posts or articles
- Getting detailed technical specifications
- Following references from other sources

### Code Research (Grep/Glob/Read)

**Discovery Process**:
1. **Pattern Finding** (Glob):
   - Find files by name patterns
   - Locate configuration files
   - Discover module structure

2. **Content Search** (Grep):
   - Search for function/class names
   - Find specific patterns in code
   - Locate error messages or constants
   - Discover usage examples

3. **Deep Reading** (Read):
   - Understand implementation details
   - Analyze code flow
   - Read documentation/comments
   - Examine configuration

**Best Practices**:
- Start broad, narrow down progressively
- Follow code references and imports
- Understand context before conclusions
- Note file locations (file:line) in findings
- Verify code is current/active (not deprecated)

## Information Organization Techniques

### Structured Note-Taking

**During Research**:
```
Topic: [Research Question]

Key Findings:
- [Finding 1] [Source]
- [Finding 2] [Source]
- [Finding 3] [Source]

Important Details:
- [Detail 1]
- [Detail 2]

Questions/Gaps:
- [What's still unclear]
- [Conflicting information]

Sources Consulted:
1. [Source 1 - URL/Reference]
2. [Source 2 - URL/Reference]
```

### Synthesis Framework

**Organizing Findings**:

1. **Main Answer**: Direct response to research question
2. **Supporting Details**: Evidence and explanations
3. **Context**: Background or related information
4. **Caveats**: Limitations, exceptions, or conditions
5. **Sources**: References and citations
6. **Further Reading**: Related topics or deeper resources

## Domain-Specific Research Guidelines

### Technical Documentation Research

**Priorities**:
1. Official documentation (primary source)
2. Version-specific information
3. Working code examples
4. Known issues/limitations
5. Migration guides (if relevant)

**Common Pitfalls**:
- Using outdated version documentation
- Missing breaking changes in updates
- Not checking compatibility requirements
- Ignoring deprecation warnings

### Best Practices Research

**Approach**:
1. Look for established standards/frameworks
2. Find expert consensus (multiple authorities)
3. Check recent discussions (practices evolve)
4. Understand context and tradeoffs
5. Identify when rules can be broken

**Sources to Prioritize**:
- Industry standards organizations
- Well-known technical books
- Recognized expert publications
- Official style guides
- Conference talks by experts

### Comparative Research

**Framework**:
1. Identify comparison criteria
2. Research each option independently
3. Gather information on same criteria for each
4. Note relative strengths/weaknesses
5. Consider context dependencies

**Presentation**:
- Clear comparison structure
- Fair representation of each option
- Context for when to choose each
- Acknowledgment of tradeoffs
- Citations for each option's claims

### Troubleshooting Research

**Process**:
1. Understand the problem clearly
2. Search for exact error messages
3. Look for common causes
4. Check version-specific issues
5. Verify with official documentation
6. Consider workarounds if needed

**Sources**:
- Official issue trackers
- Stack Overflow (verified answers)
- GitHub issues/discussions
- Official documentation (known issues)
- Community forums (recognized experts)

## Research Validation Checklist

### Before Presenting Findings

**Completeness**:
- [ ] Research question fully answered
- [ ] All major aspects covered
- [ ] Context provided where needed
- [ ] Examples included for clarity

**Accuracy**:
- [ ] Key facts verified from multiple sources
- [ ] Conflicting information investigated
- [ ] Recency confirmed for time-sensitive topics
- [ ] Technical details validated

**Credibility**:
- [ ] Sources are authoritative and appropriate
- [ ] Citations provided for major claims
- [ ] Source quality evaluated
- [ ] Bias or limitations acknowledged

**Clarity**:
- [ ] Information clearly organized
- [ ] Technical terms explained
- [ ] Logical flow maintained
- [ ] Key takeaways highlighted

**Usefulness**:
- [ ] Actionable for user's needs
- [ ] Appropriate depth for context
- [ ] Practical examples included
- [ ] Next steps or recommendations clear

## Common Research Scenarios

### Scenario 1: "What is [Technology/Concept]?"

**Research Approach**:
1. Find authoritative definition
2. Understand core concepts/principles
3. Learn typical use cases
4. Identify key benefits/tradeoffs
5. Gather practical examples
6. Note current status/adoption

**Key Elements to Include**:
- Clear definition
- Core concepts explained
- When/why to use it
- How it works (high-level)
- Practical examples
- Current relevance

### Scenario 2: "How do I [Accomplish Task]?"

**Research Approach**:
1. Find official/authoritative guidance
2. Look for step-by-step instructions
3. Gather working examples
4. Identify prerequisites/requirements
5. Note common pitfalls
6. Find troubleshooting resources

**Key Elements to Include**:
- Step-by-step instructions
- Prerequisites clearly stated
- Working code examples (if applicable)
- Common issues and solutions
- Best practices
- References to detailed docs

### Scenario 3: "[Technology A] vs [Technology B]?"

**Research Approach**:
1. Research each independently first
2. Identify comparison criteria
3. Find comparative analyses
4. Understand use case differences
5. Check community preferences
6. Note context dependencies

**Key Elements to Include**:
- Fair description of each
- Key differences highlighted
- Use case recommendations
- Tradeoffs clearly stated
- Community adoption/support
- Decision guidance

### Scenario 4: "Is [Claim] true/accurate?"

**Research Approach**:
1. Understand claim precisely
2. Find authoritative sources on topic
3. Look for confirming evidence
4. Seek contradicting evidence
5. Evaluate source quality
6. Consider context/conditions

**Key Elements to Include**:
- Verification result (true/false/partial/conditional)
- Supporting evidence with sources
- Any important nuances or conditions
- Context that affects accuracy
- Confidence level in conclusion

## Advanced Techniques

### Meta-Research

Sometimes research requires researching how to research:
- "What are the authoritative sources for [topic]?"
- "What organizations set standards for [domain]?"
- "Who are recognized experts in [field]?"

### Temporal Analysis

For evolving topics:
- Compare current vs. previous best practices
- Note when practices changed and why
- Identify trends and future directions
- Distinguish stable vs. evolving knowledge

### Gap Analysis

When information is incomplete:
- Identify what's unknown or unclear
- Determine if gaps are critical
- Suggest experiments or tests to fill gaps
- Provide best available information with caveats

### Synthesis Research

Combining information from multiple domains:
- Gather information from each relevant domain
- Identify connections and relationships
- Synthesize unified understanding
- Note domain-specific considerations

## Continuous Improvement

### Learning from Research Sessions

After completing research:
- Note what worked well
- Identify what could be improved
- Learn new authoritative sources
- Recognize patterns in topics
- Build knowledge for future research

### Staying Current

For rapidly evolving fields:
- Monitor official blogs/announcements
- Track version releases and changelogs
- Follow recognized experts
- Check for deprecations or changes
- Update understanding regularly

## References

This research skill is based on established research methodology principles:

- Research methodology best practices for rigorous, credible, and impactful research
- Information literacy and evaluation frameworks (CRAAP test)
- Evidence-based research techniques
- Cross-verification and validation methods
- Systematic information gathering protocols

## Notes

- Research is both art and science - apply principles flexibly based on context
- Quality matters more than quantity - one authoritative source beats ten unreliable ones
- Be honest about limitations - acknowledging gaps is better than speculation
- Keep learning - research techniques evolve, especially for technical topics
- Stay objective - present facts and perspectives, not just confirmation
