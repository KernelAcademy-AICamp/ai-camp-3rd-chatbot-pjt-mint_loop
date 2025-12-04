# CLAUDE.md

This file provides comprehensive guidance to Claude Code when working with this repository.

---

## Project Overview

**Trip Kit** - AI-powered vibe-driven travel platform that curates emotional travel experiences through film aesthetics and hidden local spots.

**Tagline**: "You just book the ticket. We'll take care of your travel vibe."

**Core Philosophy**: NOT an efficiency-focused travel planner. Trip Kit designs complete aesthetic travel experiences by extracting user's emotional "vibe" and matching it to hidden local spots, film camera aesthetics, and complete creative direction.

---

## Project Structure

```
mintloop/
├── front/                      # Next.js 14 Frontend
│   ├── app/                    # App Router pages & API routes
│   │   ├── api/chat/          # Chat endpoint
│   │   ├── chat/              # Chat page
│   │   ├── concept/           # Concept selection page
│   │   └── destinations/      # Destinations page
│   ├── components/            # React components
│   │   ├── ui/               # Base UI components
│   │   ├── chat/             # Chat components
│   │   ├── landing/          # Landing page components
│   │   ├── layout/           # Header, Footer
│   │   ├── concept/          # Concept cards
│   │   └── destinations/     # Destination cards
│   └── lib/                   # Utilities, stores, types
│       ├── store/            # Zustand stores
│       ├── types/            # TypeScript types
│       ├── constants/        # Film stocks, concepts
│       └── utils/            # Utility functions
│
├── image-generation-agent/    # Python LangGraph Backend
│   ├── src/
│   │   ├── image_agent/      # LangGraph agent
│   │   │   ├── agent.py      # Main agent class
│   │   │   ├── nodes.py      # Workflow nodes
│   │   │   └── state.py      # State definitions
│   │   ├── mcp_servers/      # MCP servers
│   │   │   ├── image_server.py    # Image generation MCP
│   │   │   └── search_server.py   # Search MCP
│   │   └── config/           # Settings
│   ├── examples/             # Usage examples
│   └── tests/                # Python tests
│
├── docs/                      # Documentation
│   ├── PRD_TripKit_MVP.md    # Product requirements
│   ├── TRD_TripKit_MVP.md    # Technical requirements
│   ├── API_Documentation.md  # API specs
│   ├── AI_Integration_Guide.md
│   ├── Frontend_Design_Specification.md
│   └── claudecode-sub-agents.md  # Sub-agent guide (Korean)
│
└── .claude/                   # Claude Code configuration
    ├── CLAUDE.md             # This file
    ├── agents/               # Sub-agent configurations
    └── settings.local.json   # Local settings
```

---

## Technology Stack

### Frontend (`front/`)

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2+ | React framework with App Router |
| TypeScript | 5.0+ | Type safety |
| Tailwind CSS | 3.4+ | Styling |
| Zustand | 4.5+ | State management |
| React Query | 5.0+ | Data fetching & caching |
| Framer Motion | 11.0+ | Animations |
| Lucide React | 0.400+ | Icons |

### Backend (`image-generation-agent/`)

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Runtime |
| LangGraph | 0.6.4+ | Agent workflow orchestration |
| LangChain | 0.3.27+ | AI framework |
| FastMCP | 2.11+ | MCP server framework |
| langchain-mcp-adapters | 0.1.9+ | MCP integration |
| OpenAI | 1.0+ | GPT-4 & DALL-E 3 |
| Tavily | 0.3+ | Search API |
| structlog | 25.4+ | Structured logging |

### Future Integration

| Technology | Purpose | Status |
|------------|---------|--------|
| Supabase | Database, Auth, Storage, RLS | Post-MVP |
| Redis | Session caching | Post-MVP |

---

## Build & Development Commands

### Frontend Commands

```bash
cd front

# Install & Development
npm install              # Install dependencies
npm run dev              # Development server (localhost:3000)
npm run build            # Production build
npm run start            # Start production server

# Code Quality
npm run lint             # Run ESLint
npm run type-check       # TypeScript type checking (tsc --noEmit)
```

### Backend Commands

```bash
cd image-generation-agent

# Environment Setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run Services
python -m src.mcp_servers.search_server    # Start Search MCP server
python -m src.mcp_servers.image_server     # Start Image MCP server

# Docker (Alternative)
docker-compose up -d     # Start all services
docker-compose down      # Stop all services
docker-compose logs -f   # View logs

# Testing
pytest                   # Run all tests
pytest tests/test_agent.py -v   # Run agent tests
```

### Environment Setup

```bash
# .env file in project root
OPENAI_API_KEY="sk-..."        # Required: GPT-4 and DALL-E 3
TAVILY_API_KEY="..."           # Required: Search functionality
ANTHROPIC_API_KEY="..."        # Optional: Claude integration
```

---

## Sub-Agent System

This project uses specialized Claude Code sub-agents. Delegate tasks to appropriate agents:

