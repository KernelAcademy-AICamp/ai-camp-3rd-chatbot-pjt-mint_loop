// User Types
export interface UserPreferences {
  mood?: 'romantic' | 'adventurous' | 'nostalgic' | 'peaceful';
  aesthetic?: 'urban' | 'nature' | 'vintage' | 'modern';
  duration?: 'short' | 'medium' | 'long';
  interests?: Interest[];
  concept?: Concept;
  // Chat에서 수집한 여행 장면 정보
  travelDestination?: string;  // 여행지 (예: "파리 몽마르트르")
  travelScene?: string;        // 장면 설명 (예: "카페 테라스에서 책을 읽는 모습")
}

export type Interest =
  | 'photography'
  | 'food'
  | 'art'
  | 'history'
  | 'nature'
  | 'architecture';

export type Concept = 'flaneur' | 'filmlog' | 'midnight' | 'pastoral' | 'noir' | 'seaside';

export type ConversationStep =
  | 'init'
  | 'mood'
  | 'aesthetic'
  | 'duration'
  | 'interests'
  | 'destination'  // 새로운 단계: 여행 장면 설명 수집
  | 'complete';

// Message Types
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

// Destination Types
export interface Destination {
  id: string;
  name: string;
  city: string;
  country: string;
  description: string;
  matchReason: string;
  bestTimeToVisit: string;
  photographyScore: number;
  transportAccessibility: 'easy' | 'moderate' | 'challenging';
  safetyRating: number;
  estimatedBudget?: '$' | '$$' | '$$$';
  tags?: string[];
  image?: string;
  thumbnail?: string;
  // 숨겨진 로컬 스폿을 위한 새 필드
  localVibe?: string;           // 현지 분위기 설명
  activities?: Activity[];       // 추천 액티비티/경험
  storyPrompt?: string;          // 이 장소에서의 스토리 제안
  whyHidden?: string;            // 왜 숨겨진 명소인지
  photographyTips?: string[];    // 사진 촬영 팁
  // Google Places API 연동 데이터
  placeDetails?: PlaceDetails;   // Google Places 상세 정보
}

// Activity/Experience 타입
export interface Activity {
  name: string;
  description: string;
  duration?: string;
  bestTime?: string;
  localTip?: string;
  photoOpportunity?: string;
}

// Google Places API 타입
export interface PlacePhoto {
  reference: string;
  url?: string;
  width?: number;
  height?: number;
}

export interface PlaceReview {
  author?: string;
  rating?: number;
  text?: string;
  time?: string;
}

export interface PlaceDetails {
  place_id?: string;
  google_name?: string;
  google_address?: string;
  phone?: string;
  website?: string;
  google_maps_url?: string;
  rating?: number;
  user_ratings_total?: number;
  price_level?: number;
  opening_hours?: string[];
  is_open_now?: boolean;
  photos?: PlacePhoto[];
  reviews?: PlaceReview[];
  location?: {
    lat: number;
    lng: number;
  };
}

// Hidden Spot Types
export interface HiddenSpot {
  id: string;
  name: string;
  address: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  description: string;
  photographyTips: string[];
  bestTimeToVisit: string;
  estimatedDuration: string;
  nearbyAmenities: string[];
  accessibilityNotes: string;
  crowdLevel: 'low' | 'medium' | 'high';
  localTip?: string;
  filmRecommendations: FilmRecommendation[];
  safetyNotes?: string;
  image?: string;
}

export interface FilmRecommendation {
  filmStock: string;
  reason: string;
}

// Styling Types
export interface StylingRecommendation {
  cameraModel: string;
  cameraDescription?: string;
  rentalInfo?: {
    available: boolean;
    estimatedCost: string;
    whereToRent: string;
  };
  filmStock: FilmStock;
  cameraSettings: CameraSettings;
  outfitSuggestions: OutfitSuggestion;
  props: Prop[];
  bestAngles: Angle[];
  locationSpecificTips?: {
    localInsights: string;
    weatherConsiderations: string;
    crowdAvoidance: string;
    seasonalNotes: string;
  };
}

export interface FilmStock {
  name: string;
  iso: number;
  colorProfile: string;
  characteristics: string[];
  sampleImages?: string[];
  priceRange: '$' | '$$' | '$$$';
  exposuresPerRoll?: number;
  bestFor?: string[];
}

export interface CameraSettings {
  aperture: string;
  shutterSpeed: string;
  iso: number;
  focusMode: 'auto' | 'manual';
  meteringMode: string;
  lightingNotes: string;
  advancedTips?: string[];
}

export interface OutfitSuggestion {
  colorPalette: string[];
  colorNames?: string[];
  style: string;
  specificItems: string[];
  seasonalNotes: string;
  avoidItems?: string[];
  shoppingTips?: string;
}

export interface Prop {
  name: string;
  purpose: string;
  whereToFind: string;
  optional: boolean;
  stylingTips?: string;
}

export interface Angle {
  description: string;
  visualExample?: string;
  technique: string;
  bestLighting: string;
  cameraHeight?: string;
  diagramUrl?: string;
}

// API Types
export interface ChatRequest {
  sessionId: string;
  message: string;
  currentStep: ConversationStep;
  preferences: UserPreferences;
}

export interface ChatResponse {
  reply: string;
  nextStep: ConversationStep;
  isComplete: boolean;
  recommendations: Destination[] | null;
  sessionId: string;
}

export interface ImageGenerationRequest {
  locationId: string;
  locationName: string;
  locationDescription: string;
  concept: Concept;
  filmStock: string;
  outfitStyle: string;
  timeOfDay?: 'morning' | 'noon' | 'sunset' | 'night';
  composition?: 'center' | 'left-third' | 'right-third';
  expression?: string;
}

export interface ImageGenerationResponse {
  imageUrl?: string;
  prompt?: string;
  generationTime?: number;
  status: 'success' | 'pending' | 'failed';
  taskId?: string;
  pollUrl?: string;
  errorMessage?: string;
}
