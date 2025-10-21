# Research Skill - Extended Examples

This document provides detailed, real-world examples of using the research skill in various scenarios.

## Example 1: Technical Implementation Research

### User Request
"Research how to implement server-side rendering with React in 2025"

### Research Process

**Step 1: Define Objectives**
- Research question: What are the current methods and best practices for implementing SSR with React?
- Scope: Modern approaches, popular frameworks, implementation patterns
- Success criteria: Understanding of options, implementation guidance, code examples

**Step 2: Plan Sources**
- React official documentation
- Next.js documentation (popular SSR framework)
- Recent articles on SSR best practices
- Community discussions and comparisons
- Code examples and tutorials

**Step 3: Information Gathering**

*Query 1: WebSearch "React server-side rendering 2025 best practices"*
- Results show Next.js as dominant solution
- React 18+ features (Server Components, Suspense)
- Alternative frameworks (Remix, Astro)
- Performance considerations

*Query 2: WebFetch React official documentation*
- Server Components introduced in React 18
- Streaming SSR capabilities
- Hydration best practices
- Integration patterns

*Query 3: WebFetch Next.js documentation*
- App Router (current recommended approach)
- Pages Router (legacy but stable)
- Automatic SSR/SSG/ISR handling
- Performance optimization features

**Step 4: Verification**
- Cross-check React Server Components info across official docs and multiple sources
- Verify Next.js is current recommended approach (multiple authoritative sources agree)
- Confirm React 18+ features are stable and production-ready
- Check recent migration guides and version compatibility

**Step 5: Synthesis**

### Research Findings

**Overview**
Server-side rendering (SSR) with React in 2025 has evolved significantly with React 18+ features and mature frameworks.

**Current Approaches**

1. **Next.js (Recommended for most projects)**
   - Most popular and mature SSR framework
   - App Router (React Server Components) - current approach
   - Built-in optimization and routing
   - Strong community and ecosystem

   Source: Next.js official documentation, Vercel blog posts

2. **React Server Components (Native)**
   - Built into React 18+
   - Requires build tool integration
   - More control but more setup
   - Good for custom solutions

   Source: React official documentation

3. **Remix**
   - Full-stack framework
   - Focus on web fundamentals
   - Progressive enhancement
   - Growing adoption

   Source: Remix documentation, community comparisons

**Implementation Example (Next.js App Router)**
```javascript
// app/page.tsx - Server Component by default
async function getData() {
  const res = await fetch('https://api.example.com/data')
  return res.json()
}

export default async function Page() {
  const data = await getData()
  return <div>{data.content}</div>
}
```

**Best Practices**
- Use React Server Components for data fetching
- Implement streaming for improved performance
- Minimize client-side JavaScript
- Use Suspense boundaries for loading states
- Consider static generation (SSG) when possible

**Key Considerations**
- React 18+ required for modern features
- Build tool setup more complex for native approach
- Next.js simplifies many SSR challenges
- Consider hosting requirements (Node.js server needed)

**Sources**
- React Documentation: https://react.dev/reference/react/
- Next.js Documentation: https://nextjs.org/docs
- "React Server Components" (React team blog)
- Community comparisons on SSR frameworks (2024-2025)

---

## Example 2: Comparative Analysis Research

### User Request
"Compare Redux and Zustand for state management"

### Research Process

**Step 1: Define Objectives**
- Compare two state management libraries
- Understand key differences
- Identify use cases for each
- Provide recommendation guidance

**Step 2: Plan Sources**
- Official documentation for both
- Community comparisons and discussions
- GitHub repositories (stars, activity)
- Migration guides or comparison articles
- Code examples for both

**Step 3: Information Gathering**

*Research Redux*
- WebFetch: Official Redux Toolkit documentation
- WebSearch: "Redux best practices 2025"
- Gather: Core concepts, ecosystem, learning curve

*Research Zustand*
- WebFetch: Zustand GitHub repository and docs
- WebSearch: "Zustand state management advantages"
- Gather: Core concepts, simplicity factors, use cases

