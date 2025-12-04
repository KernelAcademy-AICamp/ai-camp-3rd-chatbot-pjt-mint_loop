# TripKit Sub-Agent System Guide

**"실무에서 검증된 Claude Code Sub-Agent 활용 가이드"**

---

## 📋 Overview

이 디렉토리는 TripKit 프로젝트의 **Claude Code Sub-Agent** 설정 파일을 포함합니다.
각 Sub-Agent는 특정 도메인에 특화되어 있으며, Task tool을 통해 독립적으로 작업을 수행합니다.

### Sub-Agent의 장점

1. **전문화**: 각 에이전트가 특정 영역의 전문가
2. **병렬 처리**: 여러 작업을 동시에 진행 가능
3. **컨텍스트 분리**: 각 에이전트가 독립적인 컨텍스트 보유
4. **품질 향상**: 전문화된 지식으로 더 나은 결과
5. **유지보수성**: 역할이 명확하여 관리 용이

---

## 🤖 Available Sub-Agents

### 1. Frontend Developer
**파일**: `frontend-developer.md`
**전문 분야**: React, Next.js, TypeScript, Tailwind CSS, Zustand

**주요 책임**:
- React 컴포넌트 개발
- TypeScript 타입 정의
- Zustand 상태 관리
- Tailwind CSS 스타일링
- API 통합
- 접근성 및 반응형 디자인

**사용 예시**:
```
// 메인 Claude에서 호출
Task: "Create a FilmAestheticCard component that displays film stock information with vintage styling"
Agent: frontend-developer
Model: sonnet  # 빠른 작업은 sonnet
```

**적합한 작업**:
- 새 컴포넌트 생성
- 기존 컴포넌트 리팩토링
- 상태 관리 로직 구현
- UI/UX 개선
- 타입 정의

---

### 2. Backend Developer
**파일**: `backend-developer.md`
**전문 분야**: Supabase, Python, LangGraph, MCP Servers

**주요 책임**:
- Supabase 스키마 설계
- RLS 정책 설정
- Python AI 에이전트 개발
- MCP 서버 구축
- API 엔드포인트 구현

**사용 예시**:
```
Task: "Create Supabase migration for storing user travel vibes with RLS policies"
Agent: backend-developer
Model: sonnet
```

**적합한 작업**:
- 데이터베이스 스키마 설계
- Python 비즈니스 로직 구현
- Supabase 통합
- MCP 서버 개발
- API 엔드포인트 구현

---

### 3. LangGraph Specialist
**파일**: `langgraph-specialist.md`
**전문 분야**: LangGraph, StateGraph, Multi-Agent Systems

**주요 책임**:
- LangGraph 워크플로우 설계
- State schema 정의
- Node/Edge 구현
- Conditional routing
- MCP 통합

**사용 예시**:
```
Task: "Design a LangGraph workflow for vibe extraction with 5-step conversation flow"
Agent: langgraph-specialist
Model: sonnet  # 복잡한 로직은 opus도 고려
```

**적합한 작업**:
- AI 워크플로우 아키텍처
- 복잡한 상태 관리
- Multi-agent orchestration
- Prompt engineering

---

### 4. Test Engineer
**파일**: `test-engineer.md`
**전문 분야**: Jest, Pytest, React Testing Library, Playwright

**주요 책임**:
- 단위 테스트 작성
- 통합 테스트 구현
- E2E 테스트 시나리오
- 테스트 커버리지 관리
- CI/CD 테스트 설정

**사용 예시**:
```
Task: "Write comprehensive tests for the VibeExtractionAgent including unit and integration tests"
Agent: test-engineer
Model: haiku  # 테스트 코드는 haiku로 충분
```

**적합한 작업**:
- 컴포넌트 테스트
- API 테스트
- 워크플로우 테스트
- E2E 시나리오
- 회귀 테스트

---

### 5. Documentation Specialist
**파일**: `documentation-specialist.md`
**전문 분야**: Technical Writing, API Documentation, Mermaid Diagrams

**주요 책임**:
- API 문서 작성
- 아키텍처 문서
- 사용자 가이드
- README, CHANGELOG
- Mermaid 다이어그램

**사용 예시**:
```
Task: "Create comprehensive API documentation for the new /api/recommendations/hidden-spots endpoint"
Agent: documentation-specialist
Model: haiku
```

**적합한 작업**:
- API 엔드포인트 문서화
- 아키텍처 다이어그램
- 사용자 가이드 작성
- 코드 주석 개선

---

### 6. DevOps Engineer
**파일**: `devops-engineer.md`
**전문 분야**: Docker, GitHub Actions, Vercel, CI/CD

**주요 책임**:
- Docker 컨테이너화
- CI/CD 파이프라인
- Vercel 배포 설정
- 환경변수 관리
- 모니터링 설정

