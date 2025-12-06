'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { Download } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import type { ConceptData } from '@/lib/constants/concepts';

type ModalStatus = 'loading' | 'success' | 'error';

interface ImageGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  status: ModalStatus;
  concept: ConceptData;
  destination: string;
  filmStock: string;
  // Success data
  imageUrl?: string;
  optimizedPrompt?: string;
  // Error data
  errorMessage?: string;
  // Actions
  onRegenerate: () => void;
  onContinue: () => void;
}

export function ImageGenerationModal({
  isOpen,
  onClose,
  status,
  concept,
  destination,
  filmStock,
  imageUrl,
  optimizedPrompt,
  errorMessage,
  onRegenerate,
  onContinue,
}: ImageGenerationModalProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (!imageUrl) return;

    setIsDownloading(true);
    try {
      // 파일명 생성: tripkit_목적지_컨셉_타임스탬프.png
      const timestamp = new Date().toISOString().slice(0, 10);
      const sanitizedDestination = destination.replace(/[^a-zA-Z0-9가-힣]/g, '_');
      const filename = `tripkit_${sanitizedDestination}_${concept.id}_${timestamp}.png`;

      // API route를 통해 이미지 다운로드 (CORS 우회)
      const response = await fetch('/api/download-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imageUrl, filename }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Download API error:', errorData);
        throw new Error(errorData.error || 'Download failed');
      }

      const blob = await response.blob();
      console.log('Download blob:', { size: blob.size, type: blob.type });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('이미지 다운로드에 실패했습니다. 다시 시도해 주세요.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={status === 'loading' ? () => {} : onClose}
      size="full"
      showCloseButton={status !== 'loading'}
      closeOnOverlayClick={status !== 'loading'}
    >
      <div className="p-6 md:p-8">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <Badge variant="primary">{concept.nameKo}</Badge>
          <span className="text-sm text-gray-500">{destination}</span>
        </div>

        {/* Loading State */}
        {status === 'loading' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            {/* Animated Loader */}
            <div className="relative w-24 h-24 mx-auto mb-6">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-0 border-4 border-cream-200 border-t-sepia-600 rounded-full"
              />
              <div className="absolute inset-2 bg-cream-50 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-sepia-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" />
                </svg>
              </div>
            </div>

            <h3 className="text-xl font-serif text-gray-900 mb-2">
              이미지 생성 중...
            </h3>
            <p className="text-gray-500 mb-4">
              DALL-E 3가 <strong>{concept.nameKo}</strong> 감성의 여행 사진을 만들고 있어요
            </p>

            {/* Progress Animation */}
            <div className="max-w-xs mx-auto">
              <div className="h-2 bg-cream-100 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-sepia-400 to-sepia-600"
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{ duration: 15, ease: 'easeInOut' }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-2">
                약 10-15초 정도 소요됩니다
              </p>
            </div>

            {/* Film Stock Info */}
            <div className="mt-8 inline-flex items-center gap-2 px-4 py-2 bg-cream-50 rounded-full">
              <span className="text-sm text-gray-600">
                {filmStock} 필름 스타일 적용 중
              </span>
            </div>
          </motion.div>
        )}

        {/* Error State */}
        {status === 'error' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-8"
          >
            <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>

            <h3 className="text-xl font-serif text-gray-900 mb-2">
              이미지 생성에 실패했어요
            </h3>
            <p className="text-gray-500 mb-6 max-w-sm mx-auto">
              {errorMessage || '일시적인 오류가 발생했습니다. 다시 시도해 주세요.'}
            </p>

            <div className="flex justify-center gap-3">
              <Button variant="outline" onClick={onClose}>
                닫기
              </Button>
              <Button onClick={onRegenerate}>
                다시 시도하기
              </Button>
            </div>
          </motion.div>
        )}

        {/* Success State */}
        {status === 'success' && imageUrl && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {/* Generated Image */}
            <div className="relative aspect-square w-full max-w-lg mx-auto mb-6 rounded-xl overflow-hidden shadow-lg">
              <Image
                src={imageUrl}
                alt={`${destination} - ${concept.nameKo} 스타일`}
                fill
                className="object-cover"
                unoptimized
              />

              {/* Film Badge Overlay */}
              <div className="absolute bottom-3 left-3">
                <span className="px-3 py-1 bg-black/60 text-white text-sm rounded-full backdrop-blur-sm">
                  {filmStock}
                </span>
              </div>

              {/* Download Button Overlay */}
              <button
                onClick={handleDownload}
                disabled={isDownloading}
                className="absolute bottom-3 right-3 p-2 bg-black/60 hover:bg-black/80 text-white rounded-full backdrop-blur-sm transition-colors disabled:opacity-50"
                aria-label="이미지 다운로드"
              >
                {isDownloading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                  />
                ) : (
                  <Download className="w-5 h-5" />
                )}
              </button>
            </div>

            {/* Image Info */}
            <div className="text-center mb-6">
              <h3 className="text-xl font-serif text-gray-900 mb-2">
                이미지가 생성되었어요!
              </h3>
              <p className="text-gray-600">
                <strong>{destination}</strong>을(를) <strong>{concept.nameKo}</strong> 감성으로 담았습니다
              </p>
            </div>

            {/* Optimized Prompt (Collapsible) */}
            {optimizedPrompt && (
              <details className="mb-6 bg-cream-50 rounded-xl p-4">
                <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-sepia-600">
                  생성에 사용된 프롬프트 보기
                </summary>
                <p className="mt-3 text-xs text-gray-500 leading-relaxed">
                  {optimizedPrompt}
                </p>
              </details>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row justify-center gap-3">
              <Button variant="outline" onClick={onRegenerate}>
                다시 생성하기
              </Button>
              <Button
                variant="outline"
                onClick={handleDownload}
                disabled={isDownloading}
              >
                <Download className="w-4 h-4 mr-2" />
                {isDownloading ? '다운로드 중...' : '이미지 저장'}
              </Button>
              <Button onClick={onContinue}>
                여행지 추천 받기 →
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </Modal>
  );
}
