import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

interface ChatRequestBody {
  message: string;
  sessionId: string;
  userId?: string;
}

interface ChatApiResponse {
  reply: string;
  currentStep: string;
  nextStep: string;
  isComplete: boolean;
  collectedData?: Record<string, string | null>;
  rejectedItems?: {
    cities: string[];
    spots: string[];
    actions: string[];
    concepts: string[];
    outfits: string[];
    poses: string[];
    films: string[];
    cameras: string[];
  };
  suggestedOptions?: string[];
  sessionId: string;
  error?: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequestBody = await request.json();
    const { message, sessionId, userId } = body;

    if (!sessionId) {
      return NextResponse.json(
        { error: 'sessionId is required' },
        { status: 400 }
      );
    }

    // 백엔드 ChatAgent API 호출
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        sessionId,
        userId,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend chat error:', errorText);
      throw new Error(`Backend error: ${response.status}`);
    }

    const data: ChatApiResponse = await response.json();

    return NextResponse.json({
      reply: data.reply,
      currentStep: data.currentStep,
      nextStep: data.nextStep,
      isComplete: data.isComplete,
      collectedData: data.collectedData,
      rejectedItems: data.rejectedItems,
    });
  } catch (error) {
    console.error('Chat API error:', error);

    // 백엔드 연결 실패 시 폴백 응답
    return NextResponse.json({
      reply: '죄송해요, 잠시 연결에 문제가 있어요. 다시 시도해주세요. 🙏',
      currentStep: 'greeting',
      nextStep: 'greeting',
      isComplete: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}

// 세션 히스토리 조회 (GET /api/chat/[sessionId]/history)
export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const sessionId = url.searchParams.get('sessionId');

    if (!sessionId) {
      return NextResponse.json(
        { error: 'sessionId is required' },
        { status: 400 }
      );
    }

    // 백엔드 세션 히스토리 API 호출
    const response = await fetch(`${BACKEND_URL}/chat/${sessionId}/history`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // 세션이 없는 경우 빈 히스토리 반환
      if (response.status === 404) {
        return NextResponse.json({
          sessionId,
          history: [],
          currentStep: null,
          collectedData: null,
          isComplete: false,
        });
      }
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Get history error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