**사용 예시**:
```
Task: "Setup GitHub Actions workflow for running tests and deploying to Vercel on merge to main"
Agent: devops-engineer
Model: sonnet
```

**적합한 작업**:
- CI/CD 구성
- 배포 자동화
- Docker 설정
- 환경 설정
- 모니터링 통합

---

## 🎯 Sub-Agent 사용 패턴

### Pattern 1: Single Agent for Specific Task

가장 기본적인 패턴입니다. 명확한 작업을 특정 에이전트에게 위임합니다.

```
User: "Create a new DestinationCard component for displaying travel recommendations"

Main Claude:
┌─────────────────────────────────────────┐
│ 1. 요구사항 분석                           │
│ 2. frontend-developer에게 위임 결정        │
│ 3. Task tool 호출                        │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Frontend Developer Sub-Agent             │
│ - 컴포넌트 구조 설계                       │
│ - TypeScript 타입 정의                    │
│ - Tailwind 스타일링                       │
│ - 접근성 속성 추가                         │
│ - Lint 검증                              │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Main Claude                              │
│ - 결과 확인 및 사용자에게 전달              │
└─────────────────────────────────────────┘
```

### Pattern 2: Sequential Agent Chain

여러 에이전트가 순차적으로 작업하는 패턴입니다.

```
User: "Implement a new feature: AI-generated travel journal entries"

Main Claude → backend-developer → frontend-developer → test-engineer → documentation-specialist
      ↓              ↓                  ↓                  ↓                    ↓
   Plan        API endpoint        UI component        Test cases        API docs
```

**Example Code**:
```javascript
// Main Claude internal logic (conceptual)
const tasks = [
  { agent: 'backend-developer', task: 'Create journal entry API in Supabase' },
  { agent: 'frontend-developer', task: 'Create JournalEntry component' },
  { agent: 'test-engineer', task: 'Write tests for journal feature' },
  { agent: 'documentation-specialist', task: 'Document journal API' }
];

for (const { agent, task } of tasks) {
  await Task({
    subagent_type: agent,
    prompt: task,
    model: 'sonnet'
  });
}
```

### Pattern 3: Parallel Agent Execution

독립적인 작업들을 병렬로 실행하는 패턴입니다.

```
User: "Prepare for production launch: tests, docs, deployment"

Main Claude
     ├─→ test-engineer (Run all tests)
     ├─→ documentation-specialist (Update README, CHANGELOG)
     └─→ devops-engineer (Setup CI/CD, deployment)

모두 완료 후 결과 취합
```

**SuperClaude 사용 예시**:
```
// 병렬 실행 명령 (SuperClaude)
User: "에이전트들을 병렬로 실행해줘: 테스트 실행, 문서 업데이트, CI/CD 설정"

Main Claude will send single message with multiple Task tool calls:
- Task(test-engineer, "Run comprehensive test suite")
- Task(documentation-specialist, "Update README and CHANGELOG")
- Task(devops-engineer, "Setup GitHub Actions CI/CD")
```

### Pattern 4: Review & Iterate

에이전트가 작업을 수행하고, 다른 에이전트가 리뷰하는 패턴입니다.

```
frontend-developer → test-engineer (review & add tests)
      ↓                      ↓
   Component             Test results
      ↓                      ↓
      └──────→ 필요시 재작업 ←──────┘
```

### Pattern 5: Coordinated Feature Development

완전한 기능을 여러 에이전트가 협력하여 개발하는 패턴입니다.

```
Feature: "Hidden Spot Discovery with Image Generation"

1. langgraph-specialist
   - Design workflow (search → recommend → generate image)

2. backend-developer
   - Implement Supabase schema
   - Create MCP server for spot search

3. frontend-developer
   - Build SpotDiscovery component
   - Integrate with backend API

4. test-engineer
   - Unit tests for workflow nodes
   - E2E test for full feature

5. documentation-specialist
   - API documentation
   - User guide

6. devops-engineer
   - Add to CI/CD pipeline
   - Performance monitoring
```

---

## 💡 Best Practices

### 1. 명확한 작업 정의

**Good**:
```
Task: "Create a ConceptCard component that displays the three travel concepts (Flâneur, Film Log, Midnight) with hover effects and selection state management"
Agent: frontend-developer
```

**Bad**:
```
Task: "Make the concept thing"
Agent: frontend-developer
```

### 2. 적절한 모델 선택

- **Haiku**: 단순 반복 작업 (테스트 작성, 문서 업데이트)
- **Sonnet**: 일반적인 개발 작업 (컴포넌트 구현, API 개발)
- **Opus**: 복잡한 아키텍처 설계 (LangGraph 워크플로우, 시스템 설계)

### 3. 컨텍스트 제공

에이전트에게 충분한 컨텍스트를 제공하세요:

```
Task: "Create a HiddenSpotCard component.
Reference: See TravelVibeCard for similar design patterns.
This component will display hidden local spots with:
- Name, address, description
- Photography tips (bullet list)
- Best time to visit
- Film stock recommendations
Style: Vintage aesthetic matching Film Log concept"

Agent: frontend-developer
```

### 4. 에이전트 간 의존성 관리

순차적 작업이 필요한 경우 명확히 하세요:

```
// Step 1
Task: "Create Supabase schema for hidden_spots table"
Agent: backend-developer

// Wait for completion, then Step 2
Task: "Create TypeScript types from the hidden_spots Supabase schema"
Agent: frontend-developer
```

### 5. 결과 검증

에이전트 작업 후 항상 결과를 확인하세요:

```
// After agent completes
Main Claude should:
1. Read generated files
2. Run lint/type-check
3. Verify tests pass
4. Confirm with user
```

---

## 🚫 Anti-Patterns (피해야 할 패턴)

### ❌ 너무 모호한 작업
```
Bad: "Fix the app"
Good: "Fix TypeScript type error in useChatStore.ts:45 where Message type is incompatible"
```

### ❌ 잘못된 에이전트 선택
```
Bad: Task: "Write Supabase migration" → frontend-developer
Good: Task: "Write Supabase migration" → backend-developer
```

### ❌ 과도한 작업 범위
```
Bad: "Implement entire vibe extraction feature from scratch"
Good: Split into multiple tasks:
  1. "Design LangGraph workflow" → langgraph-specialist
  2. "Implement conversation nodes" → backend-developer
  3. "Create chat UI" → frontend-developer
```

### ❌ 의존성 무시
```
Bad: 병렬 실행
  - frontend: "Create component using VibeName type"
  - backend: "Define VibeName type"

Good: 순차 실행
  1. backend: "Define VibeName type"
  2. frontend: "Create component using VibeName type"
```

---

## 📊 Performance Tips

### 1. 적절한 병렬화

독립적인 작업은 병렬로 실행:

```bash
# 병렬 가능한 작업들
- Frontend 컴포넌트 A 개발
- Frontend 컴포넌트 B 개발
- Backend API 엔드포인트 구현
- 문서 작성

→ 모두 동시에 Task tool로 실행
```

### 2. 모델 선택 최적화

| 작업 복잡도 | 모델 | 예상 시간 | 비용 |
|------------|------|----------|------|
| 단순 반복 | Haiku | ~30s | $ |
| 일반 개발 | Sonnet | ~60s | $$ |
| 복잡한 설계 | Opus | ~90s | $$$ |

### 3. Resume 기능 활용

이전 에이전트 세션을 재개할 수 있습니다:

```javascript
// 첫 번째 호출
const agentId1 = await Task({
  subagent_type: 'frontend-developer',
  prompt: 'Create VibeCard component'
});

// 나중에 같은 컨텍스트로 계속
await Task({
  subagent_type: 'frontend-developer',
  prompt: 'Add animation to the VibeCard',
  resume: agentId1  // 이전 컨텍스트 유지
});
```

---

## 🎓 Learning Path

### Beginner

1. **Single Agent 사용 연습**
   - 간단한 컴포넌트 생성
   - 테스트 작성
   - 문서 업데이트

2. **적절한 에이전트 선택 연습**
   - 각 에이전트의 전문 분야 이해
   - 작업과 에이전트 매칭

### Intermediate

3. **Sequential Chain 구현**
   - 여러 에이전트 순차 실행
   - 의존성 관리
   - 결과 검증

4. **Parallel Execution**
   - 병렬 가능한 작업 식별
   - 병렬 실행 구현
   - 결과 취합

### Advanced

5. **Complex Feature Development**
   - 전체 기능을 에이전트 팀으로 개발
   - 에이전트 간 협업 조율
   - Review & Iterate 패턴 활용

6. **Custom Agent 개발**
   - 프로젝트 특화 에이전트 생성
   - 새로운 전문 분야 추가

---

## 📚 References

- **Claude Code Documentation**: [claude.ai/claude-code](https://claude.ai/claude-code)
- **Task Tool Reference**: SuperClaude COMMANDS.md
- **Multi-Agent Patterns**: SuperClaude ORCHESTRATOR.md

---

## 🤝 Contributing

새로운 Sub-Agent를 추가하려면:

1. `.claude/agents/` 디렉토리에 `{agent-name}.md` 파일 생성
2. 기존 에이전트 파일을 템플릿으로 사용
3. 다음 섹션 포함:
   - Role & Responsibilities
   - Tools Available
   - Expertise
   - Work Pattern
   - Example Usage
   - Quality Standards
   - Do Not (제외 사항)

4. 이 README.md 업데이트 (Available Sub-Agents 섹션)

---

**Last Updated**: 2025-12-04
**Maintained By**: TripKit Development Team