*Compare*
- WebSearch: "Redux vs Zustand 2025"
- Look for: Migration experiences, performance comparisons, community opinions

**Step 4: Verification**
- Verify popularity metrics from multiple sources (GitHub, npm trends)
- Cross-check performance claims with benchmarks
- Confirm ecosystem maturity from official sources
- Validate code examples work with current versions

**Step 5: Synthesis**

### Research Findings

**Overview**
Redux and Zustand are both popular state management solutions for React, but serve different needs and philosophies.

**Redux (with Redux Toolkit)**

*Strengths:*
- Mature ecosystem with extensive tooling
- DevTools with time-travel debugging
- Well-established patterns and conventions
- Large community and resources
- Middleware ecosystem for complex async logic
- Excellent for large applications with complex state

*Considerations:*
- More boilerplate (even with Redux Toolkit)
- Steeper learning curve
- Can be overkill for simple applications

*Example:*
```javascript
// Redux Toolkit approach
import { createSlice } from '@reduxjs/toolkit'

const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    increment: (state) => { state.value += 1 },
    decrement: (state) => { state.value -= 1 }
  }
})
```

**Zustand**

*Strengths:*
- Minimal boilerplate and simple API
- No provider wrapper needed
- Smaller bundle size (~1KB)
- Easy to learn and use
- Flexible - works outside React too
- Excellent for small to medium applications

*Considerations:*
- Smaller ecosystem and less tooling
- Fewer established patterns
- Less middleware options
- DevTools less mature than Redux

*Example:*
```javascript
// Zustand approach
import create from 'zustand'

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 }))
}))
```

**Key Differences**

| Aspect | Redux | Zustand |
|--------|-------|---------|
| Learning Curve | Moderate-Steep | Minimal |
| Boilerplate | More (even with RTK) | Very minimal |
| Bundle Size | ~12KB (RTK) | ~1KB |
| Ecosystem | Extensive | Growing |
| DevTools | Excellent | Good |
| Best For | Large, complex apps | Small-medium apps |

**Recommendations**

*Choose Redux when:*
- Building large, complex applications
- Need extensive middleware (sagas, observables)
- Want mature DevTools and time-travel debugging
- Team familiar with Redux patterns
- Need established best practices and conventions

*Choose Zustand when:*
- Building small to medium applications
- Want minimal setup and boilerplate
- Prefer simple, flexible API
- Bundle size is a concern
- New project starting fresh

**Migration Considerations**
- Zustand → Redux: May need middleware for complex async
- Redux → Zustand: Can simplify significantly but lose some tooling

**Sources**
- Redux Toolkit Documentation: https://redux-toolkit.js.org/
- Zustand GitHub: https://github.com/pmndrs/zustand
- npm trends comparison (January 2025)
- "Redux vs Zustand" community discussions (2024-2025)
- Performance benchmarks from js-framework-benchmark

---

## Example 3: Fact Verification Research

### User Request
"Verify if it's true that React Server Components eliminate the need for useEffect"

### Research Process

**Step 1: Define Objectives**
- Verify specific claim about React Server Components and useEffect
- Understand the relationship between these concepts
- Provide accurate, nuanced answer

**Step 2: Plan Sources**
- React official documentation (primary authority)
- React team blog posts and announcements
- Technical articles explaining Server Components
- Examples showing both scenarios

**Step 3: Information Gathering**

*Query 1: React Official Documentation on Server Components*
- Server Components run only on server
- Don't have access to browser APIs
- Can't use hooks like useEffect, useState

*Query 2: React Documentation on useEffect*
- useEffect is for synchronizing with external systems
- Only works in Client Components
- Still needed for browser interactions

*Query 3: Articles and Examples*
- Server vs Client Component patterns
- When each is appropriate
- Real-world usage examples

**Step 4: Verification**
- Cross-reference across official React docs
- Confirm in multiple technical articles
- Find code examples demonstrating the nuance
- Check React team's official statements

**Step 5: Synthesis**

### Research Findings

**Verification Result: Partially True (Requires Important Context)**

