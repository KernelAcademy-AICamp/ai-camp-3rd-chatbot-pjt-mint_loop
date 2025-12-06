import { NextRequest, NextResponse } from 'next/server';

interface GenerateRequest {
  destination: string;
  concept: 'flaneur' | 'filmlog' | 'midnight';
  filmStock: string;
  colorPalette: string[];
  outfitStyle: string;
  additionalPrompt?: string;
}

// Python 백엔드 API 서버 URL
const AGENT_API_URL = process.env.AGENT_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body: GenerateRequest = await request.json();
    const { destination, concept, filmStock, colorPalette, outfitStyle, additionalPrompt } = body;

    // 입력 검증
    if (!destination || !concept) {
      return NextResponse.json(
        { error: 'INVALID_INPUT', message: 'destination and concept are required' },
        { status: 400 }
      );
    }

    console.log('[Generate API] Forwarding to Python backend:', { destination, concept, filmStock });

    // Python Agent API 호출
    const response = await fetch(`${AGENT_API_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        destination,
        concept,
        filmStock,
        colorPalette: colorPalette || [],
        outfitStyle: outfitStyle || '',
        additionalPrompt: additionalPrompt || '',
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Agent API call failed');
    }

    if (data.status === 'error') {
      throw new Error(data.error || 'Image generation failed');
    }

    console.log('[Generate API] Image generated successfully');

    return NextResponse.json({
      status: 'success',
      imageUrl: data.imageUrl,
      optimizedPrompt: data.optimizedPrompt,
      extractedKeywords: data.extractedKeywords || [],
      metadata: {
        concept,
        filmStock,
        destination,
        generatedAt: new Date().toISOString(),
        ...(data.metadata || {}),
      },
    });

  } catch (error) {
    console.error('[Generate API] Error:', error);

    // 사용자 친화적 에러 메시지 (민감한 정보 제거)
    const rawMessage = error instanceof Error ? error.message : '';
    let userMessage = '이미지 생성 중 오류가 발생했습니다. 다시 시도해 주세요.';

    if (rawMessage.includes('API key') || rawMessage.includes('401') || rawMessage.includes('invalid_api_key')) {
      userMessage = '이미지 생성 서비스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.';
    } else if (rawMessage.includes('ECONNREFUSED') || rawMessage.includes('fetch failed')) {
      userMessage = '서버 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.';
    } else if (rawMessage.includes('rate limit') || rawMessage.includes('429')) {
      userMessage = '요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.';
    } else if (rawMessage.includes('content_policy') || rawMessage.includes('safety')) {
      userMessage = '요청한 이미지를 생성할 수 없습니다. 다른 내용으로 시도해 주세요.';
    }

    return NextResponse.json(
      {
        status: 'error',
        error: 'GENERATION_FAILED',
        message: userMessage,
      },
      { status: 500 }
    );
  }
}
