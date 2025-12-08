'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { cn } from '@/lib/utils/cn';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import type { Destination } from '@/lib/types';

interface DestinationCardProps {
  destination: Destination;
  index: number;
}

export function DestinationCard({ destination, index }: DestinationCardProps) {
  const [isExpanded, setIsExpanded] = useState(index === 0);

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.15 }}
      className={cn(
        'bg-white rounded-2xl overflow-hidden border transition-all duration-300',
        isExpanded
          ? 'border-sepia-300 shadow-xl'
          : 'border-cream-200 hover:border-cream-300 hover:shadow-md'
      )}
    >
      {/* Header (Always Visible) */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-4 p-4 text-left"
      >
        {/* Thumbnail - Google Places 사진 또는 기본 아이콘 */}
        <div className="flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden relative bg-sepia-100 flex items-center justify-center">
          {destination.placeDetails?.photos?.[0]?.url ? (
            <img
              src={destination.placeDetails.photos[0].url}
              alt={destination.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-3xl">📍</span>
          )}
        </div>

        {/* Title & Location */}
        <div className="flex-1 min-w-0">
          <h3 className="font-serif text-lg text-gray-900 mb-1">
            {destination.name}
          </h3>
          <p className="text-sm text-gray-500">
            {destination.city}, {destination.country}
          </p>
          {!isExpanded && (
            <div className="flex items-center gap-2 mt-2">
              {destination.placeDetails?.rating && (
                <Badge variant="primary" size="sm">
                  ⭐ {destination.placeDetails.rating.toFixed(1)}
                </Badge>
              )}
              <Badge variant="secondary" size="sm">
                📸 {destination.photographyScore}/10
              </Badge>
              <Badge variant="secondary" size="sm">
                {destination.estimatedBudget || '$$'}
              </Badge>
            </div>
          )}
        </div>

        {/* Expand Icon */}
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="flex-shrink-0 w-8 h-8 rounded-full bg-cream-100 flex items-center justify-center"
        >
          <span className="text-gray-500 text-sm">▼</span>
        </motion.div>
      </button>

      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-6 space-y-4">
              {/* Google Places Photos Gallery */}
              {destination.placeDetails?.photos && destination.placeDetails.photos.length > 1 && (
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {destination.placeDetails.photos.slice(0, 5).map((photo, idx) => (
                    <div
                      key={idx}
                      className="flex-shrink-0 w-24 h-24 rounded-lg overflow-hidden"
                    >
                      {photo.url && (
                        <img
                          src={photo.url}
                          alt={`${destination.name} ${idx + 1}`}
                          className="w-full h-full object-cover"
                        />
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Google Rating & Info */}
              {destination.placeDetails && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
                  <h4 className="text-sm font-medium text-blue-800 mb-3 flex items-center gap-2">
                    <span>📍</span> Google Places 정보
                  </h4>
                  <div className="space-y-2">
                    {/* 평점 */}
                    {destination.placeDetails.rating && (
                      <div className="flex items-center gap-2">
                        <span className="text-yellow-500">⭐</span>
                        <span className="font-semibold text-gray-900">
                          {destination.placeDetails.rating.toFixed(1)}
                        </span>
                        <span className="text-sm text-gray-500">
                          ({destination.placeDetails.user_ratings_total?.toLocaleString()}개 리뷰)
                        </span>
                      </div>
                    )}
                    {/* 주소 */}
                    {destination.placeDetails.google_address && (
                      <p className="text-sm text-gray-600">
                        📫 {destination.placeDetails.google_address}
                      </p>
                    )}
                    {/* 영업 상태 */}
                    {destination.placeDetails.is_open_now !== undefined && (
                      <p className={cn(
                        "text-sm font-medium",
                        destination.placeDetails.is_open_now ? "text-green-600" : "text-red-600"
                      )}>
                        {destination.placeDetails.is_open_now ? "🟢 영업 중" : "🔴 영업 종료"}
                      </p>
                    )}
                    {/* 영업시간 */}
                    {destination.placeDetails.opening_hours && destination.placeDetails.opening_hours.length > 0 && (
                      <details className="text-sm">
                        <summary className="cursor-pointer text-blue-700 hover:text-blue-800">
                          🕐 영업시간 보기
                        </summary>
                        <ul className="mt-2 space-y-1 pl-4 text-gray-600">
                          {destination.placeDetails.opening_hours.map((hours, idx) => (
                            <li key={idx}>{hours}</li>
                          ))}
                        </ul>
                      </details>
                    )}
                    {/* 연락처 & 링크 */}
                    <div className="flex flex-wrap gap-2 mt-2">
                      {destination.placeDetails.phone && (
                        <a
                          href={`tel:${destination.placeDetails.phone}`}
                          className="inline-flex items-center gap-1 text-xs bg-white px-2 py-1 rounded border border-blue-200 text-blue-700 hover:bg-blue-50"
                        >
                          📞 {destination.placeDetails.phone}
                        </a>
                      )}
                      {destination.placeDetails.website && (
                        <a
                          href={destination.placeDetails.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs bg-white px-2 py-1 rounded border border-blue-200 text-blue-700 hover:bg-blue-50"
                        >
                          🌐 웹사이트
                        </a>
                      )}
                      {destination.placeDetails.google_maps_url && (
                        <a
                          href={destination.placeDetails.google_maps_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs bg-white px-2 py-1 rounded border border-blue-200 text-blue-700 hover:bg-blue-50"
                        >
                          🗺️ Google Maps
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Google Reviews */}
              {destination.placeDetails?.reviews && destination.placeDetails.reviews.length > 0 && (
                <div className="bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl p-4 border border-yellow-100">
                  <h4 className="text-sm font-medium text-yellow-800 mb-3 flex items-center gap-2">
                    <span>💬</span> 실제 방문자 리뷰
                  </h4>
                  <div className="space-y-3">
                    {destination.placeDetails.reviews.slice(0, 3).map((review, idx) => (
                      <div key={idx} className="bg-white rounded-lg p-3 border border-yellow-100">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-sm text-gray-900">
                            {review.author}
                          </span>
                          <span className="text-yellow-500 text-xs">
                            {'⭐'.repeat(review.rating || 0)}
                          </span>
                          <span className="text-xs text-gray-400">
                            {review.time}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 line-clamp-3">
                          {review.text}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Description */}
              <p className="text-gray-700 leading-relaxed">
                {destination.description}
              </p>

              {/* Local Vibe - 현지 분위기 */}
              {destination.localVibe && (
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 border border-amber-100">
                  <h4 className="text-sm font-medium text-amber-800 mb-2 flex items-center gap-2">
                    <span>🌿</span> 현지 분위기
                  </h4>
                  <p className="text-sm text-amber-700 italic">
                    &ldquo;{destination.localVibe}&rdquo;
                  </p>
                </div>
              )}

              {/* Why Hidden - 숨겨진 이유 */}
              {destination.whyHidden && (
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100">
                  <h4 className="text-sm font-medium text-purple-800 mb-2 flex items-center gap-2">
                    <span>💎</span> 숨겨진 보석인 이유
                  </h4>
                  <p className="text-sm text-purple-700">
                    {destination.whyHidden}
                  </p>
                </div>
              )}

              {/* Match Reason */}
              <div className="bg-sepia-50 rounded-xl p-4 border border-sepia-100">
                <h4 className="text-sm font-medium text-sepia-800 mb-2 flex items-center gap-2">
                  <span>✓</span> 당신의 Vibe에 맞는 이유
                </h4>
                <p className="text-sm text-sepia-700">
                  {destination.matchReason}
                </p>
              </div>

              {/* Activities - 추천 액티비티 */}
              {destination.activities && destination.activities.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-800 flex items-center gap-2">
                    <span>🎯</span> 이곳에서의 특별한 경험
                  </h4>
                  <div className="space-y-2">
                    {destination.activities.map((activity, idx) => (
                      <div
                        key={idx}
                        className="bg-white border border-cream-200 rounded-xl p-3 hover:border-sepia-200 transition-colors"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 rounded-lg bg-sepia-100 flex items-center justify-center flex-shrink-0">
                            <span className="text-sm">{idx === 0 ? '⭐' : idx === 1 ? '🌟' : '✨'}</span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <h5 className="font-medium text-gray-900 text-sm">
                              {activity.name}
                            </h5>
                            <p className="text-xs text-gray-600 mt-0.5">
                              {activity.description}
                            </p>
                            {(activity.duration || activity.bestTime) && (
                              <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                                {activity.duration && (
                                  <span className="flex items-center gap-1">
                                    <span>⏱️</span> {activity.duration}
                                  </span>
                                )}
                                {activity.bestTime && (
                                  <span className="flex items-center gap-1">
                                    <span>🕐</span> {activity.bestTime}
                                  </span>
                                )}
                              </div>
                            )}
                            {activity.localTip && (
                              <div className="mt-2 p-2 bg-amber-50 rounded-lg">
                                <p className="text-xs text-amber-700">
                                  <span className="font-medium">💡 로컬 팁:</span> {activity.localTip}
                                </p>
                              </div>
                            )}
                            {activity.photoOpportunity && (
                              <div className="mt-2 p-2 bg-blue-50 rounded-lg">
                                <p className="text-xs text-blue-700">
                                  <span className="font-medium">📷 포토 포인트:</span> {activity.photoOpportunity}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Story Prompt - 스토리 제안 */}
              {destination.storyPrompt && (
                <div className="bg-gradient-to-r from-rose-50 to-amber-50 rounded-xl p-4 border border-rose-100">
                  <h4 className="text-sm font-medium text-rose-800 mb-2 flex items-center gap-2">
                    <span>📖</span> 이곳에서 만들 당신의 스토리
                  </h4>
                  <p className="text-sm text-rose-700 leading-relaxed">
                    {destination.storyPrompt}
                  </p>
                </div>
              )}

              {/* Photography Tips - 사진 촬영 팁 */}
              {destination.photographyTips && destination.photographyTips.length > 0 && (
                <div className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl p-4 border border-cyan-100">
                  <h4 className="text-sm font-medium text-cyan-800 mb-2 flex items-center gap-2">
                    <span>📸</span> 인생샷 촬영 팁
                  </h4>
                  <ul className="space-y-1.5">
                    {destination.photographyTips.map((tip, idx) => (
                      <li key={idx} className="text-xs text-cyan-700 flex items-start gap-2">
                        <span className="text-cyan-500 mt-0.5">•</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center p-3 bg-cream-50 rounded-xl">
                  <div className="text-xl mb-1">📸</div>
                  <div className="text-xs text-gray-500 mb-0.5">포토 스팟</div>
                  <div className="font-semibold text-gray-900">
                    {destination.photographyScore}/10
                  </div>
                </div>
                <div className="text-center p-3 bg-cream-50 rounded-xl">
                  <div className="text-xl mb-1">🚃</div>
                  <div className="text-xs text-gray-500 mb-0.5">접근성</div>
                  <div className="font-semibold text-gray-900 capitalize text-sm">
                    {destination.transportAccessibility === 'easy'
                      ? '쉬움'
                      : destination.transportAccessibility === 'moderate'
                      ? '보통'
                      : '어려움'}
                  </div>
                </div>
                <div className="text-center p-3 bg-cream-50 rounded-xl">
                  <div className="text-xl mb-1">🛡️</div>
                  <div className="text-xs text-gray-500 mb-0.5">안전도</div>
                  <div className="font-semibold text-gray-900">
                    {destination.safetyRating}/10
                  </div>
                </div>
              </div>

              {/* Best Time */}
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>🗓️</span>
                <span>추천 시기: {destination.bestTimeToVisit}</span>
              </div>

              {/* Tags */}
              {destination.tags && (
                <div className="flex flex-wrap gap-2">
                  {destination.tags.map((tag) => (
                    <Badge key={tag} variant="outline" size="sm">
                      #{tag}
                    </Badge>
                  ))}
                </div>
              )}

              {/* CTA Button */}
              <Link
                href={`/destinations/${destination.id}/spots`}
                className="block"
              >
                <Button variant="primary" size="lg" className="w-full">
                  <span>숨겨진 스팟 탐색하기</span>
                  <span className="ml-2">→</span>
                </Button>
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.article>
  );
}