**Accurate Aspects:**
- Server Components cannot use useEffect (they run on server only)
- Many use cases previously requiring useEffect (like data fetching) can be replaced with Server Components
- Server Components can eliminate useEffect for server-side data fetching

**Important Nuances:**

1. **Server Components CAN'T use useEffect**
   - Server Components run only on the server
   - They don't have access to client-side APIs
   - Hooks like useEffect, useState are not available

   Source: React Documentation - Server Components

2. **Client Components STILL need useEffect**
   - Browser interactions (event listeners, etc.)
   - Client-side state synchronization
   - Working with browser APIs
   - Third-party library integration

   Source: React Documentation - useEffect

3. **Use Case Shift, Not Elimination**
   - Data fetching: Server Components (async/await)
   - Browser interactions: Client Components (useEffect)
   - You use the right tool for each context

   Source: React team blog posts on Server Components

**Example Demonstrating the Difference**

```javascript
// ❌ Server Component - Cannot use useEffect
async function ServerComponent() {
  // This works - async data fetching
  const data = await fetchData()

  // This would ERROR - useEffect not available
  // useEffect(() => { ... }, [])

  return <div>{data}</div>
}

// ✅ Client Component - Can use useEffect
'use client'
function ClientComponent() {
  // This works - client-side effects
  useEffect(() => {
    const handleResize = () => console.log(window.innerWidth)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return <div>Responsive Component</div>
}
```

**Accurate Statement Would Be:**
"React Server Components replace the need for useEffect for server-side operations like data fetching, but useEffect is still essential for client-side interactions and remains necessary in Client Components."

**Why This Matters:**
- Understanding prevents misuse of Server Components
- Clarifies the complementary nature of Server and Client Components
- Helps developers choose the right component type

**Sources:**
- React Documentation: "Server Components"
- React Documentation: "useEffect"
- React team blog: "Introducing Server Components"
- Next.js documentation on component boundaries

**Confidence Level:** High - verified through official React documentation and team statements.

---

## Example 4: Codebase-Specific Research

### User Request
"Research how we handle API errors in this codebase"

### Research Process

**Step 1: Define Objectives**
- Understand current error handling patterns
- Identify where API errors are caught
- Document the approach for team reference

**Step 2: Plan Sources**
- Grep for error handling patterns
- Read API client code
- Examine error handling utilities
- Check middleware or interceptors
- Look for error logging

**Step 3: Information Gathering**

*Search 1: Find API client code*
```bash
Glob: "**/*api*.{ts,js,tsx,jsx}"
```

*Search 2: Look for error handling*
```bash
Grep: "catch|try|Error" in API files
```

*Search 3: Find error utilities*
```bash
Grep: "handleError|errorHandler"
```

*Search 4: Examine configuration*
```bash
Read: axios configuration, fetch wrappers
```

**Step 4: Analysis**
- Read identified files to understand patterns
- Trace error flow from API call to user display
- Note consistency across codebase
- Identify any gaps or inconsistencies

**Step 5: Synthesis**

### Research Findings

**Overview**
The codebase uses a centralized error handling approach with Axios interceptors and custom error utilities.

**Error Handling Architecture**

1. **API Client Setup** (src/api/client.ts:15-45)
   - Axios instance with interceptors
   - Response interceptor catches all API errors
   - Transforms API errors to consistent format

```javascript
// Simplified example
axios.interceptors.response.use(
  response => response,
  error => {
    const apiError = transformError(error)
    logError(apiError)
    return Promise.reject(apiError)
  }
)
```

2. **Error Transformation** (src/utils/errors.ts:10-35)
   - Standardizes different error types
   - Extracts error messages from various formats
   - Adds error codes and metadata

3. **Error Display** (src/components/ErrorBoundary.tsx:20-50)
   - React Error Boundary for unhandled errors
   - Toast notifications for API errors
   - User-friendly error messages

4. **Logging** (src/utils/logger.ts:25-40)
   - Errors logged to console in development
   - Sent to error tracking service in production
   - Includes stack traces and context

