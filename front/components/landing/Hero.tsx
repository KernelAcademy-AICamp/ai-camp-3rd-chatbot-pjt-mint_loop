'use client';

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-cream-50">
      {/* Background Image */}
      <div className="absolute inset-0">
        <Image
          src="/img/Gemini_Generated_Image_tm9qwmtm9qwmtm9q.png"
          alt="Travel vibe background"
          fill
          priority
          className="object-cover"
        />
        {/* Overlay for text readability */}
        <div className="absolute inset-0 bg-cream-50/10" />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          {/* Brand Badge */}
          <motion.span
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="inline-block px-4 py-2 mb-8 text-sm font-bold tracking-wider text-sepia-700 bg-sepia-100/70 rounded-full border border-sepia-200"
          >
            AI-Powered Vibe Travel
          </motion.span>

          {/* Main Headline */}
          <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-gray-900 leading-tight mb-8 drop-shadow-[0_2px_10px_rgba(255,255,255,0.8)]">
            당신은 티켓만 끊으세요.
            <br />
            <span className="text-white font-normal">여행의 &apos;분위기&apos;</span>는
            <br />
            우리가 챙겨드립니다.
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl lg:text-2xl text-white max-w-3xl mx-auto mb-12 font-normal leading-relaxed md:leading-loose tracking-wide drop-shadow-[0_2px_8px_rgba(0,0,0,0.6)]">
            AI가 당신의 여행 &apos;바이브&apos;를 분석하여
            <br className="hidden md:block" />
            숨겨진 장소, 필름 카메라 스타일, 완벽한 스타일링을 큐레이션합니다.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/chat">
              <Button size="lg" className="group px-8 py-4 text-lg border-2 border-sepia-800 bg-sepia-800 hover:bg-sepia-700 hover:border-white">
                <span>나만의 Vibe 찾기</span>
                <motion.span
                  className="inline-block ml-2"
                  animate={{ x: [0, 4, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  →
                </motion.span>
              </Button>
            </Link>
            <Link href="/concept">
              <Button variant="outline" size="lg" className="px-8 py-4 text-lg border-white text-white hover:bg-white/30">
                컨셉 둘러보기
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="w-6 h-10 border-2 border-gray-400 rounded-full flex justify-center pt-2">
          <div className="w-1.5 h-3 bg-gray-400 rounded-full" />
        </div>
      </motion.div>
    </section>
  );
}
