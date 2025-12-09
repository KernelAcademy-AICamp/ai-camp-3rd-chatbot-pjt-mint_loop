'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { CONCEPTS, getConceptById } from '@/lib/constants/concepts';
import { useVibeStore } from '@/lib/store/useVibeStore';
import { ConceptCard } from '@/components/concept/ConceptCard';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import type { Concept } from '@/lib/types';

export default function ConceptPage() {
  const router = useRouter();
  const { selectedConcept, setConcept, preferences } = useVibeStore();
  const [localSelected, setLocalSelected] = useState<Concept | null>(
    selectedConcept
  );
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const handleSelect = (conceptId: Concept) => {
    setLocalSelected(conceptId);
    setConcept(conceptId);
  };

  const handleContinue = () => {
    if (localSelected) {
      router.push('/generate');
    }
  };

  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 360; // Card width + gap
      const newScrollLeft =
        direction === 'left'
          ? scrollContainerRef.current.scrollLeft - scrollAmount
          : scrollContainerRef.current.scrollLeft + scrollAmount;

      scrollContainerRef.current.scrollTo({
        left: newScrollLeft,
        behavior: 'smooth',
      });
    }
  };

  return (
    <div className="min-h-screen bg-cream-50">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur-md border-b border-cream-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="font-serif text-xl text-gray-900">컨셉 선택</h1>
            <p className="text-sm text-gray-500">
              당신의 여행 스타일을 선택하세요
            </p>
          </div>
          {preferences.mood && (
            <Badge variant="secondary">
              ✓ Vibe: {preferences.mood}
            </Badge>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h2 className="font-serif text-3xl md:text-4xl text-gray-900 mb-4">
            어떤 감성으로 여행을 기록하고 싶으신가요?
          </h2>
          <p className="text-gray-600 max-w-xl mx-auto mb-2">
            여섯 가지 필름 스타일 중 하나를 선택하면, 그에 맞는 장소, 카메라, 스타일을
            큐레이션해드립니다.
          </p>
          <p className="text-sm text-gray-400">
            ← 좌우로 스크롤하여 모든 컨셉을 확인하세요 →
          </p>
        </motion.div>

        {/* Horizontal Scroll Container */}
        <div className="relative mb-10">
          {/* Left Scroll Button */}
          <button
            onClick={() => scroll('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white/90 hover:bg-white shadow-lg rounded-full p-3 transition-all duration-200 hover:scale-110 hidden md:flex items-center justify-center"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-6 h-6 text-gray-700" />
          </button>

          {/* Right Scroll Button */}
          <button
            onClick={() => scroll('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white/90 hover:bg-white shadow-lg rounded-full p-3 transition-all duration-200 hover:scale-110 hidden md:flex items-center justify-center"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-6 h-6 text-gray-700" />
          </button>

          {/* Scrollable Container */}
          <div
            ref={scrollContainerRef}
            className="flex gap-5 overflow-x-auto pb-4 px-2 md:px-10 scroll-smooth snap-x snap-mandatory scrollbar-hide"
            style={{
              scrollbarWidth: 'none',
              msOverflowStyle: 'none',
            }}
          >
            {CONCEPTS.map((concept, index) => (
              <motion.div
                key={concept.id}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: index * 0.08 }}
                className="snap-center"
              >
                <ConceptCard
                  concept={concept}
                  isSelected={localSelected === concept.id}
                  onSelect={() => handleSelect(concept.id)}
                />
              </motion.div>
            ))}
          </div>

          {/* Scroll Indicator Dots */}
          <div className="flex justify-center gap-2 mt-4">
            {CONCEPTS.map((concept) => (
              <button
                key={concept.id}
                onClick={() => handleSelect(concept.id)}
                className={`w-2 h-2 rounded-full transition-all duration-200 ${
                  localSelected === concept.id
                    ? 'bg-sepia-500 w-6'
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}
                aria-label={`Select ${concept.nameKo}`}
              />
            ))}
          </div>
        </div>

        {/* Continue Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: localSelected ? 1 : 0.5 }}
          className="text-center"
        >
          <Button
            size="lg"
            onClick={handleContinue}
            disabled={!localSelected}
            className="px-12"
          >
            여행 이미지 생성하기 →
          </Button>
          {!localSelected && (
            <p className="text-sm text-gray-500 mt-3">
              컨셉을 선택해주세요
            </p>
          )}
        </motion.div>
      </main>

      {/* Custom CSS for hiding scrollbar */}
      <style jsx global>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
}
