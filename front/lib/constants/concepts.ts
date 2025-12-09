import type { Concept } from '@/lib/types';

export type FilmType = 'FUJI' | 'Kodak' | 'Canon' | 'Ricoh' | 'Nikon' | 'Pentax';

export interface ConceptData {
  id: Concept;
  name: string;
  nameKo: string;
  tagline: string;
  description: string;
  image: string;
  sampleImages: string[];
  filmType: FilmType;
  filmStyleDescription: string;
  recommendedFilms: string[];
  cameraModels: string[];
  outfitStyle: string;
  keywords: string[];
}

// Film style descriptions by type
export const FILM_STYLE_DESCRIPTIONS: Record<FilmType, string> = {
  FUJI: 'Fujifilm-style photograph with vibrant greens and cool blues, crisp tones, clean grain, and airy atmosphere.',
  Kodak: 'Kodak Portra-style soft pastel colors, warm golden highlights, creamy shadows, and nostalgic analog tones.',
  Canon: 'Canon-style warm soft tones, creamy skin tones, smooth contrast, and emotional rendering.',
  Ricoh: 'Ricoh GR-style high micro-contrast, muted colors, sharp details, and street photography mood.',
  Nikon: 'Nikon-style natural color accuracy, deep contrast, high sharpness, and realistic tones.',
  Pentax: 'Pentax vintage film look with matte tones, warm shadows, noticeable grain, and emotional softness.',
};

