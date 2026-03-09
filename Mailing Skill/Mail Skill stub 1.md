# Universal Email Capability for Claude Agents

> **Date:** January 9, 2026
> **Purpose:** Give any Claude agent human-like email communication abilities with persistent memory
> **Architecture:** Cloud-ready but local-first

---

## Executive Summary

This plan creates a **reusable skill** that any Claude agent can inherit to gain:
1. **Email mailbox** - Send/receive emails via AgentMail
2. **Persistent memory** - Remember contacts, knowledge, tasks across sessions
3. **Identity system** - Each agent has its own persona and configuration
4. **Thread management** - Clean email threading per contact

**Key Design Principle:** Start local (SQLite), design for cloud portability (PostgreSQL/Supabase).

---

## Local vs Cloud Storage Tradeoffs

| Factor | Local (SQLite) | Cloud (PostgreSQL/Supabase) |
|--------|----------------|------------------------------|
| **Setup** | Zero config - just a file | Account, connection string, env vars |
| **Cost** | Free | $0-25/mo (free tiers exist) |
| **Latency** | ~1ms (local disk) | 20-100ms (network round trip) |
| **Multi-device** | Only this machine | Access from anywhere |
| **Multi-agent** | File locking issues if concurrent | Native concurrent access |
| **Backup** | Manual / your responsibility | Automatic + point-in-time recovery |
| **Deployment** | Complex (absolute paths) | Simple (connection string) |
| **Offline** | Works offline | Requires internet |
| **Data size** | Practical limit ~10GB | Virtually unlimited |

### Recommendation: Hybrid Start

**Start local, design for portability, migrate when needed.**

Why this makes sense:
1. **Faster iteration** - No cloud setup friction while prototyping
2. **Schema stays the same** - SQLite → PostgreSQL migration is straightforward
3. **MCP supports both** - Just change the connection config
4. **You'll know when you need cloud** - When you want:
   - Agents running on servers (not your laptop)
   - Multiple agents writing simultaneously
   - Access from different machines
   - Automatic backups

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLAUDE AGENT                                       │
│                                                                              │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐    │
│  │  Email Skill    │    │  Identity File   │    │   Memory Database   │    │
│  │  (SKILL.md)     │    │  (identity.md)   │    │   (memory.db)       │    │
│  │                 │    │                  │    │                     │    │
│  │  • How to email │    │  • Agent name    │    │  • Contacts         │    │
│  │  • When to log  │    │  • Email address │    │  • Knowledge        │    │
│  │  • Memory ops   │    │  • Inbox ID      │    │  • Tasks            │    │
│  │                 │    │  • Role/persona  │    │  • Instructions     │    │
│  │                 │    │  • Style guide   │    │  • Sessions         │    │
│  └────────┬────────┘    └────────┬─────────┘    └──────────┬──────────┘    │
│           │                      │                         │               │
│           └──────────────────────┼─────────────────────────┘               │
│                                  │                                          │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌─────────────────────┐       ┌─────────────────────┐
        │    AgentMail MCP    │       │    SQLite MCP       │
        │                     │       │                     │
        │  • send_email       │       │  • query            │
        │  • list_messages    │       │  • execute          │
        │  • get_message      │       │                     │
        │  • reply            │       │  (or PostgreSQL)    │
        │  • create_inbox     │       │                     │
        └──────────┬──────────┘       └──────────┬──────────┘
                   │                             │
                   ▼                             ▼
        ┌─────────────────────┐       ┌─────────────────────┐
        │  AgentMail Cloud    │       │  Local SQLite File  │
        │                     │       │  (or Cloud DB)      │
        │  • Email storage    │       │                     │
        │  • Threading        │       │  • Agent memory     │
        │  • Webhooks         │       │  • Portable schema  │
        └─────────────────────┘       └─────────────────────┘
