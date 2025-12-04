# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Trip Kit (트립 키트)** - AI-powered vibe-driven travel platform that curates emotional travel experiences.

**Tagline**: "당신은 티켓만 끊으세요. 여행의 '분위기(Vibe)'는 우리가 챙겨드립니다."

**Core Philosophy**: This is NOT an efficiency-focused travel planner. Trip Kit designs complete aesthetic travel experiences by extracting user's emotional "vibe" and matching it to hidden local spots, film camera aesthetics, and complete creative direction.

**Current Status**: Documentation-only (pre-implementation). All files in `docs/` contain planning specs.

---

## Build & Development Commands

### When Implementation Begins (Next.js)
```bash
npm install          # Install dependencies
npm run dev          # Development server (localhost:3000)
npm run build        # Production build
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking (tsc --noEmit)
npm test             # Run Jest tests
npm run test:unit    # Unit tests only
npm run test:e2e     # Playwright E2E tests
```

### Environment Setup
```bash
# Required environment variables in .env
OPENAI_API_KEY="sk-..."        # GPT-4 and DALL-E 3
ANTHROPIC_API_KEY="..."        # Optional
```

---

## Architecture

### 3-Layer Design (Planned)
```
Client (Next.js 14+)  →  API Routes  →  AI Services
├── Vibe Chat              ├── /api/chat              ├── LangGraph (conversation state)
├── Concept Selector       ├── /api/recommendations   ├── GPT-4 (vibe matching)
└── Hidden Spot Gallery    └── /api/generate/image    └── DALL-E 3 (film aesthetic)
```

### Key Files (When Implementation Starts)
- `app/api/chat/route.ts` - LangGraph conversation endpoint
- `lib/langgraph/` - Conversation state graph
- `lib/ai/prompts/` - Prompt templates for GPT-4/DALL-E
- `lib/ai/services/` - AI service wrappers

### Technology Stack
- **Frontend**: Next.js 14.2+, TypeScript, Tailwind CSS, Zustand
- **AI/ML**: LangGraph, LangChain, OpenAI SDK (GPT-4, DALL-E 3)
- **State**: Session storage (no DB for MVP)

---

## Documentation Structure

```
docs/
├── PRD_TripKit_MVP.md       # Product requirements, user stories, success metrics
├── TRD_TripKit_MVP.md       # Technical architecture, API specs, data models
├── API_Documentation.md     # REST API contracts (5 endpoints)
└── AI_Integration_Guide.md  # LangGraph setup, prompt templates, DALL-E patterns
```

Cross-reference: PRD (what/why) → TRD (how) → API Docs (contracts) → AI Guide (implementation)

---

## Vibe-Driven Design Principles

When implementing features:

1. **Emotional Preference Extraction**: Use empathetic, warm language in AI prompts
2. **Hidden Spot Curation**: Avoid mainstream tourist attractions; focus on local favorites
3. **Film Aesthetic Authenticity**: Generate images that look like real analog photography (not filters)
4. **Complete Creative Direction**: Every recommendation includes location + outfit + camera + settings

### Three Aesthetic Concepts
- **플라뇌르 (Flâneur)**: Urban wandering, literary aesthetic
- **필름 로그 (Film Log)**: Vintage photography, analog feel
- **미드나잇 (Midnight)**: Artistic time travel, bohemian

### User Preference Schema
```typescript
interface UserPreferences {
  mood: 'romantic' | 'adventurous' | 'nostalgic' | 'peaceful';
  aesthetic: 'urban' | 'nature' | 'vintage' | 'modern';
  duration: 'short' | 'medium' | 'long';
  interests: ('photography' | 'food' | 'art' | 'history' | 'nature')[];
  concept?: 'flaneur' | 'filmlog' | 'midnight';
}
```

---

## AI Integration Patterns

### LangGraph Conversation Flow
```
init → mood → aesthetic → duration → interests → complete
```
Each node extracts one preference via GPT-4 and advances state.

### Prompt Template Pattern (from AI_Integration_Guide.md)
```typescript
// lib/ai/prompts/destination-recommendations.ts
export function buildVibeMatchedDestinationPrompt(preferences: UserPreferences): string {
  // Include mood description, aesthetic context, concept alignment
  // Request JSON output with matchReason explaining emotional fit
}
```

### Image Generation (DALL-E 3)
- Use `quality: 'hd'` and `style: 'natural'` for photorealistic film look
- Include film stock profile in prompt (Kodak ColorPlus, Portra, Fuji Superia, Ilford HP5)
- Specify grain texture, vignetting, and analog color shifts

---

## API Endpoints (Planned)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/chat` | LangGraph vibe extraction conversation |
| `POST /api/recommendations/destinations` | GPT-4 vibe-matched destinations |
| `POST /api/recommendations/hidden-spots` | Local-favorite locations per destination |
| `POST /api/generate/image` | DALL-E 3 film-aesthetic preview |
| `POST /api/recommendations/styling` | Camera, film, outfit, props package |

---

## Performance Targets

- API Response (chat): <3s
- Recommendations: <5s
- Image Generation: <15s
- Page Load: <3s

---

## Git Conventions

### Commit Format
```
<type>(<scope>): <subject>
```
**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
**Scopes**: `prd`, `trd`, `api`, `ai`, `ui`, `docs`
