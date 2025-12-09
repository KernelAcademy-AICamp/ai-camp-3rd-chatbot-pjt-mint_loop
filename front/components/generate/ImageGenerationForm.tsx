'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import type { ConceptData } from '@/lib/constants/concepts';
import type { TripKitProfile } from '@/lib/types';

interface ImageGenerationFormProps {
  concept: ConceptData;
  onGenerate: (data: {
    destination: string;
    additionalPrompt: string;
    selectedFilm: string;
  }) => void;
  isLoading: boolean;
  // Chat에서 전달받은 초기값
  initialDestination?: string;
  initialAdditionalPrompt?: string;
  initialFilm?: string;
  // 대화에서 수집한 전체 프로필
  tripKitProfile?: Partial<TripKitProfile>;
}

export function ImageGenerationForm({
  concept,
  onGenerate,
  isLoading,
  initialDestination = '',
  initialAdditionalPrompt = '',
  initialFilm,
  tripKitProfile,
}: ImageGenerationFormProps) {
  const [destination, setDestination] = useState(initialDestination);
  const [additionalPrompt, setAdditionalPrompt] = useState(initialAdditionalPrompt);
  // initialFilm이 concept.recommendedFilms에 포함되어 있으면 사용, 아니면 첫 번째 필름 사용
  const defaultFilm = initialFilm && concept.recommendedFilms.includes(initialFilm)
    ? initialFilm
    : concept.recommendedFilms[0];
  const [selectedFilm, setSelectedFilm] = useState(defaultFilm);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (destination.trim()) {
      onGenerate({
        destination: destination.trim(),
        additionalPrompt: additionalPrompt.trim(),
        selectedFilm,
      });
    }
  };

  const placeholderExamples: Record<string, string> = {
    flaneur: '예: 파리 몽마르트르의 카페 테라스',
    filmlog: '예: 제주도 협재 해변의 석양',
    midnight: '예: 뉴욕 그리니치 빌리지의 재즈 클럽',
    pastoral: '예: 프로방스 라벤더 들판의 오솔길',
    noir: '예: 홍콩 네온 불빛 아래 골목길',
    seaside: '예: 포르투갈 나자레 해안의 파도',
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-cream-200 p-6 shadow-sm"
      onSubmit={handleSubmit}
    >
      {/* 컨셉 정보 및 대화에서 수집한 정보 통합 표시 */}
      <div className="mb-6 pb-6 border-b border-cream-100">
        <div className="flex items-center gap-3 mb-3">
          <Badge variant="primary">{concept.nameKo}</Badge>
          <span className="text-sm text-gray-500 italic">&ldquo;{concept.tagline}&rdquo;</span>
        </div>
        <p className="text-sm text-gray-600 mb-4">{concept.description}</p>

        {/* 대화에서 수집한 정보 (tripKitProfile이 있을 때만 표시) */}
        {tripKitProfile && (tripKitProfile.city || tripKitProfile.spotName || tripKitProfile.mainAction) && (
          <div className="mt-4 pt-4 border-t border-cream-100">
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <span className="text-sepia-500" role="img" aria-label="star">✦</span>
              대화에서 수집한 정보
            </h4>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm bg-cream-50 p-3 rounded-lg">
              {tripKitProfile.city && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 min-w-[3rem]">도시:</span>
                  <span className="text-gray-800">{tripKitProfile.city}</span>
                </div>
              )}
              {tripKitProfile.spotName && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 min-w-[3rem]">장소:</span>
                  <span className="text-gray-800">{tripKitProfile.spotName}</span>
                </div>
              )}
              {tripKitProfile.mainAction && (
                <div className="flex items-center gap-2 col-span-2">
                  <span className="text-gray-500 min-w-[3rem]">장면:</span>
                  <span className="text-gray-800">{tripKitProfile.mainAction}</span>
                </div>
              )}
              {tripKitProfile.outfitStyle && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 min-w-[3rem]">의상:</span>
                  <span className="text-gray-800">{tripKitProfile.outfitStyle}</span>
                </div>
              )}
              {tripKitProfile.posePreference && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 min-w-[3rem]">포즈:</span>
                  <span className="text-gray-800">{tripKitProfile.posePreference}</span>
                </div>
              )}
              {tripKitProfile.filmType && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 min-w-[3rem]">필름:</span>
                  <span className="text-gray-800">{tripKitProfile.filmType}</span>
                </div>
              )}
              {tripKitProfile.cameraModel && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 min-w-[3rem]">카메라:</span>
                  <span className="text-gray-800">{tripKitProfile.cameraModel}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 여행지 입력 */}
      <div className="mb-5">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          어디로 여행하시나요? *
        </label>
        <Input
          type="text"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          placeholder={placeholderExamples[concept.id]}
          disabled={isLoading}
          className="w-full"
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          구체적인 장소를 입력할수록 더 멋진 이미지가 생성됩니다
        </p>
      </div>

      {/* 추가 프롬프트 (옵션) */}
      <div className="mb-5">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          추가 묘사 (선택)
        </label>
        <textarea
          value={additionalPrompt}
          onChange={(e) => setAdditionalPrompt(e.target.value)}
          placeholder="예: 해질녘에 혼자 걷고 있는 모습, 카페에서 책을 읽는 순간..."
          disabled={isLoading}
          className="w-full px-4 py-3 rounded-xl border border-cream-200 focus:border-sepia-400 focus:ring-2 focus:ring-sepia-100 transition-all resize-none"
          rows={3}
        />
      </div>

      {/* 필름 스톡 선택 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          필름 선택
        </label>
        <div className="flex flex-wrap gap-2">
          {concept.recommendedFilms.map((film) => (
            <button
              key={film}
              type="button"
              onClick={() => setSelectedFilm(film)}
              disabled={isLoading}
              className={`px-4 py-2 rounded-full text-sm transition-all ${selectedFilm === film
                ? 'bg-sepia-500 text-white shadow-md'
                : 'bg-cream-100 text-gray-700 hover:bg-cream-200'
                }`}
            >
              {film}
            </button>
          ))}
        </div>
      </div>

      {/* 필름 스타일 미리보기 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <span role="img" aria-label="film">🎞️</span> {concept.filmType} 필름 스타일
        </label>
        <p className="text-sm text-gray-600 bg-cream-50 p-3 rounded-lg border border-cream-200">
          {concept.filmStyleDescription}
        </p>
      </div>

      {/* 생성 버튼 */}
      <Button
        type="submit"
        size="lg"
        className="w-full"
        disabled={!destination.trim() || isLoading}
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            이미지 생성 중...
          </span>
        ) : (
          '여행 이미지 생성하기'
        )}
      </Button>

      {isLoading && (
        <p className="text-center text-sm text-gray-500 mt-3">
          {concept.nameKo} 감성의 여행 사진을 만들고 있어요...
        </p>
      )}
    </motion.form>
  );
}
