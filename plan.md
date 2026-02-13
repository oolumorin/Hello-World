# Executive Coach Agent — Plan

## 1. Overview

An AI-powered executive coach agent built on the **Google Agent Development Kit (ADK)** that helps a Senior IC stay accountable to goals, grow their career, and make better strategic decisions. The agent communicates primarily through **Slack** and uses **Obsidian** as both its knowledge base and persistent memory store.

---

## 2. Requirements Summary

| Dimension | Decision |
|---|---|
| **Framework** | Google ADK (Python) |
| **LLM** | Gemini 2.5 Flash (native to ADK) |
| **Communication** | Slack — DMs for coaching, dedicated `#coach-log` channel for summaries |
| **Context source** | Markdown files (goals, OKRs, career plans) |
| **Productivity tool** | Obsidian — full vault access (daily notes, tasks, projects, meeting notes, goals) |
| **Memory** | Obsidian-based — coaching history, decisions, and progress stored as `.md` files |
| **Check-in cadence** | Daily brief check-ins (morning + evening) + deep weekly review |
| **Coaching tone** | Adaptive — supportive by default, escalates directness when goals are consistently missed |
| **Career stage** | Senior IC targeting Staff/Principal or management transition |
| **Decision support** | Socratic coaching → structured frameworks (SWOT, decision matrix, pre-mortem) → decision journaling with outcome follow-up |
| **Deployment** | Local-first (with cloud deployment guide for later) |

---

## 3. Architecture

### 3.1 Multi-Agent Design

The system uses ADK's multi-agent orchestration with a **root coordinator agent** that delegates to specialized sub-agents.

```
                          ┌─────────────────────┐
                          │   CoordinatorAgent   │  (root LlmAgent)
                          │   Routes requests    │
                          │   to sub-agents      │
                          └─────────┬────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
   ┌──────────▼──────────┐ ┌───────▼────────┐ ┌──────────▼──────────┐
   │  AccountabilityAgent │ │ DecisionAgent  │ │   CareerCoachAgent  │
   │                      │ │                │ │                     │
   │  - Goal tracking     │ │ - Socratic Q's │ │ - Career planning   │
   │  - OKR check-ins     │ │ - Frameworks   │ │ - Skill gap analysis│
   │  - Daily/weekly      │ │ - Decision log │ │ - Promo readiness   │
   │    reviews           │ │ - Outcome      │ │ - Network strategy  │
   │  - Progress reports  │ │   follow-up    │ │ - IC vs mgmt path   │
   └──────────────────────┘ └────────────────┘ └─────────────────────┘
```

Each sub-agent has access to shared **tools** for Obsidian I/O, Slack messaging, and scheduling.

### 3.2 Tool Layer

| Tool | Purpose |
|---|---|
| `read_obsidian_note` | Read a note from the Obsidian vault by path |
| `write_obsidian_note` | Create or update a note in the Obsidian vault |
| `list_obsidian_notes` | List notes in a vault directory |
| `search_obsidian_vault` | Full-text search across the vault |
| `send_slack_dm` | Send a direct message to the user |
| `send_slack_channel` | Post to the `#coach-log` channel |
| `get_slack_history` | Read recent DM conversation history |
| `get_current_datetime` | Get current date/time for scheduling context |
| `log_decision` | Log a decision with context, options, rationale to Obsidian |
| `get_decision_log` | Retrieve past decisions for follow-up |

### 3.3 Obsidian Vault Structure

The agent expects (and will create if missing) the following directory structure within the vault:

```
vault/
├── coach/
│   ├── goals/
│   │   ├── quarterly-goals.md        # Current quarter OKRs
│   │   └── annual-goals.md           # Annual objectives
│   ├── check-ins/
│   │   ├── daily/
│   │   │   └── 2026-02-13.md         # Daily check-in logs
│   │   └── weekly/
│   │       └── 2026-W07.md           # Weekly review logs
│   ├── decisions/
│   │   └── 2026-02-13-decision.md    # Decision journal entries
│   ├── career/
│   │   ├── career-plan.md            # Career roadmap
│   │   └── skill-gaps.md             # Skill gap tracker
│   └── memory/
│       ├── coaching-context.md        # Running coaching context/patterns
│       └── progress-summary.md        # Aggregated progress over time
├── daily-notes/                       # User's existing daily notes
├── projects/                          # User's existing project notes
└── ...                                # Rest of user's vault
```

---

## 4. Features — Detailed Specification

### 4.1 Goal & OKR Tracking

**How it works:**
- User defines goals in `coach/goals/quarterly-goals.md` and `annual-goals.md` using a structured markdown format
- Agent reads these during check-ins and asks about progress on each key result
- Progress updates are logged to daily check-in notes
- Weekly reviews aggregate progress and surface goals at risk