**Key Files**
- `src/api/client.ts:15-45` - Axios interceptor setup
- `src/utils/errors.ts:10-35` - Error transformation logic
- `src/components/ErrorBoundary.tsx:20-50` - UI error handling
- `src/utils/logger.ts:25-40` - Error logging
- `src/hooks/useApiCall.ts:30-60` - Hook for API calls with error handling

**Error Types Handled**
- Network errors (no connection)
- HTTP errors (4xx, 5xx status codes)
- Timeout errors
- Validation errors (from API)
- Authentication errors (redirects to login)

**Best Practices Observed**
✅ Centralized error handling
✅ Consistent error format
✅ User-friendly error messages
✅ Error logging for debugging
✅ Graceful degradation

**Areas for Improvement**
- Some components bypass the error handling hook
- Error messages could be more specific in some cases
- Retry logic not implemented for transient failures

**Usage Pattern**
```javascript
// Recommended approach (using custom hook)
const { data, error, loading } = useApiCall('/endpoint')

// Errors automatically handled by interceptor
// Toast notification shown to user
// Error logged for debugging
```

**Sources**
- src/api/client.ts (Axios configuration)
- src/utils/errors.ts (Error utilities)
- src/components/ErrorBoundary.tsx (Error UI)
- src/hooks/useApiCall.ts (API hook)
- src/utils/logger.ts (Logging)

---

## Example 5: Current Events/Trends Research

### User Request
"What's the current state of AI coding assistants in 2025?"

### Research Process

**Step 1: Define Objectives**
- Understand current landscape of AI coding tools
- Identify major players and their capabilities
- Note recent developments and trends

**Step 2: Plan Sources**
- Recent news and articles (last 6 months)
- Official announcements from AI companies
- Developer community discussions
- Comparison articles and reviews

**Step 3: Information Gathering**

*WebSearch: "AI coding assistants 2025"*
- Latest tools and features
- Recent announcements
- Market leaders

*WebSearch: "GitHub Copilot vs Claude Code vs Cursor 2025"*
- Comparative information
- Feature differences
- User preferences

*WebFetch: Official product pages*
- Current capabilities
- Pricing and availability
- Latest updates

**Step 4: Verification**
- Cross-check features from official sources
- Verify adoption numbers from multiple sources
- Confirm recent updates with official announcements
- Check publication dates (ensure recency)

**Step 5: Synthesis**

### Research Findings

**Overview**
As of early 2025, AI coding assistants have matured significantly, with several strong offerings serving different developer needs.

**Major Players**

1. **GitHub Copilot**
   - One of the most widely adopted
   - Integrated directly into VS Code, IDEs
   - Strong code completion and generation
   - Enterprise version with customization

2. **Claude Code (Anthropic)**
   - Command-line interface approach
   - Strong at complex refactoring and understanding
   - Conversational workflow
   - Skill system for customization

3. **Cursor**
   - AI-native code editor
   - Chat and inline editing
   - Codebase-aware assistance
   - Growing developer base

4. **Amazon CodeWhisperer**
   - AWS integrated
   - Security scanning included
   - Good for AWS services
   - Free tier available

**Current Trends (Early 2025)**

1. **Codebase Awareness**
   - Tools increasingly understand entire projects
   - Context from multiple files
   - Better architecture suggestions

2. **Agentic Capabilities**
   - AI performing multi-step tasks autonomously
   - Planning and executing complex refactors
   - Running tests and fixing issues

3. **Specialization**
   - Tools optimizing for specific workflows
   - Command-line vs IDE integration
   - Different strengths emerging

4. **Security Focus**
   - Code scanning and security analysis
   - License compliance checking
   - Vulnerability detection

**Adoption Status**
- ~40-50% of professional developers use AI coding tools regularly (various surveys)
- Most common use: code completion and generation
- Growing use: refactoring, documentation, testing

**Key Considerations**

*Choosing a Tool:*
- IDE vs command-line preference
- Existing tool integration
- Budget (free vs paid tiers)
- Use case (quick suggestions vs complex tasks)
- Privacy/security requirements

*Current Limitations:*
- Still require developer oversight
- Can suggest incorrect or insecure code
- Variable quality across different languages/frameworks
- Context window limitations

