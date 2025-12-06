'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { useVibeStore } from '@/lib/store/useVibeStore';
import { getConceptById } from '@/lib/constants/concepts';
import { ImageGenerationForm } from '@/components/generate/ImageGenerationForm';
import { ImageGenerationModal } from '@/components/generate/ImageGenerationModal';
import { Badge } from '@/components/ui/Badge';

interface GenerationResult {
  imageUrl: string;
  optimizedPrompt: string;
  destination: string;
  filmStock: string;
}

type ModalStatus = 'loading' | 'success' | 'error';

export default function GeneratePage() {
  const router = useRouter();
  const { selectedConcept, preferences, addGeneratedImage } = useVibeStore();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalStatus, setModalStatus] = useState<ModalStatus>('loading');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [currentFormData, setCurrentFormData] = useState<{
    destination: string;
    additionalPrompt: string;
    selectedFilm: string;
  } | null>(null);

  const concept = selectedConcept ? getConceptById(selectedConcept) : null;

  // 컨셉이 선택되지 않은 경우 리다이렉트
  useEffect(() => {
    if (!selectedConcept) {
      router.push('/concept');
    }
  }, [selectedConcept, router]);

  const handleGenerate = async (formData: {
    destination: string;
    additionalPrompt: string;
    selectedFilm: string;
  }) => {
    if (!concept) return;

    // 모달 열고 로딩 상태로 시작
    setCurrentFormData(formData);
    setIsModalOpen(true);
    setModalStatus('loading');
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          destination: formData.destination,
          concept: concept.id,
          filmStock: formData.selectedFilm,
          colorPalette: concept.colorPalette,
          outfitStyle: concept.outfitStyle,
          additionalPrompt: formData.additionalPrompt,
        }),
      });

      const data = await response.json();

      if (!response.ok || data.status === 'error') {
        throw new Error(data.message || 'Image generation failed');
      }

      const generationResult = {
        imageUrl: data.imageUrl,
        optimizedPrompt: data.optimizedPrompt,
        destination: formData.destination,
        filmStock: formData.selectedFilm,
      };

      setResult(generationResult);
      setModalStatus('success');

      // Store에 생성된 이미지 저장
      addGeneratedImage(formData.destination, data.imageUrl);
    } catch (err) {
      console.error('Generation error:', err);
      setError(
        err instanceof Error
          ? err.message
          : 'An error occurred while generating the image'
      );
      setModalStatus('error');
    }
  };

  const handleRegenerate = () => {
    if (currentFormData) {
      handleGenerate(currentFormData);
    }
  };

  const handleContinue = () => {
    setIsModalOpen(false);
    router.push('/destinations');
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  if (!concept) {
    return (
      <div className="min-h-screen bg-cream-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">컨셉을 먼저 선택해주세요</p>
          <Link href="/concept" className="text-sepia-600 hover:underline">
            컨셉 선택하러 가기 →
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream-50">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur-md border-b border-cream-200">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-serif text-xl text-gray-900">
                여행 이미지 생성
              </h1>
              <p className="text-sm text-gray-500">
                {concept.nameKo} 감성으로 여행 사진 미리보기
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="primary">{concept.nameKo}</Badge>
              {preferences.mood && (
                <Badge variant="secondary" className="hidden sm:inline-flex">
                  {preferences.mood}
                </Badge>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Intro */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h2 className="font-serif text-2xl md:text-3xl text-gray-900 mb-3">
            당신의 여행을 미리 만나보세요
          </h2>
          {preferences.travelScene ? (
            <div className="space-y-2">
              <p className="text-gray-600 max-w-lg mx-auto">
                대화에서 말씀하신 <strong>&ldquo;{preferences.travelScene}&rdquo;</strong>를
                <br />
                <strong>{concept.nameKo}</strong> 감성으로 그려드릴게요!
              </p>
              <p className="text-sm text-sepia-600">
                아래에서 내용을 수정하거나 바로 생성할 수 있어요.
              </p>
            </div>
          ) : (
            <p className="text-gray-600 max-w-lg mx-auto">
              여행지를 입력하면 <strong>{concept.nameKo}</strong> 감성의
              {' '}<strong>{concept.recommendedFilms[0]}</strong> 필름으로 촬영한 듯한
              여행 사진을 생성해 드려요.
            </p>
          )}
        </motion.div>

        {/* 입력 폼 - 항상 표시 */}
        <ImageGenerationForm
          concept={concept}
          onGenerate={handleGenerate}
          isLoading={isModalOpen && modalStatus === 'loading'}
          initialDestination={preferences.travelDestination || ''}
          initialAdditionalPrompt={preferences.travelScene || ''}
        />

        {/* 이전 생성 결과 미리보기 (모달 닫힌 후) */}
        {result && !isModalOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 p-4 bg-white rounded-2xl border border-cream-200 shadow-sm"
          >
            <div className="flex items-center gap-4">
              <div className="relative w-20 h-20 rounded-lg overflow-hidden flex-shrink-0">
                <Image
                  src={result.imageUrl}
                  alt="Generated"
                  fill
                  className="object-cover"
                  unoptimized
                />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">
                  마지막 생성: <strong>{result.destination}</strong>
                </p>
                <p className="text-xs text-gray-400">{result.filmStock}</p>
              </div>
              <button
                onClick={() => setIsModalOpen(true)}
                className="text-sepia-600 text-sm hover:underline"
              >
                다시 보기
              </button>
            </div>
          </motion.div>
        )}

        {/* 네비게이션 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center mt-8"
        >
          <Link
            href="/concept"
            className="text-sm text-gray-500 hover:text-sepia-600 transition-colors"
          >
            ← 컨셉 다시 선택하기
          </Link>
        </motion.div>
      </main>

      {/* Image Generation Modal */}
      {currentFormData && (
        <ImageGenerationModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          status={modalStatus}
          concept={concept}
          destination={currentFormData.destination}
          filmStock={currentFormData.selectedFilm}
          imageUrl={result?.imageUrl}
          optimizedPrompt={result?.optimizedPrompt}
          errorMessage={error || undefined}
          onRegenerate={handleRegenerate}
          onContinue={handleContinue}
        />
      )}
    </div>
  );
}
