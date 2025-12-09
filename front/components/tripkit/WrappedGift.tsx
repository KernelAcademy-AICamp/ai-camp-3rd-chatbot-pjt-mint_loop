'use client';

import { motion } from 'framer-motion';

interface WrappedGiftProps {
  onUnwrap: () => void;
}

export function WrappedGift({ onUnwrap }: WrappedGiftProps) {
  return (
    <motion.div
      className="relative cursor-pointer select-none"
      onClick={onUnwrap}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {/* Gift wrapper */}
      <div className="relative w-64 h-72">
        {/* Main package body */}
        <div className="absolute inset-0 bg-gradient-to-br from-sepia-100 via-cream-100 to-sepia-50 rounded-lg shadow-lg border border-cream-300">
          {/* Texture pattern */}
          <div className="absolute inset-0 opacity-30">
            <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              <pattern id="paper-texture" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="0.5" fill="#d4c4a8" opacity="0.5" />
                <circle cx="12" cy="12" r="0.5" fill="#d4c4a8" opacity="0.3" />
              </pattern>
              <rect width="100%" height="100%" fill="url(#paper-texture)" />
            </svg>
          </div>
        </div>

        {/* Vertical ribbon */}
        <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-8">
          <div className="w-full h-full bg-gradient-to-r from-sepia-400 via-sepia-300 to-sepia-400 shadow-sm" />
          {/* Ribbon shine */}
          <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-1 bg-gradient-to-b from-transparent via-white/40 to-transparent" />
        </div>

        {/* Horizontal ribbon */}
        <div className="absolute top-1/3 left-0 right-0 h-8">
          <div className="w-full h-full bg-gradient-to-b from-sepia-400 via-sepia-300 to-sepia-400 shadow-sm" />
          {/* Ribbon shine */}
          <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-1 bg-gradient-to-r from-transparent via-white/40 to-transparent" />
        </div>

        {/* Ribbon bow */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
          {/* Bow loops */}
          <div className="relative">
            {/* Left loop */}
            <div className="absolute -left-8 top-1/2 -translate-y-1/2 w-10 h-7 bg-gradient-to-l from-sepia-300 to-sepia-400 rounded-full -rotate-12 shadow-sm" />
            {/* Right loop */}
            <div className="absolute -right-8 top-1/2 -translate-y-1/2 w-10 h-7 bg-gradient-to-r from-sepia-300 to-sepia-400 rounded-full rotate-12 shadow-sm" />
            {/* Center knot */}
            <div className="relative w-6 h-6 bg-gradient-to-br from-sepia-400 to-sepia-500 rounded-full shadow-md z-10" />
            {/* Ribbon tails */}
            <div className="absolute top-4 -left-2 w-4 h-10 bg-gradient-to-b from-sepia-400 to-sepia-300 rounded-b-sm -rotate-12 origin-top" />
            <div className="absolute top-4 -right-2 w-4 h-10 bg-gradient-to-b from-sepia-400 to-sepia-300 rounded-b-sm rotate-12 origin-top" />
          </div>
        </div>

        {/* Decorative tag */}
        <div className="absolute bottom-6 right-6 z-10">
          <div className="relative">
            {/* Tag string */}
            <div className="absolute -top-3 left-1/2 w-px h-3 bg-sepia-400" />
            {/* Tag body */}
            <div className="bg-cream-50 border border-sepia-300 rounded px-3 py-1.5 shadow-sm">
              <span className="text-xs font-serif text-sepia-600 italic">For You</span>
            </div>
          </div>
        </div>

        {/* Subtle sparkle effects */}
        <motion.div
          className="absolute top-8 right-12 w-2 h-2 bg-sepia-300 rounded-full"
          animate={{ opacity: [0.3, 0.8, 0.3], scale: [0.8, 1.2, 0.8] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-16 left-8 w-1.5 h-1.5 bg-sepia-400 rounded-full"
          animate={{ opacity: [0.2, 0.6, 0.2], scale: [0.8, 1.1, 0.8] }}
          transition={{ duration: 2.5, repeat: Infinity, delay: 0.5 }}
        />
      </div>

      {/* Tap hint */}
      <motion.p
        className="text-center text-xs text-sepia-400 mt-4"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        탭하여 열기
      </motion.p>
    </motion.div>
  );
}
