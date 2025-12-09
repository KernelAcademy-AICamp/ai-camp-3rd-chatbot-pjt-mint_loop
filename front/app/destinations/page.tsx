'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useVibeStore } from '@/lib/store/useVibeStore';
import { DestinationCard } from '@/components/destinations/DestinationCard';
import { DestinationModal } from '@/components/destinations/DestinationModal';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { getConceptById } from '@/lib/constants/concepts';
import { cn } from '@/lib/utils/cn';
import type { Destination } from '@/lib/types';

// Skeleton Card
function SkeletonCard() {
  return (
    <div className="flex-shrink-0 w-[calc(100vw-4rem)] max-w-2xl bg-white rounded-2xl overflow-hidden shadow-lg">
      <div className="aspect-[4/3] bg-cream-100 relative overflow-hidden">
        <div className="absolute inset-0 shimmer" />
      </div>
      <div className="p-4 space-y-3">
        <div className="flex gap-3">
          <div className="h-5 w-16 bg-cream-200 rounded animate-pulse" />
          <div className="h-5 w-16 bg-cream-200 rounded animate-pulse" />
        </div>
        <div className="h-4 w-full bg-cream-100 rounded animate-pulse" />
        <div className="h-4 w-3/4 bg-cream-100 rounded animate-pulse" />
      </div>
    </div>
  );
}

