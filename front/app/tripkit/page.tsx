'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useVibeStore } from '@/lib/store/useVibeStore';
import { WrappedGift } from '@/components/tripkit/WrappedGift';
import { UnwrappingAnimation } from '@/components/tripkit/UnwrappingAnimation';
import { Postcard } from '@/components/tripkit/Postcard';
import { getConceptById } from '@/lib/constants/concepts';

type Stage = 'intro' | 'unwrapping' | 'reveal';

export default function TripKitPage() {
  const { tripKitProfile, selectedConcept } = useVibeStore();
  const [stage, setStage] = useState<Stage>('intro');
  const [showPostcard, setShowPostcard] = useState(false);

  const concept = tripKitProfile.conceptId
    ? getConceptById(tripKitProfile.conceptId) ?? null
    : null;

  const handleUnwrap = () => {
    setStage('unwrapping');
  };

  const handleUnwrapComplete = () => {
    setStage('reveal');
    setTimeout(() => {
      setShowPostcard(true);
    }, 200);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-cream-50 via-cream-100 to-cream-200 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-10 w-64 h-64 bg-sepia-200/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-80 h-80 bg-film-warm/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cream-300/20 rounded-full blur-3xl" />
      </div>

      {/* Main content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6 py-12">
        <AnimatePresence mode="wait">
          {stage === 'intro' && (
            <motion.div
              key="intro"
              className="flex flex-col items-center text-center max-w-md"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.5 }}
            >
              {/* Decorative line */}
              <motion.div
                className="w-12 h-0.5 bg-sepia-400 mb-8"
                initial={{ width: 0 }}
                animate={{ width: 48 }}
                transition={{ delay: 0.2, duration: 0.6 }}
              />

              <motion.h1
                className="font-serif text-2xl md:text-3xl text-sepia-800 leading-relaxed mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.6 }}
              >
                당신만을 위한 TripKit이<br />준비됐어요
              </motion.h1>

              <motion.div
                className="space-y-1 mb-10"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5, duration: 0.6 }}
              >
                <p className="text-sepia-600 text-sm md:text-base">대화로 고른 분위기,</p>
                <p className="text-sepia-600 text-sm md:text-base">선택한 컨셉, 그리고 잘 어울리는 장소까지</p>
                <p className="text-sepia-600 text-sm md:text-base">오늘을 위한 &apos;여행 키트&apos;를 한 장의 엽서에 담아두었어요.</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7, duration: 0.6 }}
              >
                <WrappedGift onUnwrap={handleUnwrap} />
              </motion.div>

              <motion.p
                className="text-sepia-500 text-base italic mt-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1, duration: 0.6 }}
              >
                열어볼까요?
              </motion.p>
            </motion.div>
          )}

          {stage === 'unwrapping' && (
            <motion.div
              key="unwrapping"
              className="flex flex-col items-center"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <UnwrappingAnimation onComplete={handleUnwrapComplete} />
            </motion.div>
          )}

          {stage === 'reveal' && (
            <motion.div
              key="reveal"
              className="flex flex-col items-center w-full max-w-lg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Postcard
                profile={tripKitProfile}
                concept={concept}
                isVisible={showPostcard}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