**Goal markdown format:**
```markdown
## Q1 2026 OKRs

### Objective 1: Ship the new platform architecture
- [ ] KR1: Complete design doc review by Feb 28 (Progress: 60%)
- [ ] KR2: Migrate 3 services to new architecture by Mar 15 (Progress: 20%)
- [ ] KR3: Zero P0 incidents during migration (Progress: on-track)

### Objective 2: Build technical leadership visibility
- [ ] KR1: Publish 2 internal tech blog posts (Progress: 0/2)
- [ ] KR2: Present at 1 engineering all-hands (Progress: 0/1)
```

### 4.2 Daily Check-ins

**Morning check-in (configurable time, default 9:00 AM):**
- Reviews today's priorities from Obsidian daily note (if exists)
- Asks: "What are your top 3 priorities today?"
- Cross-references with OKRs to ensure alignment
- Posts summary to `#coach-log`

**Evening reflection (configurable time, default 5:30 PM):**
- Asks: "What did you accomplish today? Any blockers?"
- Logs accomplishments and blockers to daily check-in note
- Identifies patterns (e.g., same blocker recurring)

### 4.3 Weekly Review

**Triggered every Friday (configurable):**
- Aggregates the week's daily check-ins
- Reviews OKR progress (% change from last week)
- Highlights wins and areas of concern
- Prompts reflection: "What went well? What would you change?"
- Generates a structured weekly summary in `coach/check-ins/weekly/`
- Posts summary to `#coach-log`

### 4.4 Decision Support

**Three-phase approach:**

1. **Socratic Coaching** — When user raises a decision, agent asks probing questions:
   - "What outcome are you optimizing for?"
   - "What are the second-order effects?"
   - "What would you advise a peer in this situation?"
   - "What's the cost of reversing this decision?"

2. **Structured Frameworks** — After exploration, agent offers framework-based analysis:
   - **Decision Matrix**: Weighted criteria scoring
   - **Pre-mortem**: "Imagine this failed — why?"
   - **SWOT**: Strengths, weaknesses, opportunities, threats
   - **Reversibility check**: One-way door vs two-way door

3. **Decision Journal** — Agent logs every decision with:
   - Context and constraints
   - Options considered
   - Framework analysis
   - Final decision and rationale
   - Expected outcome and review date
   - **Outcome follow-up**: Agent revisits decisions at the review date and asks how it turned out, logging the actual outcome for pattern learning

### 4.5 Career Coaching

**Tailored for Senior IC → Staff/Principal or Management path:**

- **Career Plan**: Helps build and maintain a career roadmap in `coach/career/career-plan.md`
- **Skill Gap Analysis**: Identifies gaps between current skills and target role requirements
- **Promotion Readiness**: Tracks artifacts and evidence for promotion (design docs, impact metrics, leadership examples)
- **Networking Strategy**: Prompts regular relationship-building actions
- **IC vs Management**: Helps evaluate and clarify path preference through structured reflection

### 4.6 Adaptive Coaching Tone

The agent adjusts its communication style based on goal adherence:

| Adherence Level | Tone | Example |
|---|---|---|
| On-track (>80% of goals progressing) | Supportive, celebratory | "Great momentum on the migration! You're ahead of schedule on KR2." |
| At-risk (50-80%) | Encouraging but direct | "I notice the blog posts haven't started yet. What's blocking you? Let's find 2 hours this week." |
| Off-track (<50%) | Challenging, tough love | "We're 6 weeks in and KR1 is still at 20%. This pattern has shown up before. What needs to change right now?" |

---

## 5. Project Structure

```
executive-coach-agent/
├── pyproject.toml                     # Project config & dependencies
├── .env.example                       # Template for environment variables
├── README.md                          # Setup and usage instructions
│
├── executive_coach/                   # ADK agent package
│   ├── __init__.py                    # Exports root_agent
│   ├── agent.py                       # Root coordinator agent definition
│   │
│   ├── sub_agents/
│   │   ├── __init__.py
│   │   ├── accountability.py          # AccountabilityAgent
│   │   ├── decision.py                # DecisionAgent
│   │   └── career_coach.py            # CareerCoachAgent
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── obsidian.py                # Obsidian vault read/write/search tools
│   │   ├── slack.py                   # Slack DM and channel tools
│   │   └── utils.py                   # Date/time and utility tools
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── coordinator.py             # Coordinator system prompt
│   │   ├── accountability.py          # Accountability agent prompt
│   │   ├── decision.py                # Decision agent prompt
│   │   └── career_coach.py            # Career coach prompt
│   │
│   └── scheduler.py                   # APScheduler-based check-in scheduler
│
├── scripts/
│   ├── run_agent.py                   # Start the agent (interactive mode)
│   └── run_scheduler.py               # Start the scheduler for proactive check-ins
│
├── vault_template/                    # Template Obsidian vault structure
│   └── coach/
│       ├── goals/
│       │   ├── quarterly-goals.md
│       │   └── annual-goals.md
│       ├── check-ins/
│       │   ├── daily/.gitkeep
│       │   └── weekly/.gitkeep
│       ├── decisions/.gitkeep
│       ├── career/
│       │   ├── career-plan.md
│       │   └── skill-gaps.md
│       └── memory/
│           ├── coaching-context.md
│           └── progress-summary.md
│
└── tests/
    ├── __init__.py
    ├── test_tools_obsidian.py
    ├── test_tools_slack.py
    └── test_agents.py
```

