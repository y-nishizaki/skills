---
name: research
description: Conduct thorough research using systematic methodology. Use when researching topics, gathering information, investigating subjects, verifying facts, or performing comprehensive analysis. Keywords - research, investigate, analyze, gather information, fact-check, verify, study.
version: 1.0.0
---

# Research Skill

## Purpose

This skill guides you through conducting rigorous, systematic research following established best practices. It ensures comprehensive information gathering, proper verification, and credible results through a structured methodology.

## When to Use This Skill

Use this skill when:
- User requests to research a topic or subject
- User asks to investigate or analyze information
- User needs to gather comprehensive information on a subject
- User wants to verify facts or cross-check information
- User mentions "research", "investigate", "analyze", or "study"
- User needs a systematic approach to information gathering

## Research Process

### Step 1: Define Research Objectives

Before beginning research, clearly establish:

1. **Research Question**: What specific question are you trying to answer?
2. **Scope**: What are the boundaries of this research?
3. **Success Criteria**: What information would constitute a complete answer?
4. **Time/Depth Constraints**: How comprehensive should the research be?

**Ask the user for clarification if:**
- The research topic is too broad or vague
- Multiple interpretations are possible
- Specific aspects should be prioritized

### Step 2: Plan Information Sources

Identify appropriate sources based on the research topic:

**Primary Sources:**
- Official documentation
- Academic papers and research publications
- Technical specifications
- Original datasets
- Expert interviews or statements

**Secondary Sources:**
- Analysis and commentary
- Tutorials and guides
- News articles (from credible outlets)
- Community discussions (verified)

**Tool-Specific Sources:**
- WebSearch: For current information, recent developments, general knowledge
- WebFetch: For specific documentation, articles, or web pages
- Read: For local documentation, code, or files
- Grep/Glob: For searching within codebases or file systems

### Step 3: Systematic Information Gathering

Follow a structured approach:

1. **Start Broad, Then Narrow**:
   - Begin with overview sources to understand the landscape
   - Identify key concepts, terminology, and subtopics
   - Drill down into specific areas of interest

2. **Use Multiple Sources**:
   - Gather information from at least 2-3 independent sources
   - Cross-reference facts to ensure accuracy
   - Note any conflicting information for further investigation

3. **Document Source Quality**:
   - Evaluate credibility (official docs > blogs)
   - Check publication dates (prefer recent for current topics)
   - Assess author expertise and reputation
   - Note any potential biases

4. **Maintain Organization**:
   - Track which sources provided which information
   - Organize findings by subtopic or theme
   - Note questions that arise during research

### Step 4: Verify and Cross-Check Information

Critical verification practices:

1. **Cross-Reference Facts**:
   - Verify key claims across multiple sources
   - Flag information found in only one source
   - Investigate discrepancies between sources

2. **Check Recency**:
   - Verify information is current and up-to-date
   - Note if practices or facts have changed
   - Prefer recent sources for technical or evolving topics

3. **Evaluate Source Authority**:
   - Official documentation > community resources
   - Peer-reviewed > non-reviewed
   - Expert consensus > individual opinions

4. **Quality Assurance**:
   - Sufficient coverage of the topic
   - Appropriate depth for the user's needs
   - Accurate and reliable information

### Step 5: Synthesize and Present Findings

Organize research results effectively:

1. **Structure Information Clearly**:
   - Use headings and sections for different aspects
   - Present information in logical order
   - Highlight key findings prominently

2. **Provide Context**:
   - Explain technical terms when necessary
   - Connect related concepts
   - Note important caveats or limitations

3. **Include Citations**:
   - Reference specific sources for key claims
   - Provide URLs or file paths when relevant
   - Enable users to verify or explore further

4. **Acknowledge Gaps**:
   - Note areas where information is limited
   - Identify conflicting information
   - Suggest areas for further investigation if needed

## Best Practices

### Information Gathering

- **Thoroughness**: Cover the topic comprehensively within defined scope
- **Efficiency**: Balance depth with the user's needs
- **Diversity**: Use varied source types to get complete picture
- **Recency**: Prioritize current information for evolving topics
- **Reliability**: Favor authoritative, peer-reviewed, or official sources

### Verification

- **Multi-Source Validation**: Confirm key facts from multiple sources
- **Quality Over Quantity**: Better to have fewer high-quality sources
- **Critical Evaluation**: Question claims that seem unusual or unsupported
- **Context Awareness**: Consider the source's perspective and potential bias

### Presentation

- **Clarity**: Present findings in clear, understandable language
- **Structure**: Organize information logically
- **Completeness**: Answer the research question fully
- **Transparency**: Acknowledge limitations and uncertainties
- **Actionability**: Provide practical takeaways when appropriate

## Research Strategies by Topic Type

### Technical/Code Research
- Start with official documentation
- Check recent GitHub issues, discussions, or release notes
- Verify version compatibility
- Look for code examples and best practices
- Cross-check with community resources (Stack Overflow, forums)

