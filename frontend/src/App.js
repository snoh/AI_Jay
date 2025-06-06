import React, { useState, useEffect } from 'react';
import { Container, Grid, Card, CardContent, Typography, Box, CircularProgress, CardActionArea } from '@mui/material';

function App() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/news');
        if (!response.ok) {
          throw new Error('뉴스를 가져오는데 실패했습니다.');
        }
        const data = await response.json();
        setNews(data.slice(0, 9)); // 9개만 보여줌
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #e0e7ff 0%, #fff 100%)', py: 6 }}>
      <Container maxWidth="md">
        <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ fontWeight: 700, color: '#1a237e', mb: 4 }}>
          오늘의 뉴스 3 x 3
        </Typography>
        <Grid container spacing={4}>
          {news.map((article, index) => (
            <Grid item xs={12} sm={4} md={4} key={index}>
              <Card
                sx={{
                  height: 220,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: 4,
                  borderRadius: 3,
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-8px) scale(1.03)',
                    boxShadow: 8,
                  },
                  background: 'rgba(255,255,255,0.95)'
                }}
              >
                <CardActionArea component="a" href={article.link} target="_blank" rel="noopener noreferrer" sx={{ height: '100%' }}>
                  <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <Typography variant="subtitle2" color="primary" gutterBottom sx={{ fontWeight: 600 }}>
                      {article.source}
                    </Typography>
                    <Typography variant="h6" component="h2" sx={{ fontWeight: 700, mb: 1, color: '#222' }}>
                      {article.title}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}

export default App; 