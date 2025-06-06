from flask import Flask, render_template_string
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)
CORS(app)

# HTML 템플릿
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>뉴스 그리드</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Noto Sans KR', sans-serif;
        }
        body {
            background: linear-gradient(135deg, #e0e7ff 0%, #fff 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #1a237e;
            margin-bottom: 2rem;
            font-size: 2.5rem;
            font-weight: 700;
        }
        .news-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            padding: 1rem;
        }
        .news-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .news-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        .source {
            color: #1a237e;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        .title {
            color: #333;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 1rem;
        }
        .news-card a {
            text-decoration: none;
            color: inherit;
        }
        .empty-card {
            background: transparent;
            box-shadow: none;
            border: 2px dashed #c5cae9;
        }
        @media (max-width: 768px) {
            .news-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 480px) {
            .news-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>오늘의 주요 해외 뉴스와 심리·과학 뉴스</h1>
        <div class="news-grid">
            {% for article in news %}
            {% if article %}
            <div class="news-card">
                <a href="{{ article.link }}" target="_blank" rel="noopener noreferrer">
                    <div class="source">{{ article.source }}</div>
                    <div class="title">{{ article.title }}</div>
                </a>
            </div>
            {% else %}
            <div class="news-card empty-card"></div>
            {% endif %}
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

def get_npr_news():
    try:
        response = requests.get('https://www.npr.org/')
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        for article in soup.select('.story-wrap')[:10]:
            title = article.select_one('.title')
            if title:
                title_text = title.text.strip()
                link = article.select_one('a')['href']
                if not link.startswith('http'):
                    link = f'https://www.npr.org{link}'
                articles.append({
                    'title': title_text,
                    'link': link,
                    'source': 'NPR'
                })
        return articles
    except Exception as e:
        print(f"NPR Error: {str(e)}")
        return []

def get_npr_health_news():
    try:
        response = requests.get('https://www.npr.org/sections/health/')
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        for article in soup.select('.story-wrap')[:10]:
            title = article.select_one('.title')
            if title:
                title_text = title.text.strip()
                link = article.select_one('a')['href']
                if not link.startswith('http'):
                    link = f'https://www.npr.org{link}'
                articles.append({
                    'title': title_text,
                    'link': link,
                    'source': 'NPR Health'
                })
        return articles
    except Exception as e:
        print(f"NPR Health Error: {str(e)}")
        return []

def get_science_daily_news():
    try:
        response = requests.get('https://www.sciencedaily.com/news/mind_brain/psychology/')
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        for article in soup.select('.latest-head')[:10]:
            title = article.text.strip()
            link = article.find('a')['href']
            if not link.startswith('http'):
                link = f'https://www.sciencedaily.com{link}'
            articles.append({
                'title': title,
                'link': link,
                'source': 'Science Daily'
            })
        return articles
    except Exception as e:
        print(f"Science Daily Error: {str(e)}")
        return []

def get_apa_news():
    try:
        response = requests.get('https://www.apa.org/news/psycport')
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        for article in soup.select('.news-item')[:10]:
            title = article.select_one('.title')
            if title:
                title_text = title.text.strip()
                link = article.select_one('a')['href']
                if not link.startswith('http'):
                    link = f'https://www.apa.org{link}'
                articles.append({
                    'title': title_text,
                    'link': link,
                    'source': 'APA'
                })
        return articles
    except Exception as e:
        print(f"APA Error: {str(e)}")
        return []

@app.route('/')
def get_news():
    # 각 소스별로 최대 10개씩 긁어오기
    sources = [
        get_npr_news(),
        get_npr_health_news(),
        get_science_daily_news(),
        get_apa_news()
    ]
    news = []
    seen_links = set()
    idx = 0
    # 라운드로빈 방식으로 9개 채우기
    while len(news) < 9:
        added = False
        for src in sources:
            if idx < len(src):
                article = src[idx]
                if article['link'] not in seen_links:
                    news.append(article)
                    seen_links.add(article['link'])
                    if len(news) == 9:
                        break
                added = True
        if not added:
            break  # 더 이상 추가할 뉴스가 없음
        idx += 1
    return render_template_string(HTML_TEMPLATE, news=news)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 