from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import csv
from datetime import datetime, timedelta
import requests
import feedparser
import os
import sys
import time
from urllib.parse import quote, parse_qs, urlparse
import pytz
import re

class NewsHandler(SimpleHTTPRequestHandler):
    # RSS 피드 URL 목록
    RSS_FEEDS = {
        # IT/기술 전문 매체
        'etnews': 'https://www.etnews.com/rss/section/901',      # 전자신문 AI/SW
        'zdnet': 'https://feeds.feedburner.com/zdkorea',         # ZDNet Korea
        'dt': 'https://www.dt.co.kr/rss/all.xml',               # 디지털타임스
        'bloter': 'https://www.bloter.net/feed',                # 블로터
        'aitimes': 'https://www.aitimes.kr/rss/allArticle.xml',  # AI타임스
        'itworld': 'https://www.itworld.co.kr/rss/feed',        # IT World
        'itdonga': 'https://it.donga.com/feeds/rss/news/',      # IT동아
        
        # 주요 종합 언론사 IT/과학 섹션
        'chosun_tech': 'https://www.chosun.com/arc/outboundfeeds/rss/category/it-science/',  # 조선일보 IT/과학
        'joongang_sci': 'https://rss.joins.com/joins_it_list.xml',  # 중앙일보 IT
        'mk_tech': 'https://www.mk.co.kr/rss/30000001/',        # 매일경제 기술
        'hankyung_tech': 'https://rss.hankyung.com/feed/it',    # 한국경제 IT/과학
        'donga_tech': 'https://rss.donga.com/science.xml',      # 동아일보 IT/과학
    }

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # API 요청 처리
        if path == '/api/news':
            self.handle_api_request(parsed_url)
        # 정적 파일 처리
        elif path == '/':
            self.serve_index()
        else:
            super().do_GET()

    def serve_index(self):
        try:
            with open('index.html', 'rb') as f:
                content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
        except Exception as e:
            print(f"Error serving index.html: {e}")
            self.send_error(404, "File not found")

    def handle_api_request(self, parsed_url):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Parse query parameters
            query = parse_qs(parsed_url.query)
            page = int(query.get('page', ['1'])[0])
            per_page = int(query.get('per_page', ['9'])[0])
            
            news_data = self.get_news_data()
            
            # Calculate pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_data = news_data[start_idx:end_idx]
            
            response = {
                'articles': paginated_data,
                'total': len(news_data),
                'page': page,
                'per_page': per_page,
                'total_pages': (len(news_data) + per_page - 1) // per_page
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
        except Exception as e:
            print(f"Error handling API request: {e}")
            self.send_error(500, "Internal Server Error")

    def do_POST(self):
        if self.path == '/api/shutdown':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 서버 종료를 위한 응답
            self.wfile.write(json.dumps({"status": "shutting down"}).encode())
            
            # 서버 종료
            def shutdown():
                self.server.shutdown()
            
            # 1초 후에 서버 종료
            import threading
            threading.Timer(1, shutdown).start()
        else:
            self.send_error(404, "Not Found")

    def get_news_data(self):
        csv_file = 'news.csv'
        
        print("\n=== 뉴스 데이터 수집 시작 ===\n")
        
        all_articles = []
        
        # 각 RSS 피드에서 기사 수집
        for source, feed_url in self.RSS_FEEDS.items():
            try:
                articles = self.parse_rss_feed(source, feed_url)
                if articles:
                    all_articles.extend(articles)
                time.sleep(2)  # 요청 간 딜레이 증가
            except Exception as e:
                print(f"피드 처리 중 오류 발생 ({source}): {e}")
                continue
        
        print(f"\n=== 총 {len(all_articles)}개의 기사 수집 완료 ===")
        
        if all_articles:
            # 중복 제거
            unique_articles = self.remove_duplicates(all_articles)
            print(f"중복 제거 후 {len(unique_articles)}개의 기사 남음")
            
            # AI 관련 기사 필터링
            ai_articles = self.filter_ai_articles(unique_articles)
            print(f"AI 관련 기사 필터링 후 {len(ai_articles)}개의 기사 남음")
            
            if not ai_articles:
                print("경고: AI 관련 기사를 찾을 수 없습니다!")
                return []
            
            # 날짜순 정렬
            ai_articles.sort(key=lambda x: x['date'], reverse=True)
            
            # CSV 저장
            self.save_to_csv(ai_articles, csv_file)
            return ai_articles
        else:
            print("수집된 기사가 없습니다!")
            return []

    def parse_rss_feed(self, source, feed_url):
        articles = []
        kst = pytz.timezone('Asia/Seoul')
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"\n시도: {source} - {feed_url}")
            
            try:
                response = requests.get(feed_url, headers=headers, timeout=10)
                response.raise_for_status()  # HTTP 에러 체크
                feed = feedparser.parse(response.content)
            except requests.exceptions.RequestException as e:
                print(f"RSS 피드 요청 실패 ({source}): {e}")
                return articles
            
            if not feed.entries:
                print(f"경고: {source}에서 기사를 찾을 수 없습니다")
                return articles
                
            print(f"성공: {source}에서 {len(feed.entries)}개의 기사를 찾았습니다")
            
            # 5일 전 날짜 계산 (한국 시간 기준)
            five_days_ago = datetime.now(kst) - timedelta(days=5)
            
            for entry in feed.entries:
                try:
                    # 발행일 파싱 및 KST로 변환
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        pub_date = pytz.utc.localize(pub_date).astimezone(kst)
                    else:
                        print(f"경고: {source}의 기사에 발행일이 없습니다. 현재 시간으로 설정합니다.")
                        pub_date = datetime.now(kst)
                    
                    # 5일 이내의 기사만 포함
                    if pub_date >= five_days_ago:
                        # 기사 내용 가져오기
                        description = ""
                        if hasattr(entry, 'description'):
                            description = entry.description
                        elif hasattr(entry, 'summary'):
                            description = entry.summary
                        
                        article = {
                            'title': entry.title,
                            'url': entry.link,
                            'source': source,
                            'summary': description,
                            'date': pub_date.isoformat(),
                            'keyword': 'AI',
                            'timestamp': datetime.now(kst).isoformat()
                        }
                        articles.append(article)
                        print(f"파싱 완료: {article['title']} ({article['date']})")
                    
                except Exception as e:
                    print(f"RSS 항목 처리 중 오류 발생 ({source}): {e}")
                    continue
                    
        except Exception as e:
            print(f"RSS 피드 파싱 중 오류 발생 ({source}): {e}")
            
        return articles

    def filter_ai_articles(self, articles):
        """AI 관련 키워드가 포함된 기사만 필터링"""
        ai_keywords = [
            'AI', '인공지능', '머신러닝', '딥러닝', 'ChatGPT', 'LLM', '생성형',
            '대규모 언어모델', '강화학습', 'GPT', '생성형AI', '생성 AI',
            '인공지능챗봇', 'AI챗봇', '초거대AI', '초거대 AI', '생성적 AI',
            '로봇', '자율주행', '음성인식', '이미지생성', '영상생성',
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', '신경망', '딥페이크', 'deepfake', '클로드',
            '바드', 'Bard', 'Claude', 'Gemini', '제미나이', '코파일럿',
            'Copilot', '알파고', 'AlphaGo', '달리', 'DALL-E', '미드저니',
            'Midjourney', '스테이블 디퓨전', 'Stable Diffusion'
        ]
        
        # 제외할 키워드 (오탐을 줄이기 위함)
        exclude_keywords = [
            '부고', '인사', '동정', '장모상', '별세', '부음'
        ]
        
        filtered_articles = []
        for article in articles:
            title = article['title'].lower()
            summary = article['summary'].lower()
            
            # 제외 키워드가 포함된 기사는 건너뛰기
            if any(exclude in title or exclude in summary for exclude in exclude_keywords):
                print(f"제외 키워드로 인해 제외된 기사: {article['title']}")
                continue
            
            # 정규표현식을 사용하여 더 정확한 키워드 매칭
            for keyword in ai_keywords:
                # 영문 키워드는 단어 경계를 확인
                if re.match(r'^[a-zA-Z]', keyword):
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                # 한글 키워드는 정확한 매칭
                else:
                    pattern = re.escape(keyword.lower())
                
                if (re.search(pattern, title) or re.search(pattern, summary)):
                    print(f"\nAI 관련 기사 발견: {article['title']}")
                    print(f"매칭된 키워드: {keyword}")
                    print(f"출처: {article['source']}")
                    filtered_articles.append(article)
                    break
                
        return filtered_articles

    def remove_duplicates(self, articles):
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
                
        return unique_articles

    def save_to_csv(self, articles, filename):
        if not articles:
            return
            
        fieldnames = ['title', 'url', 'source', 'summary', 'date', 'keyword', 'timestamp']
        
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(articles)
                
            print(f"Saved {len(articles)} articles to {filename}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")

def run_server():
    port = 8000
    server_address = ('', port)
    
    try:
        httpd = HTTPServer(server_address, NewsHandler)
        print(f"Server running on port {port}")
        httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_server() 