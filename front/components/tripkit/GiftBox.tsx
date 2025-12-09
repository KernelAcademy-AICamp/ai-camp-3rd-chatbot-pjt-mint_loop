'use client';

import { motion, AnimatePresence } from 'framer-motion';

interface GiftBoxProps {
  isOpen: boolean;
  onAnimationComplete?: () => void;
}

export function GiftBox({ isOpen, onAnimationComplete }: GiftBoxProps) {
  return (
    <div className="relative w-48 h-48 mx-auto">
      {/* Box Shadow */}
      <motion.div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-40 h-4 bg-sepia-200/30 rounded-full blur-md"
        animate={isOpen ? { scale: 1.5, opacity: 0.2 } : { scale: 1, opacity: 0.4 }}
        transition={{ duration: 0.5 }}
      />

      {/* Box Base */}
      <motion.div
        className="absolute bottom-4 left-1/2 -translate-x-1/2 w-36 h-28 bg-gradient-to-b from-sepia-600 to-sepia-700 rounded-lg shadow-lg"
        animate={isOpen ? { scale: 0.95 } : { scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        {/* Vertical Ribbon on Box */}
        <div className="absolute left-1/2 -translate-x-1/2 w-6 h-full bg-gradient-to-b from-cream-200 to-cream-300" />

        {/* Horizontal Ribbon on Box */}
        <div className="absolute top-1/2 -translate-y-1/2 w-full h-6 bg-gradient-to-r from-cream-200 via-cream-100 to-cream-200" />
      </motion.div>

      {/* Box Lid */}
      <motion.div
        className="absolute bottom-28 left-1/2 origin-bottom"
        initial={{ x: '-50%', rotateX: 0 }}
        animate={isOpen
          ? { x: '-50%', rotateX: -120, y: -60 }
          : { x: '-50%', rotateX: 0, y: 0 }
        }
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        {/* Lid Top */}
        <div className="w-40 h-8 bg-gradient-to-b from-sepia-500 to-sepia-600 rounded-t-lg shadow-md">
          {/* Vertical Ribbon on Lid */}
          <div className="absolute left-1/2 -translate-x-1/2 w-6 h-full bg-gradient-to-b from-cream-100 to-cream-200" />
        </div>
      </motion.div>

      {/* Ribbon Bow */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            className="absolute bottom-32 left-1/2 -translate-x-1/2 z-10"
            initial={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5, y: -30 }}
            transition={{ duration: 0.3 }}
          >
            {/* Bow Center */}
            <div className="relative">
              <div className="w-5 h-5 bg-cream-300 rounded-full shadow-sm" />

              {/* Left Loop */}
              <div className="absolute -left-6 top-1/2 -translate-y-1/2 w-7 h-5 bg-gradient-to-l from-cream-200 to-cream-300 rounded-full -rotate-12" />

              {/* Right Loop */}
              <div className="absolute -right-6 top-1/2 -translate-y-1/2 w-7 h-5 bg-gradient-to-r from-cream-200 to-cream-300 rounded-full rotate-12" />

              {/* Ribbon Tails */}
              <div className="absolute -left-3 top-4 w-3 h-8 bg-cream-200 rounded-b-sm -rotate-12 origin-top" />
              <div className="absolute -right-3 top-4 w-3 h-8 bg-cream-200 rounded-b-sm rotate-12 origin-top" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Four Sides Unfolding */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Front Side */}
            <motion.div
              className="absolute bottom-4 left-1/2 -translate-x-1/2 w-36 h-28 bg-gradient-to-b from-sepia-600 to-sepia-700 rounded-lg origin-bottom"
              initial={{ rotateX: 0 }}
              animate={{ rotateX: 85 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <div className="absolute left-1/2 -translate-x-1/2 w-6 h-full bg-cream-200/50" />
            </motion.div>

            {/* Back Side */}
            <motion.div
              className="absolute bottom-4 left-1/2 -translate-x-1/2 w-36 h-28 bg-gradient-to-b from-sepia-700 to-sepia-800 rounded-lg origin-top"
              initial={{ rotateX: 0 }}
              animate={{ rotateX: -85 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <div className="absolute left-1/2 -translate-x-1/2 w-6 h-full bg-cream-200/30" />
            </motion.div>

            {/* Left Side */}
            <motion.div
              className="absolute bottom-4 left-[calc(50%-72px)] w-36 h-28 bg-gradient-to-r from-sepia-700 to-sepia-600 rounded-lg origin-right"
              initial={{ rotateY: 0 }}
              animate={{ rotateY: -85 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              <div className="absolute top-1/2 -translate-y-1/2 w-full h-6 bg-cream-200/30" />
            </motion.div>

            {/* Right Side */}
            <motion.div
              className="absolute bottom-4 left-[calc(50%-72px)] w-36 h-28 bg-gradient-to-l from-sepia-700 to-sepia-600 rounded-lg origin-left"
              initial={{ rotateY: 0 }}
              animate={{ rotateY: 85 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              onAnimationComplete={onAnimationComplete}
            >
              <div className="absolute top-1/2 -translate-y-1/2 w-full h-6 bg-cream-200/30" />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Sparkles when opening */}
      <AnimatePresence>
        {isOpen && (
          <>
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-sepia-300 rounded-full"
                initial={{
                  opacity: 0,
                  scale: 0,
                  left: '50%',
                  bottom: '60%'
                }}
                animate={{
                  opacity: [0, 1, 0],
                  scale: [0, 1, 0],
                  left: `${30 + Math.random() * 40}%`,
                  bottom: `${60 + Math.random() * 30}%`
                }}
                transition={{
                  duration: 0.8,
                  delay: 0.2 + i * 0.1,
                  ease: 'easeOut'
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
