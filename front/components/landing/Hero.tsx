'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/Button';

const slides = [
  { src: '/img/1.avif', alt: 'Travel vibe 1' },
  { src: '/img/2.png', alt: 'Travel vibe 2' },
  { src: '/img/1043251_1065941_175.jpg', alt: 'Autumn landscape' },
  { src: '/img/4.jpg', alt: 'Travel vibe 4' },
];

export function Hero() {
  const [mounted, setMounted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % slides.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [mounted]);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-cream-50">
      {/* Background Image Slider */}
      <div className="absolute inset-0">
        <AnimatePresence mode="popLayout">
          <motion.div
            key={currentIndex}
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '-100%', opacity: 0 }}
            transition={{
              duration: 0.8,
              ease: [0.25, 0.1, 0.25, 1]
            }}
            className="absolute inset-0"
          >
            <Image
              src={slides[currentIndex].src}
              alt={slides[currentIndex].alt}
              fill
              priority
              className="object-cover"
            />
          </motion.div>
        </AnimatePresence>
        {/* Overlay for text readability */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/40 to-black/60 z-10" />
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
            className="inline-block px-4 py-2 mb-8 text-sm font-bold tracking-wider text-white bg-white/20 backdrop-blur-sm rounded-full border border-white/40"
          >
            AI-Powered Vibe Travel
          </motion.span>

          {/* Main Headline */}
          <div className="relative inline-block mb-8">
            <h1 className="relative font-serif text-4xl md:text-5xl lg:text-6xl xl:text-7xl text-white leading-tight drop-shadow-[0_4px_12px_rgba(0,0,0,0.8)]">
              당신은 티켓만 끊으세요.
              <br />
              <span className="text-cream-100 font-normal">여행의 &apos;분위기&apos;</span>는
              <br />
              우리가 챙겨드립니다.
            </h1>
          </div>

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
        <div className="w-6 h-10 border-2 border-white rounded-full flex justify-center pt-2">
          <div className="w-1.5 h-3 bg-white rounded-full" />
        </div>
      </motion.div>
    </section>
  );
}
