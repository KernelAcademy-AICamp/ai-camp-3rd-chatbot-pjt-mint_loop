import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  UserPreferences,
  Destination,
  HiddenSpot,
  StylingRecommendation,
  Concept,
  TripKitProfile,
  TripKitStep,
  Message,
} from '@/lib/types';

interface GeneratedImage {
  spotId: string;
  imageUrl: string;
  timestamp: number;
}

// 이미지 생성 시 사용된 컨텍스트 정보
interface ImageGenerationContext {
  destination: string;        // 사용자가 입력한 여행지 (예: "파리 몽마르트르 카페 테라스")
  additionalPrompt: string;   // 추가 프롬프트/장면 설명
  filmStock: string;          // 선택한 필름 스톡
  outfitStyle: string;        // 의상 스타일
  generatedAt: number;        // 생성 시점
}

interface VibeState {
  // Session
  sessionId: string | null;

  // User Preferences
  preferences: UserPreferences;

  // TripKit 챗봇 상태
  tripKitProfile: TripKitProfile;
  tripKitStep: TripKitStep;
  chatMessages: Message[];

  // Selected Items
  selectedConcept: Concept | null;
  selectedDestination: Destination | null;
  selectedSpots: HiddenSpot[];

  // Recommendations
  destinations: Destination[];
  hiddenSpots: HiddenSpot[];
  styling: StylingRecommendation | null;

  // Generated Images
  generatedImages: GeneratedImage[];

  // Image Generation Context (이미지 생성 시 사용된 컨텍스트)
  imageGenerationContext: ImageGenerationContext | null;

  // Actions
  setSessionId: (id: string) => void;
  setPreferences: (prefs: Partial<UserPreferences>) => void;
  setConcept: (concept: Concept) => void;
  setDestinations: (destinations: Destination[]) => void;
  addDestination: (destination: Destination) => void;
  clearDestinations: () => void;
  selectDestination: (destination: Destination) => void;
  setHiddenSpots: (spots: HiddenSpot[]) => void;
  toggleSpotSelection: (spot: HiddenSpot) => void;
  setStyling: (styling: StylingRecommendation) => void;
  addGeneratedImage: (spotId: string, imageUrl: string) => void;
  getGeneratedImage: (spotId: string) => string | undefined;
  setImageGenerationContext: (context: Omit<ImageGenerationContext, 'generatedAt'>) => void;
  // TripKit 챗봇 액션
  updateTripKitProfile: (data: Partial<TripKitProfile>) => void;
  setTripKitStep: (step: TripKitStep) => void;
  addChatMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setChatMessages: (messages: Message[]) => void;
  resetTripKitChat: () => void;
  resetSession: () => void;
}

const initialState = {
  sessionId: null,
  preferences: {} as UserPreferences,
  tripKitProfile: {} as TripKitProfile,
  tripKitStep: 'greeting' as TripKitStep,
  chatMessages: [] as Message[],
  selectedConcept: null,
  selectedDestination: null,
  selectedSpots: [],
  destinations: [],
  hiddenSpots: [],
  styling: null,
  generatedImages: [],
  imageGenerationContext: null,
};

export const useVibeStore = create<VibeState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setSessionId: (id) => set({ sessionId: id }),

      setPreferences: (prefs) =>
        set((state) => ({
          preferences: { ...state.preferences, ...prefs },
        })),

      setConcept: (concept) =>
        set((state) => ({
          selectedConcept: concept,
          preferences: { ...state.preferences, concept },
        })),

      setDestinations: (destinations) => set({ destinations }),

      addDestination: (destination) =>
        set((state) => {
          // 이미 존재하는 destination인지 확인 (id로 체크)
          const exists = state.destinations.some((d) => d.id === destination.id);
          if (exists) {
            return state; // 이미 있으면 추가하지 않음
          }
          return {
            destinations: [...state.destinations, destination],
          };
        }),

      clearDestinations: () => set({ destinations: [] }),

      selectDestination: (destination) =>
        set({
          selectedDestination: destination,
          hiddenSpots: [],
          selectedSpots: [],
        }),

      setHiddenSpots: (spots) => set({ hiddenSpots: spots }),

      toggleSpotSelection: (spot) =>
        set((state) => {
          const isSelected = state.selectedSpots.some((s) => s.id === spot.id);
          return {
            selectedSpots: isSelected
              ? state.selectedSpots.filter((s) => s.id !== spot.id)
              : [...state.selectedSpots, spot],
          };
        }),

      setStyling: (styling) => set({ styling }),

      addGeneratedImage: (spotId, imageUrl) =>
        set((state) => ({
          generatedImages: [
            ...state.generatedImages.filter((img) => img.spotId !== spotId),
            { spotId, imageUrl, timestamp: Date.now() },
          ],
        })),

      getGeneratedImage: (spotId) => {
        const state = get();
        return state.generatedImages.find((img) => img.spotId === spotId)
          ?.imageUrl;
      },

      setImageGenerationContext: (context) =>
        set({
          imageGenerationContext: {
            ...context,
            generatedAt: Date.now(),
          },
        }),

      // TripKit 챗봇 액션
      updateTripKitProfile: (data) =>
        set((state) => ({
          tripKitProfile: { ...state.tripKitProfile, ...data },
        })),

      setTripKitStep: (step) => set({ tripKitStep: step }),

      addChatMessage: (message) =>
        set((state) => ({
          chatMessages: [
            ...state.chatMessages,
            {
              ...message,
              id: `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
              timestamp: Date.now(),
            },
          ],
        })),

      setChatMessages: (messages) => set({ chatMessages: messages }),

      resetTripKitChat: () =>
        set({
          tripKitProfile: {} as TripKitProfile,
          tripKitStep: 'greeting' as TripKitStep,
          chatMessages: [],
        }),

      resetSession: () => set(initialState),
    }),
    {
      name: 'tripkit-vibe-storage',
      partialize: (state) => ({
        sessionId: state.sessionId,
        preferences: state.preferences,
        // tripKitProfile만 저장 (generate 페이지에서 사용)
        // chatMessages, tripKitStep은 저장하지 않음 (새로고침 시 새 대화 시작)
        tripKitProfile: state.tripKitProfile,
        selectedConcept: state.selectedConcept,
        selectedDestination: state.selectedDestination,
        imageGenerationContext: state.imageGenerationContext,
      }),
    }
  )
);
