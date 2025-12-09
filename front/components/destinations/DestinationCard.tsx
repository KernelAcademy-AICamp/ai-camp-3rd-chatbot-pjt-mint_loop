'use client';

import Image from 'next/image';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';
import type { Destination } from '@/lib/types';

interface DestinationCardProps {
  destination: Destination;
  isActive?: boolean;
  onClick: () => void;
}

export function DestinationCard({ destination, isActive, onClick }: DestinationCardProps) {
  const photo = destination.placeDetails?.photos?.[0]?.url;

  return (
    <motion.article
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        'flex-shrink-0 w-[calc(100vw-4rem)] max-w-2xl bg-white rounded-2xl overflow-hidden cursor-pointer transition-all duration-300',
        isActive
          ? 'shadow-xl ring-2 ring-sepia-400'
          : 'shadow-lg hover:shadow-xl'
      )}
    >
      {/* Image */}
      <div className="relative aspect-[4/3] bg-cream-100 overflow-hidden">
        {photo ? (
          <Image
            src={photo}
            alt={destination.name}
            fill
            sizes="(max-width: 768px) calc(100vw - 4rem), 672px"
            className="object-cover"
            unoptimized
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-5xl opacity-30">📍</span>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />

        {/* Rating Badge */}
        {destination.placeDetails?.rating && (
          <div className="absolute top-3 left-3">
            <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-white/95 backdrop-blur-sm rounded-full text-sm font-medium text-gray-800">
              <span className="text-sepia-600">★</span>
              {destination.placeDetails.rating.toFixed(1)}
            </span>
          </div>
        )}

        {/* Title on Image */}
        <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
          <h3 className="font-serif text-lg font-medium mb-0.5">
            {destination.name}
          </h3>
          <p className="text-white/80 text-sm">
            {destination.city}, {destination.country}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Stats */}
        <div className="flex items-center gap-3 mb-3 text-sm text-gray-600">
          <span className="flex items-center gap-1">
            <span className="text-sepia-500">📸</span>
            {destination.photographyScore}/10
          </span>
          <span className="flex items-center gap-1">
            <span className="text-sepia-500">🛡️</span>
            {destination.safetyRating}/10
          </span>
          <span className="text-sepia-600 font-medium ml-auto">
            {destination.estimatedBudget || '$$'}
          </span>
        </div>

        {/* Match Reason */}
        <p className="text-sm text-gray-600 line-clamp-2">
          {destination.matchReason}
        </p>

        {/* View Detail */}
        <div className="mt-4 pt-3 border-t border-cream-100">
          <span className="text-sm font-medium text-sepia-600 flex items-center gap-1">
            자세히 보기
            <span>→</span>
          </span>
        </div>
      </div>
    </motion.article>
  );
}