```

---

## Directory Structure

```
~/.claude/
├── skills/
│   └── email-capability/
│       ├── SKILL.md                 # Main capability definition
│       ├── memory-schema.sql        # Database schema (SQLite/PostgreSQL compatible)
│       ├── memory-operations.md     # How to use memory effectively
│       └── identity.template.md     # Template for new agent identities
│
├── agents/
│   ├── registry.json                # Index of all agents
│   └── [agent-name]/
│       ├── identity.md              # Agent's configuration
│       ├── memory.db                # SQLite database (local mode)
│       └── memory.config.json       # Database connection config
│
└── claude.json                      # MCP server configuration
```

---

## Component Details

### 1. Email Capability Skill (`SKILL.md`)

The main skill file that teaches any agent how to use email:

```yaml
---
name: email-capability
description: Gives any Claude agent human-like email communication abilities
triggers:
  - "send email"
  - "check inbox"
  - "email"
  - "reply to"
  - "compose message"
---
```

**Core Capabilities:**
- Send emails via AgentMail MCP
- Check and read inbox
- Reply with proper threading
- Integrate with memory system

**Key Behaviors:**
1. **Session Start**: Load identity, recent sessions, active tasks, standing instructions
2. **During Session**: Track contacts, store knowledge, manage tasks, log emails
3. **Session End**: Create summary for continuity

### 2. Identity System

Each agent has an identity file that defines:

```yaml
---
name: "Sales Agent"
email: "sales@yourdomain.agentmail.to"
inbox_id: "inb_xxx"
role: "SDR handling inbound leads"
personality: "Professional but friendly"
---

# Sales Agent

## Communication Style
- Tone: Professional, helpful
- Length: Concise for follow-ups, detailed for first contact
- Always include clear CTA

## Standing Instructions
- Always check contacts before emailing
- Escalate pricing questions to human
- Log all interactions
```

### 3. Memory Schema

SQLite database with 6 core tables:

| Table | Purpose |
|-------|---------|
| `contacts` | Who have I interacted with? |
| `knowledge` | What facts do I know? |
| `tasks` | What am I working on? |
| `instructions` | What are my standing orders? |
| `sessions` | What happened in past work? |
| `email_log` | Record of all emails sent/received |
| `conversation_threads` | Track logical email threads |

**Key Design Choices:**
- UUIDs as primary keys (portable to any database)
- JSON columns for flexible metadata
- `is_current` flag for knowledge versioning (not delete, supersede)
- Views for common queries

### 4. Memory Configuration

**Local Mode (Default):**
```json
{
  "type": "sqlite",
  "path": "./memory.db"
}
```

**Cloud Mode (Future):**
```json
{
  "type": "postgres",
  "url": "postgresql://user:pass@db.supabase.co:5432/agent_memory"
}
```

---

## Memory System Deep Dive

### Session Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SESSION START                                    │
│                                                                          │
│  1. Load identity file                                                   │
│  2. Query: Recent session summaries (last 3)                            │
│  3. Query: Active tasks                                                  │
│  4. Query: Standing instructions                                         │
│  5. Query: Overdue tasks (alert if any)                                 │
│                                                                          │
│  Agent now has full context of who they are and what's pending          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DURING SESSION                                    │
│                                                                          │
│  On receiving email:                                                     │
│  ├── Update contact's last_contact_date                                 │
│  ├── Log email to email_log                                              │
│  ├── Extract any new facts → knowledge table                            │
│  ├── Check if resolves any waiting tasks                                │
│  └── Update conversation_threads                                         │
│                                                                          │
│  On sending email:                                                       │
│  ├── Check recipient in contacts (add if new)                           │
│  ├── Load relevant knowledge about recipient                            │
│  ├── Log email to email_log                                              │
│  ├── Update conversation_threads (for reply threading)                  │
│  └── Create follow-up task if needed                                    │
│                                                                          │
│  On learning something:                                                  │
│  └── INSERT into knowledge (with source reference)                      │
│                                                                          │
│  On completing task:                                                     │
│  └── UPDATE tasks SET status = 'completed', outcome = '...'             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SESSION END                                      │
│                                                                          │
│  INSERT INTO sessions:                                                   │
│  ├── summary: "Processed 5 emails, sent 2 proposals..."                 │
│  ├── emails_processed: 5                                                 │
│  ├── emails_sent: 2                                                      │
│  ├── tasks_created: ["task_1", "task_2"]                                │
│  ├── tasks_completed: ["task_3"]                                        │
│  ├── key_learnings: "Acme prefers morning calls"                        │
│  └── open_items: "Waiting on John's legal review"                       │
│                                                                          │
│  Next session starts with this context automatically                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Knowledge Versioning

Instead of updating facts, we supersede them to maintain history:

```sql
-- Old fact: "Acme revenue is $5M"
-- New info: "Acme revenue is now $7M"

