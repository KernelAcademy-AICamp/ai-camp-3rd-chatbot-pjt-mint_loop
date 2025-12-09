import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Message, ConversationStep, UserPreferences, Destination, TripKitProfile } from '@/lib/types';

// =============================================================================
// Constants
// =============================================================================

const SESSION_TTL = 7 * 24 * 60 * 60 * 1000; // 7일

// =============================================================================
// Types
// =============================================================================

interface RejectedItems {
  cities: string[];
  spots: string[];
  actions: string[];
  concepts: string[];
  outfits: string[];
  poses: string[];
  films: string[];
  cameras: string[];
}

interface ChatState {
  // Session
  sessionId: string;
  sessionCreatedAt: number;
  sessionLastActiveAt: number;

  // Messages
  messages: Message[];

  // Conversation State
  currentStep: ConversationStep;
  isLoading: boolean;
  error: string | null;

  // Collected Data (from ChatAgent)
  collectedData: TripKitProfile;
  rejectedItems: RejectedItems;

  // Preferences (accumulated during chat)
  preferences: UserPreferences;

  // Recommendations (populated when complete)
  recommendations: Destination[] | null;

  // Actions
  initSession: () => string;
  resetSession: () => string;
  refreshActivity: () => void;
  isSessionValid: () => boolean;

  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setMessages: (messages: Message[]) => void;
  setCurrentStep: (step: ConversationStep) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updatePreferences: (prefs: Partial<UserPreferences>) => void;
  setRecommendations: (recommendations: Destination[]) => void;
  setCollectedData: (data: TripKitProfile) => void;
  setRejectedItems: (items: RejectedItems) => void;
  resetChat: () => void;

  // Session recovery
  loadFromHistory: (history: Array<{ role: string; content: string }>, currentStep?: string, collectedData?: TripKitProfile) => void;
}

// =============================================================================
// Helpers
// =============================================================================

function generateId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function generateSessionId(): string {
  // UUID v4 형식
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// =============================================================================
// Initial State
// =============================================================================

const initialCollectedData: TripKitProfile = {
  city: undefined,
  spotName: undefined,
  mainAction: undefined,
  conceptId: undefined,
  outfitStyle: undefined,
  posePreference: undefined,
  filmType: undefined,
  cameraModel: undefined,
};

const initialRejectedItems: RejectedItems = {
  cities: [],
  spots: [],
  actions: [],
  concepts: [],
  outfits: [],
  poses: [],
  films: [],
  cameras: [],
};

const initialState = {
  sessionId: '',
  sessionCreatedAt: 0,
  sessionLastActiveAt: 0,
  messages: [],
  currentStep: 'init' as ConversationStep,
  isLoading: false,
  error: null,
  collectedData: initialCollectedData,
  rejectedItems: initialRejectedItems,
  preferences: {} as UserPreferences,
  recommendations: null,
};

// =============================================================================
// Store
// =============================================================================

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      ...initialState,

      // Session Management
      initSession: () => {
        const state = get();
        const now = Date.now();

        // 유효한 세션이 있으면 재사용
        if (state.sessionId && state.sessionCreatedAt && (now - state.sessionCreatedAt) < SESSION_TTL) {
          set({ sessionLastActiveAt: now });
          return state.sessionId;
        }

        // 새 세션 생성
        const newSessionId = generateSessionId();
        set({
          ...initialState,
          sessionId: newSessionId,
          sessionCreatedAt: now,
          sessionLastActiveAt: now,
        });
        return newSessionId;
      },

      resetSession: () => {
        const now = Date.now();
        const newSessionId = generateSessionId();
        set({
          ...initialState,
          sessionId: newSessionId,
          sessionCreatedAt: now,
          sessionLastActiveAt: now,
        });
        return newSessionId;
      },

      refreshActivity: () => {
        set({ sessionLastActiveAt: Date.now() });
      },

      isSessionValid: () => {
        const state = get();
        const now = Date.now();
        return !!(
          state.sessionId &&
          state.sessionCreatedAt &&
          (now - state.sessionCreatedAt) < SESSION_TTL
        );
      },

      // Message Management
      addMessage: (message) =>
        set((state) => ({
          messages: [
            ...state.messages,
            {
              ...message,
              id: generateId(),
              timestamp: Date.now(),
            },
          ],
          sessionLastActiveAt: Date.now(),
        })),

      setMessages: (messages) =>
        set({ messages }),

      setCurrentStep: (step) => set({ currentStep: step }),

      setLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),

      updatePreferences: (prefs) =>
        set((state) => ({
          preferences: { ...state.preferences, ...prefs },
        })),

      setRecommendations: (recommendations) => set({ recommendations }),

      setCollectedData: (data) =>
        set((state) => ({
          collectedData: { ...state.collectedData, ...data },
        })),

      setRejectedItems: (items) =>
        set((state) => ({
          rejectedItems: {
            cities: Array.from(new Set([...state.rejectedItems.cities, ...(items.cities || [])])),
            spots: Array.from(new Set([...state.rejectedItems.spots, ...(items.spots || [])])),
            actions: Array.from(new Set([...state.rejectedItems.actions, ...(items.actions || [])])),
            concepts: Array.from(new Set([...state.rejectedItems.concepts, ...(items.concepts || [])])),
            outfits: Array.from(new Set([...state.rejectedItems.outfits, ...(items.outfits || [])])),
            poses: Array.from(new Set([...state.rejectedItems.poses, ...(items.poses || [])])),
            films: Array.from(new Set([...state.rejectedItems.films, ...(items.films || [])])),
            cameras: Array.from(new Set([...state.rejectedItems.cameras, ...(items.cameras || [])])),
          },
        })),

      resetChat: () => {
        const state = get();
        set({
          ...initialState,
          sessionId: state.sessionId, // 세션 ID는 유지
          sessionCreatedAt: state.sessionCreatedAt,
          sessionLastActiveAt: Date.now(),
        });
      },

      // Session Recovery
      loadFromHistory: (history, currentStep, collectedData) => {
        const messages: Message[] = history.map((msg, index) => ({
          id: `recovered_${index}_${Date.now()}`,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: Date.now() - (history.length - index) * 1000, // 순서대로 타임스탬프 부여
        }));

        set({
          messages,
          currentStep: (currentStep as ConversationStep) || 'init',
          collectedData: collectedData || initialCollectedData,
          sessionLastActiveAt: Date.now(),
        });
      },
    }),
    {
      name: 'tripkit-chat-session',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // localStorage에 저장할 필드만 선택
        sessionId: state.sessionId,
        sessionCreatedAt: state.sessionCreatedAt,
        sessionLastActiveAt: state.sessionLastActiveAt,
        messages: state.messages,
        currentStep: state.currentStep,
        collectedData: state.collectedData,
        rejectedItems: state.rejectedItems,
        preferences: state.preferences,
      }),
    }
  )
);

// =============================================================================
// Selectors (성능 최적화용)
// =============================================================================

export const selectSessionId = (state: ChatState) => state.sessionId;
export const selectMessages = (state: ChatState) => state.messages;
export const selectCurrentStep = (state: ChatState) => state.currentStep;
export const selectCollectedData = (state: ChatState) => state.collectedData;
export const selectIsLoading = (state: ChatState) => state.isLoading;
export const selectIsComplete = (state: ChatState) => state.currentStep === 'complete';
