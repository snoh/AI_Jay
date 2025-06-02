# CVCforSANS_HW#1 - AI 뉴스레터 자동 수집 웹페이지

## 프로젝트 개요
이 프로젝트는 AI 관련 국내 뉴스레터를 자동으로 수집하고 정리하는 웹페이지를 구현한 것입니다.

## 주요 기능
- AI 관련 국내 뉴스레터 자동 수집
- 3x3 그리드 레이아웃의 뉴스레터 카드 표시
- 종합 요약 기사 섹션
- 검색 기능
- 페이지네이션

## 기술 스택
### 프론트엔드
- Next.js
- TailwindCSS
- 반응형 그리드 레이아웃

### 백엔드
- FastAPI
- Python 웹 스크래핑 (BeautifulSoup4, requests)
- CSV 파일 처리 (pandas)

## 프로젝트 구조
```
CVCforSANS_HW#1/
├── docs/                    # 문서 파일들
├── frontend/               # 프론트엔드 관련 파일들
├── backend/               # 백엔드 관련 파일들
├── data/                  # 데이터 파일들
├── debug/                 # 디버깅 관련 파일들
└── screenshots/          # 스크린샷 파일들
```

## 설치 및 실행 방법
1. 백엔드 설정
```bash
cd backend
pip install -r requirements.txt
python server.py
```

2. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

## 라이선스
MIT License 