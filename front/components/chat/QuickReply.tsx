'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils/cn';

interface QuickReplyOption {
  label: string;
  value: string;
}

interface QuickReplyProps {
  options: QuickReplyOption[];
  onSelect: (value: string) => void;
  disabled?: boolean;
  showCustomInput?: boolean;
}

export function QuickReply({
  options,
  onSelect,
  disabled = false,
  showCustomInput = true,
}: QuickReplyProps) {
  const [isCustomInputOpen, setIsCustomInputOpen] = useState(false);
  const [customValue, setCustomValue] = useState('');

  const handleCustomSubmit = () => {
    if (customValue.trim()) {
      onSelect(customValue.trim());
      setCustomValue('');
      setIsCustomInputOpen(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleCustomSubmit();
    }
    if (e.key === 'Escape') {
      setIsCustomInputOpen(false);
      setCustomValue('');
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {options.map((option, index) => (
          <motion.button
            key={option.value}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            onClick={() => onSelect(option.value)}
            disabled={disabled}
            className={cn(
              'px-4 py-2 rounded-full text-sm font-medium',
              'bg-white border border-cream-300 text-gray-700',
              'hover:bg-sepia-50 hover:border-sepia-400 hover:text-sepia-700',
              'transition-all duration-200',
              'disabled:opacity-50 disabled:pointer-events-none'
            )}
          >
            {option.label}
          </motion.button>
        ))}

        {/* 직접 입력 버튼 */}
        {/* {showCustomInput && !isCustomInputOpen && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: options.length * 0.05 }}
            onClick={() => setIsCustomInputOpen(true)}
            disabled={disabled}
            className={cn(
              'px-4 py-2 rounded-full text-sm font-medium',
              'bg-cream-100 border border-dashed border-sepia-300 text-sepia-600',
              'hover:bg-sepia-50 hover:border-sepia-400 hover:text-sepia-700',
              'transition-all duration-200',
              'disabled:opacity-50 disabled:pointer-events-none',
              'flex items-center gap-1'
            )}
          >
            <span>✏️</span>
            <span>직접 입력</span>
          </motion.button>
        )} */}
      </div>

      {/* 직접 입력 필드 */}
      <AnimatePresence>
        {isCustomInputOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="flex gap-2 items-center">
              <input
                type="text"
                value={customValue}
                onChange={(e) => setCustomValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="원하는 내용을 입력하세요..."
                autoFocus
                disabled={disabled}
                className={cn(
                  'flex-1 px-4 py-2 rounded-full text-sm',
                  'bg-white border border-cream-300 text-gray-700',
                  'focus:outline-none focus:ring-2 focus:ring-sepia-300 focus:border-sepia-400',
                  'placeholder:text-gray-400',
                  'disabled:opacity-50'
                )}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleCustomSubmit}
                disabled={disabled || !customValue.trim()}
                className={cn(
                  'px-4 py-2 rounded-full text-sm font-medium',
                  'bg-sepia-500 text-white',
                  'hover:bg-sepia-600',
                  'transition-colors duration-200',
                  'disabled:opacity-50 disabled:pointer-events-none'
                )}
              >
                전송
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setIsCustomInputOpen(false);
                  setCustomValue('');
                }}
                disabled={disabled}
                className={cn(
                  'p-2 rounded-full text-sm',
                  'text-gray-500 hover:text-gray-700 hover:bg-cream-100',
                  'transition-colors duration-200'
                )}
              >
                ✕
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
