"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useVibeStore } from "@/lib/store/useVibeStore";
import { DestinationCard } from "@/components/destinations/DestinationCard";
import { DestinationModal } from "@/components/destinations/DestinationModal";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { getConceptById } from "@/lib/constants/concepts";
import { cn } from "@/lib/utils/cn";
import type { Destination } from "@/lib/types";

interface StreamEvent {
  type: "destination" | "complete" | "error";
  index?: number;
  total?: number;
  destination?: Destination;
  error?: string;
}

export default function DestinationsPage() {
  const router = useRouter();
  const {
    selectedConcept,
    preferences,
    destinations,
    imageGenerationContext,
    addDestination,
    clearDestinations,
  } = useVibeStore();

  const [error, setError] = useState<string | null>(null);
  const [selectedDestination, setSelectedDestination] =
    useState<Destination | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const carouselRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const concept = selectedConcept ? getConceptById(selectedConcept) : null;

  // 스트리밍 API 호출
  const loadDestinationsStream = useCallback(async () => {
    // 이전 요청 취소
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setError(null);
    clearDestinations();

    // 현재 store 상태를 직접 가져오기
    const store = useVibeStore.getState();
    const currentPreferences = store.preferences;
    const currentConcept = store.selectedConcept;
    const currentImageContext = store.imageGenerationContext;

    try {
      const response = await fetch("/api/recommendations/destinations/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          preferences: currentPreferences,
          concept: currentConcept,
          travelScene: currentPreferences.travelScene,
          travelDestination: currentPreferences.travelDestination,
          imageGenerationContext: currentImageContext
            ? {
                destination: currentImageContext.destination,
                additionalPrompt: currentImageContext.additionalPrompt,
                filmStock: currentImageContext.filmStock,
                outfitStyle: currentImageContext.outfitStyle,
              }
            : null,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error("스트리밍 연결에 실패했습니다.");
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("스트림을 읽을 수 없습니다.");
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const eventData: StreamEvent = JSON.parse(line.slice(6));

              if (eventData.type === "destination" && eventData.destination) {
                addDestination(eventData.destination);
              } else if (eventData.type === "error") {
                throw new Error(
                  eventData.error || "추천 생성 중 오류가 발생했습니다."
                );
              }
            } catch {
              // 파싱 에러 무시
            }
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        return;
      }
      setError(
        err instanceof Error ? err.message : "추천을 불러오는 데 실패했습니다."
      );
    }
  }, [addDestination, clearDestinations]);

  // 컴포넌트 마운트 시 실행
  useEffect(() => {
    loadDestinationsStream();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 캐러셀 스크롤
  const scrollToIndex = (index: number) => {
    if (!carouselRef.current) return;
    const cards = carouselRef.current.querySelectorAll("[data-card]");
    if (cards[index]) {
      const card = cards[index] as HTMLElement;
      carouselRef.current.scrollTo({
        left: card.offsetLeft - 16,
        behavior: "smooth",
      });
    }
    setCurrentIndex(index);
  };

  const handleScroll = () => {
    if (!carouselRef.current) return;
    const scrollLeft = carouselRef.current.scrollLeft;
    const cards = carouselRef.current.querySelectorAll("[data-card]");
    let closestIndex = 0;
    let closestDistance = Infinity;
    cards.forEach((card, index) => {
      const distance = Math.abs(
        (card as HTMLElement).offsetLeft - 16 - scrollLeft
      );
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
          <Link
            href="/concept"
            className="inline-flex items-center gap-2 text-sm text-sepia-600 hover:text-sepia-800 transition-colors mb-4 group"
          >
            <span className="w-8 h-8 rounded-full bg-cream-100 flex items-center justify-center group-hover:-translate-x-1 transition-transform">
              ←
            </span>
            <span>컨셉 다시 선택하기</span>
          </Link>

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
              당신의 Vibe에 맞는{" "}
              <span className="text-sepia-600">특별한 장소들</span>
            </h1>
            <p className="text-gray-500 mt-1">
              좌우로 슬라이드하거나 버튼을 눌러 탐색하세요
            </p>
          </motion.div>

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
                &ldquo;
                {imageGenerationContext
                  ? `${imageGenerationContext.destination}${
                      imageGenerationContext.additionalPrompt
                        ? `에서 ${imageGenerationContext.additionalPrompt}`
                        : ""
                    }`
                  : preferences.travelScene}
                &rdquo;
              </p>
            </motion.div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        {/* 오류 화면 */}
        {error && (
          <div className="max-w-6xl mx-auto px-4">
            <div className="bg-white border border-red-200 rounded-xl p-8 text-center">
              <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⚠️</span>
              </div>
              <h3 className="text-lg font-serif text-gray-900 mb-2">
                오류가 발생했습니다
              </h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <Button
                onClick={() => loadDestinationsStream()}
                variant="secondary"
                size="sm"
              >
                다시 시도
              </Button>
            </div>
          </div>
        )}

        {/* 로딩 화면 - destination 데이터가 없으면 로딩 표시 */}
        {!error && destinations.length === 0 && (
          <div className="fixed inset-0 flex flex-col items-center justify-center">
            <div className="w-12 h-12 border-4 border-cream-200 border-t-sepia-500 rounded-full animate-spin mb-4" />
            <p className="text-sepia-700 text-lg">Loading...</p>
          </div>
        )}

        {/* 결과 화면 - destination 데이터가 있으면 표시 */}
        {!error && destinations.length > 0 && (
          <>
            <div className="relative">
              {/* Navigation Buttons */}
              {destinations.length > 1 && (
                <>
                  <button
                    onClick={() => scrollToIndex(currentIndex - 1)}
                    disabled={currentIndex === 0}
                    className={cn(
                      "absolute left-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center transition-all",
                      currentIndex === 0
                        ? "opacity-30 cursor-not-allowed"
                        : "hover:bg-cream-50 hover:scale-110"
                    )}
                  >
                    <span className="text-sepia-600 text-xl">‹</span>
                  </button>
                  <button
                    onClick={() => scrollToIndex(currentIndex + 1)}
                    disabled={currentIndex === destinations.length - 1}
                    className={cn(
                      "absolute right-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center transition-all",
                      currentIndex === destinations.length - 1
                        ? "opacity-30 cursor-not-allowed"
                        : "hover:bg-cream-50 hover:scale-110"
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
                <AnimatePresence mode="popLayout">
                  {destinations.map((destination, index) => (
                    <motion.div
                      key={destination.id}
                      data-card
                      layout
                      initial={{ opacity: 0, scale: 0.8, x: 50 }}
                      animate={{ opacity: 1, scale: 1, x: 0 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{
                        type: "spring",
                        stiffness: 300,
                        damping: 25,
                        delay: 0.1,
                      }}
                      className="snap-start"
                    >
                      <DestinationCard
                        destination={destination}
                        isActive={currentIndex === index}
                        onClick={() => setSelectedDestination(destination)}
                      />
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Pagination Dots */}
            {destinations.length > 1 && (
              <div className="flex justify-center gap-2 mt-6">
                {destinations.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => scrollToIndex(index)}
                    className={cn(
                      "w-2 h-2 rounded-full transition-all",
                      currentIndex === index
                        ? "bg-sepia-500 w-6"
                        : "bg-cream-300 hover:bg-cream-400"
                    )}
                  />
                ))}
              </div>
            )}

            {/* Results Count */}
            <div className="text-center mt-8">
              <p className="text-sm text-gray-500">
                총{" "}
                <span className="font-semibold text-sepia-600">
                  {destinations.length}
                </span>
                개의 숨겨진 명소
              </p>
            </div>

            {/* TripKit Complete Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="text-center mt-10 pb-8"
            >
              <Button
                onClick={() => router.push("/tripkit")}
                size="lg"
                className="px-10"
              >
                TripKit 완성하기 →
              </Button>
              <p className="text-sm text-gray-500 mt-3">
                여행 준비가 완료되었어요!
              </p>
            </motion.div>
          </>
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
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
        .shimmer::after {
          content: "";
          position: absolute;
          inset: 0;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.4),
            transparent
          );
          animation: shimmer 1.5s infinite;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}
