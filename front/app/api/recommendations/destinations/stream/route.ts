import { NextRequest } from 'next/server';
import type { UserPreferences, Concept } from '@/lib/types';

// Python 백엔드 API 서버 URL
const AGENT_API_URL = process.env.AGENT_API_URL || 'http://localhost:8000';

interface ImageGenerationContext {
  destination: string;
  additionalPrompt: string;
  filmStock: string;
  outfitStyle: string;
}

interface RecommendationRequest {
  preferences: UserPreferences;
  concept?: Concept;
  travelScene?: string;
  travelDestination?: string;
  imageGenerationContext?: ImageGenerationContext | null;
}

export async function POST(request: NextRequest) {
  try {
    const body: RecommendationRequest = await request.json();

    console.log('[Destinations Stream API] Forwarding to backend:', {
      mood: body.preferences?.mood,
      concept: body.concept,
      hasImageContext: !!body.imageGenerationContext,
    });

    // Python 백엔드 스트리밍 API 호출
    const response = await fetch(`${AGENT_API_URL}/recommendations/destinations/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = 'Backend API call failed';
      try {
        const errorData = JSON.parse(errorText);
        errorMessage = errorData.detail || errorData.error || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    // Backend SSE를 그대로 프록시 - ReadableStream으로 즉시 전달
    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            controller.enqueue(value);
          }
        } catch (error) {
          // 클라이언트가 연결을 끊은 경우 무시
          if ((error as Error).name !== 'AbortError') {
            console.error('[Destinations Stream API] Stream error:', error);
          }
        } finally {
          try {
            controller.close();
          } catch {
            // 이미 닫힌 경우 무시
          }
          reader.releaseLock();
        }
      },
      cancel() {
        // 클라이언트가 연결을 끊었을 때 호출됨
        console.log('[Destinations Stream API] Stream cancelled by client');
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
      },
    });
  } catch (error) {
    console.error('[Destinations Stream API] Error:', error);

    const rawMessage = error instanceof Error ? error.message : '';
    let userMessage = '여행지 추천 중 오류가 발생했습니다.';

    if (rawMessage.includes('ECONNREFUSED') || rawMessage.includes('fetch failed')) {
      userMessage = '추천 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.';
    }

    // SSE 형식으로 에러 반환
    const errorEvent = `data: ${JSON.stringify({ type: 'error', error: userMessage })}\n\n`;

    return new Response(errorEvent, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'X-Accel-Buffering': 'no',
      },
    });
  }
}
