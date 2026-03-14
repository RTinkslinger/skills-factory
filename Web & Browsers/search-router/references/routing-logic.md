# Search Router - Detailed Routing Logic

## Context7 Library ID Patterns

When using Context7, you must first resolve the library ID. Common patterns:

| Library | Likely ID Format | Notes |
|---------|------------------|-------|
| React | `react` | Core React library |
| Next.js | `next.js` or `nextjs` | App Router preferred |
| Vue | `vue` | Vue 3 by default |
| Supabase | `supabase` | Includes auth, storage, etc. |
| Prisma | `prisma` | ORM documentation |
| Express | `express` | Node.js framework |
| Tailwind CSS | `tailwindcss` | Utility-first CSS |
| TypeScript | `typescript` | Language docs |

### Context7 Workflow

```
1. User asks: "How do I use middleware in Next.js?"

2. Extract library: "Next.js"

3. Call resolve-library-id:
   mcp__plugin_context7_context7__resolve-library-id
   libraryName: "next.js"

4. Get libraryId from response (e.g., "nextjs-14")

5. Call query-docs:
   mcp__plugin_context7_context7__query-docs
   libraryId: "nextjs-14"
   query: "middleware"
```

---

## Edge Cases & Routing Decisions

### Multiple Libraries Mentioned

**Query:** "How to integrate Prisma with Next.js"

**Decision:** Use Context7 for BOTH, then synthesize:
1. Context7 → Prisma (integration patterns)
2. Context7 → Next.js (API routes/server actions)
3. Combine insights

### Library Not in Context7

**Query:** "How to use [obscure-library] for X"

**Fallback Chain:**
1. Try Context7 resolve-library-id
2. If not found → Exa Code Context
3. If still unclear → Native WebSearch

### Ambiguous Queries

**Query:** "Best way to handle authentication"

**Analysis:**
- No specific library → NOT Context7
- General pattern → Exa Code Context
- Could also try Native WebSearch if cost-sensitive

**Query:** "NextAuth authentication setup"

**Analysis:**
- Specific library (NextAuth) → Context7
- Library: "next-auth" or "nextauth"

---

## Exa Parameter Guidelines

### Web Search Parameters

```javascript
{
  query: "your search query",
  type: "auto",           // or "keyword" for exact matches
  numResults: 10,         // 5-15 typical range
  useHighlights: true,    // Extract relevant snippets
  livecrawl: true         // For current info (costs more)
}
```

### Code Context Parameters

```javascript
{
  query: "your code question",
  numResults: 5,          // Code context is denser
  useHighlights: true
}
```

### Company Research Parameters

```javascript
{
  company: "Company Name",
  numResults: 3           // 3-5 typical
}
```

---

## Query Classification Examples

### Definitely Context7 (FREE)

- "React useEffect cleanup"
- "Supabase row level security policies"
- "Prisma findMany with relations"
- "Next.js server actions form handling"
- "Vue composables tutorial"
- "Express middleware error handling"
- "Tailwind responsive breakpoints"

### Definitely Exa Code Context

- "How do modern frameworks handle hydration"
- "Comparing ORMs for TypeScript"
- "Best practices for API versioning"
- "Rate limiting implementation patterns"
- "Microservices event sourcing patterns"

### Definitely Native WebSearch (FREE)

- "What is the current Bitcoin price"
- "Weather in San Francisco"
- "Latest tech news today"
- "When was [event]"
- "What is [basic concept]"

### Definitely Exa Company Research

- "Tell me about Anthropic's products"
- "Stripe funding history"
- "Who are Vercel's competitors"
- "What does Linear do"

### Definitely Exa Web Search

- "Who is Dario Amodei"
- "Best databases for real-time apps 2026"
- "Comparison of cloud providers"
- "History of [technology]"

---

## Cost Tracking (Mental Model)

Per session, track approximate costs:

| Action | Cost |
|--------|------|
| Context7 query | $0.00 |
| Native WebSearch | $0.00 |
| Exa Web Search | ~$0.005 |
| Exa Code Context | ~$0.006 |
| Exa Company Research | ~$0.008 |

**Rule of thumb:** If you can answer with Context7 or Native WebSearch, always try those first. Use Exa when:
- Speed is critical (sub-350ms)
- Semantic understanding needed
- Free alternatives failed or are clearly inadequate
- User explicitly requests comprehensive research

---

## Common Mistakes to Avoid

1. **Using Exa for simple library docs** → Use Context7 (free)
2. **Using Native WebSearch for code patterns** → Use Exa Code Context (better results)
3. **Using Web Search for company info** → Use Company Research (specialized)
4. **Not trying Context7 first for any named library** → Always try free first
5. **Using Exa for real-time data** → Use Native WebSearch (fresher data)
