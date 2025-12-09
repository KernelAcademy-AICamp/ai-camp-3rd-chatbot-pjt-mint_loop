'use client';

import { motion } from 'framer-motion';

interface UnwrappingAnimationProps {
  onComplete: () => void;
}

export function UnwrappingAnimation({ onComplete }: UnwrappingAnimationProps) {
  return (
    <div className="relative w-64 h-72">
      {/* Left paper piece flying away */}
      <motion.div
        className="absolute inset-y-0 left-0 w-1/2 bg-gradient-to-r from-sepia-100 to-cream-100 rounded-l-lg origin-right overflow-hidden"
        initial={{ rotateY: 0, x: 0, opacity: 1 }}
        animate={{ rotateY: -90, x: -100, opacity: 0 }}
        transition={{ duration: 0.8, ease: 'easeInOut' }}
      >
        {/* Ribbon on left piece */}
        <div className="absolute right-0 top-0 bottom-0 w-4 bg-gradient-to-r from-sepia-300 to-sepia-400" />
        <div className="absolute top-1/3 left-0 right-0 h-4 bg-gradient-to-b from-sepia-300 to-sepia-400" />
      </motion.div>

      {/* Right paper piece flying away */}
      <motion.div
        className="absolute inset-y-0 right-0 w-1/2 bg-gradient-to-l from-sepia-100 to-cream-100 rounded-r-lg origin-left overflow-hidden"
        initial={{ rotateY: 0, x: 0, opacity: 1 }}
        animate={{ rotateY: 90, x: 100, opacity: 0 }}
        transition={{ duration: 0.8, ease: 'easeInOut' }}
      >
        {/* Ribbon on right piece */}
        <div className="absolute left-0 top-0 bottom-0 w-4 bg-gradient-to-l from-sepia-300 to-sepia-400" />
        <div className="absolute top-1/3 left-0 right-0 h-4 bg-gradient-to-b from-sepia-300 to-sepia-400" />
      </motion.div>

      {/* Top paper piece flying up */}
      <motion.div
        className="absolute top-0 left-0 right-0 h-1/3 bg-gradient-to-b from-cream-100 to-sepia-50 rounded-t-lg origin-bottom overflow-hidden z-10"
        initial={{ rotateX: 0, y: 0, opacity: 1 }}
        animate={{ rotateX: 90, y: -80, opacity: 0 }}
        transition={{ duration: 0.6, ease: 'easeInOut', delay: 0.2 }}
      >
        {/* Ribbon bow */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2">
          <div className="w-6 h-6 bg-sepia-400 rounded-full" />
        </div>
      </motion.div>

      {/* Sparkle particles */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-sepia-300 rounded-full"
          initial={{
            opacity: 0,
            scale: 0,
            left: '50%',
            top: '50%'
          }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1, 0],
            left: `${20 + Math.random() * 60}%`,
            top: `${20 + Math.random() * 60}%`
          }}
          transition={{
            duration: 0.8,
            delay: 0.3 + i * 0.08,
            ease: 'easeOut'
          }}
        />
      ))}

      {/* Animation complete trigger */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        onAnimationComplete={onComplete}
      />
    </div>
  );
}
