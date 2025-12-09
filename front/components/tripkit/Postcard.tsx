'use client';

import { motion } from 'framer-motion';
import type { TripKitProfile } from '@/lib/types';
import type { ConceptData } from '@/lib/constants/concepts';

interface PostcardProps {
  profile: TripKitProfile;
  concept: ConceptData | null;
  isVisible: boolean;
}

export function Postcard({ profile, concept, isVisible }: PostcardProps) {
  // 컨셉에서 vibe keywords 가져오기 또는 기본값 사용
  const vibeKeywords = concept?.keywords.slice(0, 3) || ['aesthetic', 'film', 'travel'];

  // 컨셉 이름 (한글)
  const conceptName = concept?.nameKo || getConceptNameKo(profile.conceptId) || '플라뇌르';

  // 필름 타입 - profile에서 우선, 없으면 concept의 추천 필름 사용
  const filmStock = profile.filmType || concept?.recommendedFilms?.[0] || 'Kodak Portra 400';

  // 도시와 장소
  const city = profile.city || '당신만의 도시';
  const spotName = profile.spotName || '특별한 장소';
  const mainAction = profile.mainAction || '자유롭게 거닐며 순간을 담는';

  return (
    <motion.div
      className="w-full max-w-sm mx-auto px-4"
      initial={{ opacity: 0, y: 60, scale: 0.9 }}
      animate={isVisible ? { opacity: 1, y: 0, scale: 1 } : { opacity: 0, y: 60, scale: 0.9 }}
      transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
    >
      <div className="relative bg-white rounded-2xl shadow-xl overflow-hidden border border-cream-200">
        {/* Top accent gradient line */}
        <div className="h-1.5 bg-gradient-to-r from-film-warm via-sepia-300 to-film-cool" />

        {/* Postcard content */}
        <div className="p-6">
          {/* Header */}
          <div className="text-center mb-6">
            <h2 className="font-serif text-xl text-sepia-800 mb-1">오늘을 위한 TripKit</h2>
            <div className="w-8 h-0.5 bg-sepia-300 mx-auto" />
          </div>

          {/* Sections */}
          <div className="space-y-6">
            {/* Travel Scene */}
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cream-100 flex items-center justify-center">
                <span className="text-base" role="img" aria-label="location">📍</span>
              </div>
              <div className="flex-1 pt-1">
                <h3 className="text-xs font-semibold text-sepia-500 uppercase tracking-wider mb-2">
                  여행 장면
                </h3>
                <p className="text-sm text-sepia-800 leading-relaxed">
                  <span className="font-medium">{city}</span>의{' '}
                  <span className="font-medium">{spotName}</span>에서
                </p>
                <p className="text-sm text-sepia-700 mt-1">
                  {mainAction}
                </p>
                <p className="text-xs text-sepia-500 italic mt-2 leading-relaxed">
                  눈앞의 풍경과 공기까지<br />
                  천천히 담아 두고 싶은 순간이에요.
                </p>
              </div>
            </div>

            {/* Concept & Film */}
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cream-100 flex items-center justify-center">
                <span className="text-base" role="img" aria-label="film">🎞️</span>
              </div>
              <div className="flex-1 pt-1">
                <h3 className="text-xs font-semibold text-sepia-500 uppercase tracking-wider mb-2">
                  컨셉 & 필름
                </h3>
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-sepia-500">컨셉</span>
                    <span className="font-medium text-sepia-800">{conceptName}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-sepia-500">필름</span>
                    <span className="font-medium text-sepia-800">{filmStock}</span>
                  </div>
                </div>
                <p className="text-xs text-sepia-500 italic mt-2 leading-relaxed">
                  오늘의 색과 온도를 부드럽게 기록해 줄 필름이에요.
                </p>
              </div>
            </div>

            {/* Vibe Keywords */}
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cream-100 flex items-center justify-center">
                <span className="text-base" role="img" aria-label="sparkle">✨</span>
              </div>
              <div className="flex-1 pt-1">
                <h3 className="text-xs font-semibold text-sepia-500 uppercase tracking-wider mb-2">
                  이런 기분을 담았어요
                </h3>
                <div className="flex flex-wrap gap-2 mb-2">
                  {vibeKeywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 text-xs font-medium text-sepia-700 bg-gradient-to-r from-cream-100 to-cream-200 rounded-full"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-sepia-500 italic leading-relaxed">
                  같은 감정을 가만히 눌러 담았습니다.
                </p>
              </div>
            </div>
          </div>

          {/* Footer message */}
          <div className="mt-6 pt-5 border-t border-dashed border-cream-300 text-center">
            <p className="text-sm text-sepia-600 leading-relaxed mb-4">
              카메라와 작은 설렘만 챙기면,<br />
              이 장면은 곧 당신의 실제 사진이 됩니다.
            </p>
            <p className="font-serif text-lg text-sepia-800 italic">
              이제, 떠나볼까요?
            </p>
          </div>
        </div>

        {/* Decorative stamp */}
        <div className="absolute top-6 right-6 w-12 h-12 border-2 border-sepia-300 rounded flex items-center justify-center rotate-12 opacity-60">
          <div className="text-center">
            <span className="block text-[8px] font-bold text-sepia-400 tracking-wider">TRIP</span>
            <span className="block text-[8px] font-bold text-sepia-400 tracking-wider">KIT</span>
          </div>
        </div>

        {/* Corner decorations */}
        <div className="absolute bottom-0 left-0 w-16 h-16 opacity-10">
          <svg viewBox="0 0 100 100" className="w-full h-full text-sepia-400">
            <circle cx="0" cy="100" r="80" fill="currentColor" />
          </svg>
        </div>
        <div className="absolute bottom-0 right-0 w-16 h-16 opacity-10">
          <svg viewBox="0 0 100 100" className="w-full h-full text-sepia-400">
            <circle cx="100" cy="100" r="80" fill="currentColor" />
          </svg>
        </div>
      </div>
    </motion.div>
  );
}

// 컨셉 ID로 한글 이름 가져오기
function getConceptNameKo(conceptId: string | undefined): string | null {
  if (!conceptId) return null;

  const conceptNames: Record<string, string> = {
    flaneur: '플라뇌르',
    filmlog: '필름 로그',
    midnight: '미드나잇',
    pastoral: '파스토럴',
    noir: '느와르',
    seaside: '씨사이드 메모아',
  };

  return conceptNames[conceptId] || null;
}