-- Step 1: Mark old as superseded
UPDATE knowledge SET is_current = FALSE, superseded_by = 'new_id'
WHERE subject = 'Acme Corp' AND attribute = 'revenue' AND is_current = TRUE;

-- Step 2: Insert new fact
INSERT INTO knowledge (category, subject, attribute, value, source, learned_date)
VALUES ('company', 'Acme Corp', 'revenue', '$7M ARR', 'email', date('now'));
```

This allows:
- Querying current state: `WHERE is_current = TRUE`
- Viewing history: All records for a subject/attribute
- Understanding changes over time

---

## MCP Configuration

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "agentmail": {
      "command": "npx",
      "args": ["-y", "@agentmail/mcp"],
      "env": {
        "AGENTMAIL_API_KEY": "your-api-key-here"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-sqlite"],
      "env": {
        "SQLITE_DB_PATH": "~/.claude/agents/default/memory.db"
      }
    }
  }
}
```

**For multiple agents**, you'd either:
1. Use a single database with agent_id column
2. Dynamically set SQLITE_DB_PATH based on current agent
3. Use cloud database where connection string is constant

---

## Agent Onboarding Flow

When a new agent needs to be created:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 1: API KEY CHECK                                │
│                                                                          │
│  Does user have AgentMail API key?                                       │
│  ├── Yes → Continue to Step 2                                            │
│  └── No → Guide to https://agentmail.to to sign up                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 2: CREATE INBOX                                 │
│                                                                          │
│  Use AgentMail MCP:                                                      │
│  mcp__agentmail__create_inbox(                                           │
│      name: "Sales Agent",                                                │
│      username: "sales-agent"                                             │
│  )                                                                       │
│                                                                          │
│  Returns: inbox_id, email address                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 3: CREATE IDENTITY FILE                         │
│                                                                          │
│  Create: ~/.claude/agents/sales-agent/identity.md                        │
│  ├── name: "Sales Agent"                                                 │
│  ├── email: "sales-agent@yourdomain.agentmail.to"                       │
│  ├── inbox_id: "inb_xxx" (from Step 2)                                  │
│  ├── role: (user defines)                                                │
│  └── personality: (user defines)                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 4: INITIALIZE MEMORY                            │
│                                                                          │
│  Create: ~/.claude/agents/sales-agent/memory.db                          │
│  Execute: memory-schema.sql                                              │
│                                                                          │
│  All tables created, ready for use                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 5: REGISTER AGENT                               │
│                                                                          │
│  Update: ~/.claude/agents/registry.json                                  │
│  Add agent to list with metadata                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 6: TEST                                         │
│                                                                          │
│  Send test email to verify:                                              │
│  • Inbox works                                                           │
│  • Memory database works                                                 │
│  • Identity loads correctly                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Memory Schema (Full SQL)

