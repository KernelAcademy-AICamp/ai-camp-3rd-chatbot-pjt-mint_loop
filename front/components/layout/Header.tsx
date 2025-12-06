'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';

export function Header() {
  const pathname = usePathname();
  const isHome = pathname === '/';
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      setIsScrolled(scrollPosition > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-in-out',
        isScrolled || !isHome
          ? 'bg-white/95 backdrop-blur-md shadow-md'
          : 'bg-transparent'
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📷</span>
            <span className={cn(
              'font-serif text-xl font-bold transition-colors duration-500',
              isScrolled || !isHome ? 'text-gray-900' : 'text-white'
            )}>
              Trip Kit
            </span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <Link
              href="/chat"
              className={cn(
                'text-sm font-medium transition-colors duration-500',
                isScrolled || !isHome ? 'text-gray-700 hover:text-sepia-400' : 'text-white hover:text-sepia-200'
              )}
            >
              Vibe 찾기
            </Link>
            <Link
              href="/concept"
              className={cn(
                'text-sm font-medium transition-colors duration-500',
                isScrolled || !isHome ? 'text-gray-700 hover:text-sepia-400' : 'text-white hover:text-sepia-200'
              )}
            >
              컨셉 둘러보기
            </Link>
          </nav>

          {/* CTA Button */}
          <Link
            href="/chat"
            className={cn(
              'hidden sm:inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-500',
              isScrolled || !isHome
                ? 'bg-sepia-800 text-white hover:bg-sepia-700'
                : 'bg-white/20 text-white border border-white hover:bg-white/30'
            )}
          >
            시작하기
          </Link>

          {/* Mobile Menu Button */}
          <button className={cn(
            'md:hidden p-2 rounded-lg transition-colors duration-500',
            isScrolled || !isHome ? 'hover:bg-cream-100' : 'hover:bg-white/10'
          )}>
            <svg
              className={cn(
                'w-6 h-6 transition-colors duration-500',
                isScrolled || !isHome ? 'text-gray-600' : 'text-white'
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
