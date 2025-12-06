import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { imageUrl, filename } = await request.json();

    console.log('[Download Image] Request:', { imageUrl: imageUrl?.slice(0, 100), filename });

    if (!imageUrl) {
      return NextResponse.json(
        { error: 'imageUrl is required' },
        { status: 400 }
      );
    }

    // 이미지 fetch (타임아웃 30초)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(imageUrl, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      },
    });

    clearTimeout(timeoutId);

    console.log('[Download Image] Fetch response:', { status: response.status, ok: response.ok });

    if (!response.ok) {
      console.error('[Download Image] Fetch failed:', response.status, response.statusText);
      return NextResponse.json(
        { error: `Failed to fetch image: ${response.status}` },
        { status: 502 }
      );
    }

    const arrayBuffer = await response.arrayBuffer();
    const contentType = response.headers.get('content-type') || 'image/png';

    console.log('[Download Image] Success:', { size: arrayBuffer.byteLength, contentType });

    // 이미지 응답 반환
    return new NextResponse(arrayBuffer, {
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `attachment; filename="${encodeURIComponent(filename || 'tripkit-image.png')}"`,
        'Content-Length': arrayBuffer.byteLength.toString(),
      },
    });
  } catch (error) {
    console.error('[Download Image] Error:', error);
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Failed to download image: ${message}` },
      { status: 500 }
    );
  }
}