export const CONCEPTS: ConceptData[] = [
  {
    id: 'flaneur',
    name: 'Flâneur',
    nameKo: '플라뇌르',
    tagline: '지도 없이 걷는 낭만',
    description:
      '19세기 파리의 산책자처럼, 목적 없이 도시를 거닐며 발견하는 순간들. 책을 손에 들고 카페에 앉아 사람들을 관찰하고, 골목길에서 우연히 마주치는 아름다움을 기록합니다.',
    image: '/images/concepts/flaneur/hero.jpg',
    sampleImages: [
      '/images/concepts/flaneur/sample-1.jpg',
      '/images/concepts/flaneur/sample-2.jpg',
      '/images/concepts/flaneur/sample-3.jpg',
    ],
    filmType: 'Ricoh',
    filmStyleDescription: FILM_STYLE_DESCRIPTIONS['Ricoh'],
    recommendedFilms: ['Kodak Portra 400', 'Ilford HP5 Plus'],
    cameraModels: ['Ricoh GR III', 'Leica M6', 'Contax G2'],
    outfitStyle: '미니멀리스트 도시 스타일, 중성 톤',
    keywords: ['urban', 'literary', 'cafe', 'street', 'intellectual'],
  },
  {
    id: 'filmlog',
    name: 'Film Log',
    nameKo: '필름 로그',
    tagline: '빈티지 감성 기록',
    description:
      '따뜻한 햇살 아래 필름 카메라를 들고, 일상의 순간들을 빈티지 감성으로 담아냅니다. 레트로 카페, 오래된 서점, 그리고 골목 사이로 스며드는 오후의 빛.',
    image: '/images/concepts/filmlog/hero.jpg',
    sampleImages: [
      '/images/concepts/filmlog/sample-1.jpg',
      '/images/concepts/filmlog/sample-2.jpg',
      '/images/concepts/filmlog/sample-3.jpg',
    ],
    filmType: 'Kodak',
    filmStyleDescription: FILM_STYLE_DESCRIPTIONS['Kodak'],
    recommendedFilms: ['Kodak ColorPlus 200', 'Fujifilm Superia 400'],
    cameraModels: ['Canon AE-1', 'Pentax K1000', 'Nikon FM2'],
    outfitStyle: '레트로 캐주얼, 따뜻한 컬러',
    keywords: ['vintage', 'warm', 'nostalgic', 'golden hour', 'retro'],
  },
  {
    id: 'midnight',
    name: 'Midnight',
    nameKo: '미드나잇',
    tagline: '과거 예술가와의 조우',
    description:
      '밤의 도시를 걷는 예술적 시간 여행. 1920년대 파리의 살롱, 헤밍웨이가 글을 쓰던 카페, 피카소가 그림을 그리던 골목. 보헤미안의 자유로운 영혼으로.',
    image: '/images/concepts/midnight/hero.jpg',
    sampleImages: [
      '/images/concepts/midnight/sample-1.jpg',
      '/images/concepts/midnight/sample-2.jpg',
      '/images/concepts/midnight/sample-3.jpg',
    ],
    filmType: 'Pentax',
    filmStyleDescription: FILM_STYLE_DESCRIPTIONS['Pentax'],
    recommendedFilms: ['Kodak Tri-X 400', 'Ilford Delta 3200'],
    cameraModels: ['Pentax K1000', 'Hasselblad 500C/M', 'Rolleiflex'],
    outfitStyle: '아티스틱, 드라마틱, 레이어드 텍스처',
    keywords: ['artistic', 'bohemian', 'dramatic', 'night', 'cultural'],
  },
  {
    id: 'pastoral',
    name: 'Pastoral',
    nameKo: '파스토럴',
    tagline: '자연을 닮은 고요',
    description:
      '도시를 벗어나 들판, 숲, 강가, 작은 마을을 천천히 걸으며 자연이 만들어주는 색과 냄새를 담아내는 여행. 필름 카메라 특유의 소프트한 색 번짐, 연한 그레인, 자연광의 드리프트가 잘 어울립니다.',
    image: '/images/concepts/pastoral/hero.jpg',
    sampleImages: [
      '/images/concepts/pastoral/sample-1.jpg',
      '/images/concepts/pastoral/sample-2.jpg',
      '/images/concepts/pastoral/sample-3.jpg',
    ],
    filmType: 'FUJI',
    filmStyleDescription: FILM_STYLE_DESCRIPTIONS['FUJI'],
    recommendedFilms: ['Fujifilm Pro 400H', 'Kodak Ektar 100'],
    cameraModels: ['Nikon F3', 'Pentax Spotmatic', 'Canon A-1'],
    outfitStyle: '내추럴 린넨, 그린·베이지 팔레트, 자연친화적 텍스처',
    keywords: ['nature', 'pastoral', 'calm', 'river', 'green', 'sunlight', 'slow'],
  },
  {
    id: 'noir',
    name: 'Noir',
    nameKo: '느와르',
    tagline: '빛과 어둠 사이, 도시의 또 다른 얼굴',
    description:
      '검은 그림자와 빛이 만들어내는 강렬한 대비, 차가운 네온, 젖은 아스팔트에 번지는 반사광. 인물 혹은 거리의 실루엣을 중심으로 만들어지는 영화 같은 밤 여행.',
    image: '/images/concepts/noir/hero.jpg',
    sampleImages: [
      '/images/concepts/noir/sample-1.jpg',
      '/images/concepts/noir/sample-2.jpg',
      '/images/concepts/noir/sample-3.jpg',
    ],
    filmType: 'Nikon',
    filmStyleDescription: FILM_STYLE_DESCRIPTIONS['Nikon'],
    recommendedFilms: ['Cinestill 800T', 'Ilford Delta 3200'],
    cameraModels: ['Ricoh GR', 'Leica Q2 Monochrom', 'Fujifilm X100V'],
    outfitStyle: '블랙 레더, 메탈릭 악세서리, 미니멀 다크톤',
    keywords: ['noir', 'night', 'neon', 'shadow', 'cinematic', 'mystery'],
  },
  {
    id: 'seaside',
    name: 'Seaside Memoir',
    nameKo: '씨사이드 메모아',
    tagline: '바람, 파도, 그리고 나의 이야기',
    description:
      '바닷바람, 젖은 모래, 파도의 미묘한 색을 담아내는 지중해·동해·포르투갈 해안의 서정적 감성. 햇빛 아래 반짝이는 물결과 흐릿한 필름 색감을 조합한 "추억이 되는 여행" 시나리오.',
    image: '/images/concepts/seaside/hero.jpg',
    sampleImages: [
      '/images/concepts/seaside/sample-1.jpg',
      '/images/concepts/seaside/sample-2.jpg',
      '/images/concepts/seaside/sample-3.jpg',
    ],
    filmType: 'Canon',
    filmStyleDescription: FILM_STYLE_DESCRIPTIONS['Canon'],
    recommendedFilms: ['Kodak Gold 200', 'Fujifilm C200'],
    cameraModels: ['Olympus Mju-II', 'Minolta Hi-Matic', 'Contax T2'],
    outfitStyle: '화이트·블루 계열, 린넨 셔츠, 라탄 가방, 내추럴한 바다 색 텍스처',
    keywords: ['seaside', 'ocean', 'memory', 'sunlight', 'blue', 'breeze', 'calm'],
  },
];

export function getConceptById(id: Concept): ConceptData | undefined {
  return CONCEPTS.find((concept) => concept.id === id);
}

// Generate film style JSON for a given film type
export function getFilmStyleJson(filmType: FilmType): {
  film_type: FilmType;
  film_style_description: string;
} {
  return {
    film_type: filmType,
    film_style_description: FILM_STYLE_DESCRIPTIONS[filmType],
  };
}