```sql
-- Agent Memory Schema
-- Designed for SQLite (local) with easy migration to PostgreSQL (cloud)

-- ============================================================================
-- CONTACTS: Who have I interacted with?
-- ============================================================================
CREATE TABLE IF NOT EXISTS contacts (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    organization TEXT,
    role TEXT,
    relationship TEXT,              -- 'customer', 'colleague', 'lead', 'vendor'
    first_contact_date DATE,
    last_contact_date DATE,
    total_interactions INTEGER DEFAULT 0,
    preferred_name TEXT,
    timezone TEXT,
    notes TEXT,
    metadata TEXT,                  -- JSON for extensibility
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- KNOWLEDGE: What facts do I know?
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    category TEXT NOT NULL,         -- 'company', 'person', 'project', 'product', 'general'
    subject TEXT NOT NULL,
    attribute TEXT,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'text', -- 'text', 'number', 'date', 'json', 'boolean'
    source TEXT,                    -- 'email', 'user_instruction', 'inference', 'web'
    source_ref TEXT,
    learned_date DATE,
    confidence REAL DEFAULT 1.0,
    superseded_by TEXT,
    is_current BOOLEAN DEFAULT TRUE,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TASKS: What am I working on?
-- ============================================================================
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',   -- 'active', 'waiting', 'completed', 'cancelled'
    priority TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    due_date DATE,
    due_time TEXT,
    waiting_on TEXT,
    waiting_since DATE,
    related_contact_id TEXT REFERENCES contacts(id),
    related_thread_id TEXT,
    related_email_id TEXT,
    tags TEXT,                      -- JSON array
    outcome TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- ============================================================================
-- INSTRUCTIONS: What are my standing orders?
-- ============================================================================
CREATE TABLE IF NOT EXISTS instructions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    instruction TEXT NOT NULL,
    scope TEXT DEFAULT 'global',    -- 'global', 'email', 'contact:[email]', 'topic:[name]'
    priority INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    given_by TEXT,
    given_date DATE,
    expires_at DATE,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SESSIONS: What happened in past work sessions?
-- ============================================================================
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    date DATE NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    summary TEXT NOT NULL,
    emails_processed INTEGER DEFAULT 0,
    emails_sent INTEGER DEFAULT 0,
    tasks_created TEXT,             -- JSON array
    tasks_completed TEXT,           -- JSON array
    key_learnings TEXT,
    open_items TEXT,
    decisions_made TEXT,
    errors_encountered TEXT,
    user_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- EMAIL_LOG: Record of all emails sent/received
-- ============================================================================
CREATE TABLE IF NOT EXISTS email_log (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    direction TEXT NOT NULL,        -- 'sent', 'received'
    agentmail_message_id TEXT,
    agentmail_thread_id TEXT,
    contact_id TEXT REFERENCES contacts(id),
    from_email TEXT NOT NULL,
    to_emails TEXT NOT NULL,        -- JSON array
    cc_emails TEXT,
    subject TEXT,
    body_preview TEXT,
    has_attachments BOOLEAN DEFAULT FALSE,
    attachment_names TEXT,          -- JSON array
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    response_sent BOOLEAN DEFAULT FALSE,
    response_message_id TEXT,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CONVERSATION_THREADS: Track logical conversation threads
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversation_threads (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    contact_id TEXT REFERENCES contacts(id),
    topic TEXT,
    agentmail_thread_id TEXT,
    last_message_id TEXT,           -- CRITICAL for reply threading
    last_activity TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_organization ON contacts(organization);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_subject ON knowledge(subject);
CREATE INDEX IF NOT EXISTS idx_knowledge_current ON knowledge(is_current);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_email_log_direction ON email_log(direction);
CREATE INDEX IF NOT EXISTS idx_email_log_thread ON email_log(agentmail_thread_id);
CREATE INDEX IF NOT EXISTS idx_threads_contact ON conversation_threads(contact_id);

-- ============================================================================
-- VIEWS
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_recent_contacts AS
SELECT * FROM contacts
WHERE last_contact_date >= date('now', '-30 days')
ORDER BY last_contact_date DESC;

CREATE VIEW IF NOT EXISTS v_overdue_tasks AS
SELECT * FROM tasks
WHERE status = 'active' AND due_date < date('now')
ORDER BY due_date ASC;

CREATE VIEW IF NOT EXISTS v_current_knowledge AS
SELECT * FROM knowledge
WHERE is_current = TRUE
ORDER BY learned_date DESC;

CREATE VIEW IF NOT EXISTS v_active_instructions AS
SELECT * FROM instructions
WHERE active = TRUE AND (expires_at IS NULL OR expires_at >= date('now'))
ORDER BY priority DESC;
```

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Create `~/.claude/skills/email-capability/` directory
- [ ] Write `SKILL.md` - main skill definition
- [ ] Write `memory-schema.sql` - database schema
- [ ] Write `memory-operations.md` - usage guide
- [ ] Write `identity.template.md` - template for new agents
- [ ] Create `~/.claude/agents/registry.json`
- [ ] Test: Skill file loads in Claude Code

