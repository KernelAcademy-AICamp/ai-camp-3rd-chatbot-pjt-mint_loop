'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';

export function CallToAction() {
  return (
    <section className="py-24 px-6 bg-sepia-800 text-white relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='1' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-block px-4 py-2 mb-6 text-sm font-medium tracking-wider bg-white/10 rounded-full border border-white/20">
            Ready to Start?
          </span>

          <h2 className="font-serif text-3xl md:text-4xl lg:text-5xl mb-6">
            지금 바로 당신만의
            <br />
            여행 Vibe를 찾아보세요
          </h2>

          <p className="text-lg text-white/80 max-w-xl mx-auto mb-10">
            5분의 대화로 완성되는 감성 여행 큐레이션.
            <br />
            AI가 당신의 여행을 예술로 만들어드립니다.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/chat">
              <Button
                size="lg"
                className="bg-white text-sepia-800 hover:bg-cream-100 px-10 py-4 text-lg"
              >
                무료로 시작하기 →
              </Button>
            </Link>
          </div>

          {/* Stats */}
          <div className="mt-16 flex flex-wrap justify-center gap-12">
            {[
              { value: '5분', label: '소요 시간' },
              { value: '무료', label: '이용 비용' },
              { value: '3가지', label: '감성 컨셉' },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-serif font-bold mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-white/60">{stat.label}</div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