---

## 6. Technology Stack

| Component | Technology |
|---|---|
| Agent framework | `google-adk` (latest) |
| LLM | Gemini 2.5 Flash via ADK |
| Slack integration | `slack-bolt` + `slack-sdk` |
| Scheduling | `APScheduler` (local cron-like scheduler) |
| Obsidian access | Direct filesystem I/O (pathlib) + full-text search |
| Python | 3.11+ |
| Package manager | `pip` with `pyproject.toml` |

---

## 7. Implementation Plan

### Phase 1: Foundation (Core Agent + Obsidian Tools)
1. Initialize project structure with `pyproject.toml` and dependencies
2. Implement Obsidian tools (`read_obsidian_note`, `write_obsidian_note`, `list_obsidian_notes`, `search_obsidian_vault`)
3. Create vault template with goal/check-in/decision markdown structures
4. Build the **CoordinatorAgent** (root agent with routing logic)
5. Build the **AccountabilityAgent** with goal reading and check-in prompts
6. Test locally via ADK CLI (`adk run`)

### Phase 2: Slack Integration
7. Implement Slack tools (`send_slack_dm`, `send_slack_channel`, `get_slack_history`)
8. Build Slack Bolt app that bridges Slack events → ADK agent
9. Handle Slack message events → agent invocation → Slack response
10. Test DM and channel interactions end-to-end

### Phase 3: Decision & Career Agents
11. Build the **DecisionAgent** with Socratic questioning + framework tools
12. Implement `log_decision` and `get_decision_log` tools
13. Build the **CareerCoachAgent** with career planning prompts
14. Test multi-agent routing (coordinator → sub-agents)

### Phase 4: Proactive Check-ins & Scheduler
15. Implement APScheduler-based scheduler for daily/weekly triggers
16. Wire scheduler → Slack DM delivery for morning/evening check-ins
17. Implement weekly review aggregation logic
18. Test scheduled check-in flow end-to-end

### Phase 5: Adaptive Tone & Memory
19. Implement goal adherence scoring (on-track / at-risk / off-track)
20. Build adaptive tone logic into agent prompts based on adherence
21. Implement coaching context memory (`coach/memory/coaching-context.md`)
22. Add decision outcome follow-up scheduling

---

## 8. Configuration

Environment variables (`.env`):

```bash
# Google AI
GOOGLE_API_KEY=your-gemini-api-key

# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_USER_ID=U12345678                    # Your Slack user ID for DMs
SLACK_CHANNEL_ID=C12345678                 # #coach-log channel ID

# Obsidian
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault

# Schedule (24h format)
MORNING_CHECKIN_TIME=09:00
EVENING_CHECKIN_TIME=17:30
WEEKLY_REVIEW_DAY=friday
WEEKLY_REVIEW_TIME=14:00

# Agent
COACHING_TONE=adaptive                      # adaptive | supportive | direct
```

---

## 9. Slack App Setup (Prerequisites)

1. Create a new Slack App at https://api.slack.com/apps
2. Enable **Socket Mode** (for local development)
3. Add Bot Token Scopes: `chat:write`, `im:history`, `im:read`, `im:write`, `channels:history`, `channels:read`
4. Subscribe to Events: `message.im`, `app_mention`
5. Install to workspace and copy tokens to `.env`

---

## 10. Future Enhancements (Post-MVP)

- **Hybrid memory**: Add SQLite for structured queries + analytics dashboards
- **Cloud deployment**: Cloud Run + Cloud Scheduler guide
- **Calendar integration**: Google Calendar for meeting prep and time-blocking
- **360 feedback**: Collect and synthesize peer feedback
- **Metrics dashboard**: Web UI for goal progress visualization
- **Voice check-ins**: Slack Huddles or audio message support
- **Multi-user**: Support coaching multiple team members