**Recent Developments (Last 3 Months)**
- Expanded context windows
- Better multi-file editing
- Improved test generation
- Enhanced debugging capabilities

**Looking Forward**
- Continued improvement in accuracy
- Better understanding of complex codebases
- More specialized tools for specific domains
- Integration with development workflows

**Sources**
- GitHub Copilot official documentation (January 2025)
- Anthropic Claude Code release (2025)
- Developer surveys from Stack Overflow, JetBrains (2024-2025)
- Tech news coverage from Verge, Ars Technica (December 2024 - January 2025)
- Official product announcements

**Last Updated:** January 2025

**Note:** This is a rapidly evolving field. Information may change quickly with new releases and updates.

---

## Example 6: Quick Definition Research

### User Request
"What is tree-shaking in JavaScript?"

### Research Process

**Step 1: Define Objectives**
- Provide clear definition
- Explain how it works
- Give practical context

**Step 2: Quick Source Strategy**
- Official bundler documentation
- Authoritative JavaScript resources
- Clear examples

**Step 3: Information Gathering**
- WebSearch: "tree-shaking JavaScript definition"
- WebFetch: webpack or Rollup documentation
- Look for clear examples

**Step 4: Quick Verification**
- Confirm definition across sources
- Verify technical accuracy

**Step 5: Concise Synthesis**

### Research Findings

**Definition**
Tree-shaking is a dead code elimination technique used in JavaScript bundlers to remove unused exports from the final bundle.

**How It Works**
1. Bundler analyzes ES6 module imports/exports
2. Identifies which exports are actually used
3. Eliminates unused code from final bundle
4. Results in smaller bundle size

**Example**
```javascript
// utils.js
export function usedFunction() { /* ... */ }
export function unusedFunction() { /* ... */ }  // Will be tree-shaken

// app.js
import { usedFunction } from './utils'
usedFunction()  // Only this is included in bundle
```

**Requirements**
- ES6 modules (import/export)
- Module bundler that supports it (webpack, Rollup, etc.)
- Side-effect-free code

**Benefits**
- Smaller bundle sizes
- Faster load times
- Better performance

**Sources**
- Webpack documentation: "Tree Shaking"
- Rollup documentation
- MDN Web Docs

---

## Common Research Patterns Summary

### Pattern 1: Breadth-First (Overview)
1. Get high-level understanding
2. Identify major concepts
3. Provide concise summary
4. Reference sources for depth

**Use for:** Quick definitions, overviews, initial exploration

### Pattern 2: Depth-First (Comprehensive)
1. Thorough investigation of topic
2. Multiple authoritative sources
3. Detailed examples and explanations
4. Comprehensive coverage

**Use for:** Complex topics, implementation guides, thorough analysis

### Pattern 3: Comparative (Analysis)
1. Research each option independently
2. Identify comparison criteria
3. Evaluate based on same criteria
4. Provide context-specific recommendations

**Use for:** Technology comparisons, solution evaluation, decision support

### Pattern 4: Verification (Fact-Checking)
1. Identify specific claim
2. Find authoritative sources
3. Look for confirming and contradicting evidence
4. Provide nuanced, accurate conclusion

**Use for:** Fact-checking, claim verification, accuracy validation

### Pattern 5: Discovery (Codebase)
1. Search for relevant code patterns
2. Read and analyze findings
3. Trace through implementation
4. Document patterns and locations

**Use for:** Understanding existing code, finding implementations, analyzing architecture

---

## Tips for Effective Research

1. **Match depth to need** - Quick question = concise answer
2. **Start authoritative** - Official docs first, community second
3. **Verify claims** - Cross-check important facts
4. **Note limitations** - Be honest about gaps and uncertainties
5. **Provide context** - Help users understand nuances
6. **Cite sources** - Enable verification and further reading
7. **Stay current** - Check dates for time-sensitive topics
8. **Organize clearly** - Structure makes information accessible
9. **Include examples** - Concrete examples clarify concepts
10. **Be objective** - Present facts and perspectives fairly