### Phase 2: AgentMail Integration
- [ ] Sign up for AgentMail account
- [ ] Get API key
- [ ] Configure AgentMail MCP in `~/.claude.json`
- [ ] Create first inbox
- [ ] Test: Send email via MCP
- [ ] Test: Receive email via MCP
- [ ] Test: Reply with threading

### Phase 3: Memory Integration
- [ ] Configure SQLite MCP
- [ ] Create first `memory.db` with schema
- [ ] Test: Insert/query contacts
- [ ] Test: Insert/query knowledge
- [ ] Test: Task lifecycle
- [ ] Test: Session summaries

### Phase 4: First Agent
- [ ] Create `~/.claude/agents/default/identity.md`
- [ ] Initialize memory database
- [ ] Test full workflow:
  - Session start (load context)
  - Check inbox
  - Process email (update contacts, learn facts)
  - Reply to email
  - Session end (create summary)
- [ ] Verify memory persists across sessions

### Phase 5: Multi-Agent (Future)
- [ ] Design agent switching mechanism
- [ ] Implement registry-based agent lookup
- [ ] Test running multiple agents
- [ ] Consider cloud migration for shared access

---

## Usage Examples

### Invoking Email Capability

When any agent inherits this skill, they can:

```
User: "Check my inbox and reply to anything urgent"

Agent (internal):
1. Load identity from ~/.claude/agents/[me]/identity.md
2. mcp__agentmail__list_messages(inbox_id, unread_only=true)
3. For each message:
   - mcp__agentmail__get_message(inbox_id, message_id)
   - Query: SELECT * FROM contacts WHERE email = sender
   - Query: SELECT * FROM knowledge WHERE subject = sender_org
   - Assess urgency
   - If urgent: compose reply using context
   - mcp__agentmail__reply(inbox_id, message_id, body)
   - INSERT INTO email_log (...)
   - UPDATE contacts SET last_contact_date = ...
4. INSERT INTO sessions (summary, ...)
```

### Cross-Project Usage

Because the skill lives in `~/.claude/skills/` (global), any project can use it:

```bash
# Project A: Sales tool
cd ~/projects/sales-crm
claude "Use email-capability to send follow-up to john@acme.com"

# Project B: Support system
cd ~/projects/support-desk
claude "Use email-capability to check inbox for new tickets"

# Both use same skill, same memory, same identity
```

---

## Migration Path to Cloud

When ready to scale:

### Step 1: Export Data
```bash
sqlite3 ~/.claude/agents/default/memory.db .dump > backup.sql
```

### Step 2: Create Cloud Database
- Supabase: Create project, get connection string
- Or: Neon, Railway, PlanetScale

### Step 3: Adjust Schema
Minor changes for PostgreSQL:
- `datetime('now')` → `NOW()`
- `date('now')` → `CURRENT_DATE`
- `randomblob` → `gen_random_uuid()`

### Step 4: Import Data
```bash
psql $DATABASE_URL < backup_adjusted.sql
```

### Step 5: Update MCP Config
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://..."
      }
    }
  }
}
```

### Step 6: Test
- Verify all queries work
- Verify triggers work
- Test concurrent access (if multi-agent)

---

## Security Considerations

1. **API Keys**: Store in environment variables, not in files
2. **Email Content**: Memory stores body_preview (500 chars), not full emails
3. **Personal Data**: Contacts table stores only necessary info
4. **Credentials**: Never store passwords in knowledge table
5. **Backups**: Regular backups of memory.db (automated in cloud)

---

## Sources

- [AgentMail](https://agentmail.to/) - Email infrastructure for AI agents
- [AgentMail Docs](https://docs.agentmail.to/) - API reference
- [Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp) - MCP integration
- [SQLite MCP](https://github.com/anthropics/anthropic-tools) - Database MCP
- [Supabase](https://supabase.com/) - Cloud PostgreSQL option