export default function DestinationsPage() {
  const { selectedConcept, preferences, setDestinations, destinations, imageGenerationContext } = useVibeStore();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDestination, setSelectedDestination] = useState<Destination | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const carouselRef = useRef<HTMLDivElement>(null);

  const concept = selectedConcept ? getConceptById(selectedConcept) : null;

  // API 호출
  const loadDestinations = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/recommendations/destinations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          preferences,
          concept: selectedConcept,
          travelScene: preferences.travelScene,
          travelDestination: preferences.travelDestination,
          // 이미지 생성에서 사용한 컨텍스트 전달
          imageGenerationContext: imageGenerationContext ? {
            destination: imageGenerationContext.destination,
            additionalPrompt: imageGenerationContext.additionalPrompt,
            filmStock: imageGenerationContext.filmStock,
            outfitStyle: imageGenerationContext.outfitStyle,
          } : null,
        }),
      });

      const data = await response.json();

      if ((data.status === 'success' || data.status === 'completed') && data.destinations) {
        setDestinations(data.destinations);
      } else {
        throw new Error('Failed to get recommendations');
      }
    } catch (err) {
      console.error('Failed to load destinations:', err);
      setError('추천을 불러오는 데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [preferences, selectedConcept, setDestinations, imageGenerationContext]);

  useEffect(() => {
    loadDestinations();
  }, [loadDestinations]);


  // 캐러셀 스크롤
  const scrollToIndex = (index: number) => {
    if (!carouselRef.current) return;
    const container = carouselRef.current;
    const cards = container.querySelectorAll('[data-card]');
    if (cards[index]) {
      const card = cards[index] as HTMLElement;
      container.scrollTo({
        left: card.offsetLeft - 16, // px-4 offset
        behavior: 'smooth',
      });
    }
    setCurrentIndex(index);
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      scrollToIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < destinations.length - 1) {
      scrollToIndex(currentIndex + 1);
    }
  };

  // 스크롤 이벤트로 현재 인덱스 업데이트
  const handleScroll = () => {
    if (!carouselRef.current) return;
    const container = carouselRef.current;
    const scrollLeft = container.scrollLeft;
    const cards = container.querySelectorAll('[data-card]');
    let closestIndex = 0;
    let closestDistance = Infinity;
    cards.forEach((card, index) => {
      const cardElement = card as HTMLElement;
      const distance = Math.abs(cardElement.offsetLeft - 16 - scrollLeft);
      if (distance < closestDistance) {
        closestDistance = distance;
        closestIndex = index;
      }
    });
    setCurrentIndex(closestIndex);
  };

  return (
    <div className="min-h-screen bg-cream-50">
      {/* Header */}
      <header className="bg-white border-b border-cream-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          {/* Back Button */}
          <Link
            href="/concept"
            className="inline-flex items-center gap-2 text-sm text-sepia-600 hover:text-sepia-800 transition-colors mb-4 group"
          >
            <span className="w-8 h-8 rounded-full bg-cream-100 flex items-center justify-center group-hover:-translate-x-1 transition-transform">
              ←
            </span>
            <span>컨셉 다시 선택하기</span>
          </Link>

          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <div className="flex items-center gap-2 mb-2">
              {concept && (
                <Badge variant="primary" className="text-sm">
                  {concept.nameKo}
                </Badge>
              )}
              {preferences.mood && (
                <Badge variant="secondary" className="text-sm">
                  {preferences.mood}
                </Badge>
              )}
            </div>

            <h1 className="font-serif text-2xl md:text-3xl text-gray-900">
              당신의 Vibe에 맞는 <span className="text-sepia-600">특별한 장소들</span>
            </h1>
            <p className="text-gray-500 mt-1">
              좌우로 슬라이드하거나 버튼을 눌러 탐색하세요
            </p>
          </motion.div>

          {/* Travel Scene - imageGenerationContext 우선 사용 */}
          {(imageGenerationContext || preferences.travelScene) && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="mt-4 p-4 bg-cream-50 rounded-xl border border-cream-200 max-w-lg"
            >
              <p className="text-xs font-semibold text-sepia-600 uppercase tracking-wider mb-1">
                꿈꾸는 장면
              </p>
              <p className="text-gray-700 italic">
                &ldquo;{imageGenerationContext
                  ? `${imageGenerationContext.destination}${imageGenerationContext.additionalPrompt ? `에서 ${imageGenerationContext.additionalPrompt}` : ''}`
                  : preferences.travelScene}&rdquo;
              </p>
            </motion.div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        {/* Error */}
        {error && (
          <div className="max-w-6xl mx-auto px-4 mb-8">
            <div className="bg-white border border-cream-200 rounded-xl p-6 text-center">
              <p className="text-gray-700 mb-4">{error}</p>
              <Button onClick={loadDestinations} variant="secondary" size="sm">
                다시 시도
              </Button>
            </div>
          </div>
        )}

        {/* Carousel Section */}
        <div className="relative">
          {/* Navigation Buttons */}
          {!isLoading && destinations.length > 1 && (
            <>
              <button
                onClick={handlePrev}
                disabled={currentIndex === 0}
                className={cn(
                  'absolute left-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center transition-all',
                  currentIndex === 0
                    ? 'opacity-30 cursor-not-allowed'
                    : 'hover:bg-cream-50 hover:scale-110'
                )}
              >
                <span className="text-sepia-600 text-xl">‹</span>
              </button>
              <button
                onClick={handleNext}
                disabled={currentIndex === destinations.length - 1}
                className={cn(
                  'absolute right-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center transition-all',
                  currentIndex === destinations.length - 1
                    ? 'opacity-30 cursor-not-allowed'
                    : 'hover:bg-cream-50 hover:scale-110'
                )}
              >
                <span className="text-sepia-600 text-xl">›</span>
              </button>
            </>
          )}

          {/* Carousel */}
          <div
            ref={carouselRef}
            onScroll={handleScroll}
            className="flex gap-6 overflow-x-auto py-4 px-4 md:px-8 scroll-smooth scrollbar-hide snap-x snap-mandatory"
          >
            {isLoading ? (
              // Skeleton
              <>
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    data-card
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="snap-start"
                  >
                    <SkeletonCard />
                  </motion.div>
                ))}
              </>
            ) : destinations.length > 0 ? (
              destinations.map((destination, index) => (
                <motion.div
                  key={destination.id}
                  data-card
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="snap-start"
                >
                  <DestinationCard
                    destination={destination}
                    isActive={currentIndex === index}
                    onClick={() => setSelectedDestination(destination)}
                  />
                </motion.div>
              ))
            ) : (
              <div className="flex-1 flex items-center justify-center min-h-[300px] w-full">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-cream-100 flex items-center justify-center mx-auto mb-4">
                    <span className="text-3xl">🌍</span>
                  </div>
                  <h3 className="text-lg font-serif text-gray-900 mb-2">
                    아직 추천된 여행지가 없어요
                  </h3>
                  <Button onClick={loadDestinations} variant="primary" size="sm">
                    여행지 추천받기
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Loading Indicator */}
          {isLoading && (
            <div className="text-center py-4">
              <span className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow text-sm text-sepia-700">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sepia-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-sepia-500" />
                </span>
                AI가 숨겨진 명소를 찾고 있어요...
              </span>
            </div>
          )}
        </div>

        {/* Pagination Dots */}
        {!isLoading && destinations.length > 1 && (
          <div className="flex justify-center gap-2 mt-6">
            {destinations.map((_, index) => (
              <button
                key={index}
                onClick={() => scrollToIndex(index)}
                className={cn(
                  'w-2 h-2 rounded-full transition-all',
                  currentIndex === index
                    ? 'bg-sepia-500 w-6'
                    : 'bg-cream-300 hover:bg-cream-400'
                )}
              />
            ))}
          </div>
        )}

        {/* Results Count */}
        {!isLoading && destinations.length > 0 && (
          <div className="text-center mt-8">
            <p className="text-sm text-gray-500">
              총 <span className="font-semibold text-sepia-600">{destinations.length}</span>개의 숨겨진 명소
            </p>
          </div>
        )}
      </main>

      {/* Modal */}
      <DestinationModal
        destination={selectedDestination}
        isOpen={!!selectedDestination}
        onClose={() => setSelectedDestination(null)}
      />

      {/* Styles */}
      <style jsx global>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .shimmer::after {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
          animation: shimmer 1.5s infinite;
        }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </div>
  );
}