### Conceptual/Theoretical Research
- Begin with authoritative definitions
- Review academic or expert sources
- Understand historical context
- Identify current consensus and debates
- Note practical applications

### Current Events/Trends
- Use recent (last 1-2 years) sources
- Check multiple news outlets for balance
- Verify with official statements or data
- Note ongoing developments
- Distinguish facts from speculation

### Best Practices/Methodologies
- Look for established standards or frameworks
- Review expert recommendations
- Consider industry consensus
- Check recent updates or evolutions
- Note context-specific variations

## Error Handling

### Insufficient Information
- Acknowledge gaps explicitly
- Explain what information is unavailable
- Suggest alternative approaches
- Provide partial answers with caveats

### Conflicting Information
- Present multiple perspectives
- Explain the nature of the conflict
- Evaluate which source is more authoritative
- Let user know uncertainty exists

### Outdated Information
- Note when information may be outdated
- Try to find more recent sources
- Explain how things have changed
- Provide historical context if relevant

### Overly Broad Topics
- Ask user to narrow the scope
- Suggest specific aspects to focus on
- Provide high-level overview with option to drill down
- Break research into manageable subtopics

## Tool Usage Guidelines

**WebSearch**:
- Best for: Current information, general knowledge, recent developments
- Use for: Getting an overview, finding recent articles, checking latest trends
- Verify: Cross-check facts from multiple search results

**WebFetch**:
- Best for: Specific articles, documentation, detailed content from known URLs
- Use for: Reading complete articles, accessing specific documentation
- Verify: Check source credibility and publication date

**Read**:
- Best for: Local files, code, documentation in the project
- Use for: Examining existing implementations, local documentation
- Verify: Check file modification dates, version information

**Grep/Glob**:
- Best for: Searching within codebases or file systems
- Use for: Finding implementations, examples, patterns in code
- Verify: Ensure results are from current/active code

## Examples

### Example 1: Technical Research

**User Request**: "Research the best practices for React state management in 2025"

**Expected Behavior**:
1. Define scope: React state management approaches, current best practices
2. Gather information:
   - WebSearch for "React state management best practices 2025"
   - WebFetch React official documentation
   - Research popular solutions (Context, Redux, Zustand, etc.)
3. Verify information from multiple sources
4. Synthesize findings:
   - Overview of current approaches
   - Comparison of popular solutions
   - Best practices and recommendations
   - When to use each approach
   - Recent trends or changes
5. Provide citations and sources

### Example 2: Conceptual Research

**User Request**: "What is test-driven development?"

**Expected Behavior**:
1. Define scope: TDD concept, methodology, benefits
2. Gather information:
   - WebSearch for authoritative definitions
   - Find original sources or standard references
   - Look for practical examples
3. Verify across multiple sources
4. Present findings:
   - Clear definition
   - Core principles and process
   - Benefits and tradeoffs
   - Practical examples
   - Common misconceptions
5. Include references to authoritative sources

### Example 3: Codebase Research

**User Request**: "Research how authentication is implemented in this project"

**Expected Behavior**:
1. Define scope: Authentication flow, methods, security practices
2. Gather information:
   - Grep for authentication-related code
   - Read configuration files
   - Examine authentication modules
   - Check for security middleware
3. Analyze findings:
   - Trace authentication flow
   - Identify methods used (JWT, session, etc.)
   - Note security measures
4. Present results:
   - Overview of authentication approach
   - Key files and functions (with file:line references)
   - Security considerations
   - Any concerns or recommendations

### Example 4: Verification Research

**User Request**: "Verify if this claim about Python performance is accurate"

**Expected Behavior**:
1. Identify specific claim to verify
2. Research from multiple authoritative sources:
   - Official Python documentation
   - Performance benchmarks
   - Expert analysis
3. Cross-check facts across sources
4. Present findings:
   - Verification result (accurate/inaccurate/partially accurate)
   - Supporting evidence from sources
   - Nuances or context that affect accuracy
   - Citations for claims

## Quality Checklist

Before presenting research results, verify:

- [ ] Research question has been answered
- [ ] Information gathered from multiple credible sources
- [ ] Key facts have been cross-verified
- [ ] Sources are appropriately recent for the topic
- [ ] Conflicting information has been investigated
- [ ] Findings are clearly organized and structured
- [ ] Technical terms are explained when necessary
- [ ] Citations or references are provided for key claims
- [ ] Gaps or limitations are acknowledged
- [ ] Result is actionable and useful for the user

## Notes

- **Adapt depth to user needs**: A quick question needs less depth than a comprehensive analysis
- **Be transparent about limitations**: Better to acknowledge gaps than to speculate
- **Prioritize quality over speed**: Thorough research takes time but provides better value
- **Stay objective**: Present facts and multiple perspectives rather than opinions
- **Keep learning**: Research methods evolve, especially for technical topics