| Agent | Specialization | Use For |
|-------|----------------|---------|
| `frontend-developer` | React, Next.js, TypeScript, Tailwind | UI components, pages, styling |
| `backend-developer` | Supabase, Python, MCP servers | Database, APIs, Python code |
| `langgraph-specialist` | LangGraph, StateGraph, workflows | AI workflows, state management |
| `test-engineer` | Jest, Pytest, Playwright | Tests, coverage |
| `documentation-specialist` | Technical writing, Mermaid | API docs, guides |
| `devops-engineer` | Docker, CI/CD, Vercel | Deployment, infrastructure |

### Sub-Agent Usage

```
Task: "Create a FilmAestheticCard component with vintage styling"
Agent: frontend-developer
Model: sonnet

Task: "Design LangGraph workflow for vibe extraction"
Agent: langgraph-specialist
Model: opus
```

See `.claude/agents/` for detailed configurations and `docs/claudecode-sub-agents.md` for comprehensive guide.

---

## Architecture Principles

### Vibe-Driven Design

1. **Emotional Preference Extraction**: Use empathetic, warm language in AI prompts
2. **Hidden Spot Curation**: Avoid mainstream tourist attractions; focus on local favorites
3. **Film Aesthetic Authenticity**: Generate images that look like real analog photography
4. **Complete Creative Direction**: Every recommendation includes location + outfit + camera + settings

### Three Aesthetic Concepts

| Concept | Korean | Description |
|---------|--------|-------------|
| Flâneur | 플라뇌르 | Urban wandering, literary aesthetic |
| Film Log | 필름 로그 | Vintage photography, analog feel |
| Midnight | 미드나잇 | Artistic time travel, bohemian |

### LangGraph Workflow Pattern

```
[User Input] → [Extract Keywords] → [Optimize Prompt] → [Generate Image] → [Output]
     ↓
State: { messages, user_prompt, extracted_keywords, optimized_prompt, generated_image_url, status }
```

---

## API Endpoints

### Frontend API Routes (`front/app/api/`)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/chat` | LangGraph vibe extraction conversation |
| `POST /api/recommendations/destinations` | GPT-4 vibe-matched destinations |
| `POST /api/recommendations/hidden-spots` | Local-favorite locations per destination |
| `POST /api/generate/image` | DALL-E 3 film-aesthetic preview |
| `POST /api/recommendations/styling` | Camera, film, outfit, props package |

### MCP Servers (`image-generation-agent/src/mcp_servers/`)

| Server | Default Port | Tools |
|--------|--------------|-------|
| Search MCP | 8050 | `extract_keywords`, `search_images` |
| Image MCP | 8051 | `optimize_prompt`, `generate_image` |

---

## Key Data Models

### User Preferences

```typescript
interface UserPreferences {
  mood: 'romantic' | 'adventurous' | 'nostalgic' | 'peaceful';
  aesthetic: 'urban' | 'nature' | 'vintage' | 'modern';
  duration: 'short' | 'medium' | 'long';
  interests: ('photography' | 'food' | 'art' | 'history' | 'nature')[];
  concept?: 'flaneur' | 'filmlog' | 'midnight';
}
```

### Image Generation State (Python)

```python
class ImageGenerationState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_prompt: str
    extracted_keywords: list[str]
    optimized_prompt: str
    generated_image_url: str | None
    image_metadata: dict | None
    status: Literal["pending", "processing", "completed", "failed"]
    error: str | None
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| API Response (chat) | <3s |
| Recommendations | <5s |
| Image Generation | <15s |
| Page Load | <3s |

---

## Code Style & Conventions

### TypeScript/React

- Use functional components with hooks
- Prefer `interface` over `type` for object shapes
- Use Tailwind CSS utility classes
- Component files: `PascalCase.tsx`
- Utility files: `camelCase.ts`
- Use Zustand for global state, React Query for server state

### Python

- Follow PEP 8 style guide
- Use type hints everywhere
- Use `structlog` for logging
- Use Pydantic for data validation
- Async-first approach with `asyncio`

### Git Conventions

```
<type>(<scope>): <subject>

Types: feat, fix, docs, refactor, test, chore
Scopes: front, agent, docs, api, ui, mcp
```

---

## Documentation Reference

| Document | Purpose |
|----------|---------|
| `docs/PRD_TripKit_MVP.md` | Product requirements, user stories |
| `docs/TRD_TripKit_MVP.md` | Technical architecture, API specs |
| `docs/API_Documentation.md` | REST API contracts |
| `docs/AI_Integration_Guide.md` | LangGraph setup, prompts |
| `docs/Frontend_Design_Specification.md` | UI/UX specifications |
| `docs/claudecode-sub-agents.md` | Sub-agent usage guide (Korean) |

---

## Important Notes

1. **Always read relevant documentation** before implementing features
2. **Use appropriate sub-agents** for specialized tasks
3. **Check existing patterns** in codebase before creating new ones
4. **Run lint/type-check** before committing
5. **Follow the vibe-driven design principles** - this is NOT a typical travel planner

---

**Last Updated**: 2025-12-04
