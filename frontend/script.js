// 뉴스 데이터를 가져오는 함수
async function fetchNews() {
    try {
        const response = await fetch('/api/news');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Received news data:', data); // 디버깅을 위한 로그
        displayNews(data);
    } catch (error) {
        console.error('뉴스를 가져오는데 실패했습니다:', error);
        document.getElementById('newsGrid').innerHTML = '<div class="error">뉴스를 불러오는데 실패했습니다. 서버가 실행 중인지 확인해주세요.</div>';
    }
}

// 뉴스를 화면에 표시하는 함수
function displayNews(newsItems) {
    const newsGrid = document.getElementById('newsGrid');
    newsGrid.innerHTML = '';

    if (!newsItems || newsItems.length === 0) {
        newsGrid.innerHTML = '<div class="error">표시할 뉴스가 없습니다.</div>';
        return;
    }

    newsItems.forEach(news => {
        const newsCard = document.createElement('div');
        newsCard.className = 'news-card';
        newsCard.innerHTML = `
            <h2>${news.title}</h2>
            <div class="source">${news.source}</div>
            <div class="summary">${news.summary}</div>
        `;
        newsGrid.appendChild(newsCard);
    });
}

// 검색 기능
function searchNews() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const newsCards = document.querySelectorAll('.news-card');

    newsCards.forEach(card => {
        const title = card.querySelector('h2').textContent.toLowerCase();
        const summary = card.querySelector('.summary').textContent.toLowerCase();
        
        if (title.includes(searchTerm) || summary.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// 서버 종료 함수
async function shutdownServer() {
    try {
        const response = await fetch('/api/shutdown', { method: 'POST' });
        if (response.ok) {
            alert('서버가 종료되었습니다.');
            window.close();
        }
    } catch (error) {
        console.error('서버 종료 실패:', error);
        alert('서버 종료에 실패했습니다.');
    }
}

// 페이지 로드 시 뉴스 데이터 가져오기
document.addEventListener('DOMContentLoaded', fetchNews); 