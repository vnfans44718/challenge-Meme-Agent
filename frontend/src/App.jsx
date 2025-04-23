import React, { useState, useRef } from 'react';

export default function MemeRecommendationApp() {
  const [emotion, setEmotion] = useState('');
  const [memes, setMemes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const buttonRef = useRef(null);

  const fetchMemes = async () => {
    if (!emotion.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(
        `/api/memes?emotion_text=${encodeURIComponent(emotion)}`
      );
      const { memes: list } = await res.json();
      setMemes(list || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const shareToInstagramStory = (url) => {
    const shareUrl = `https://www.instagram.com/create/story/?url=${encodeURIComponent(url)}`;
    window.open(shareUrl, '_blank');
  };

  const styles = {
    container: {
      maxWidth: 960,
      margin: "0 auto",
      padding: 20,
      fontFamily: 'sans-serif',
      minHeight: '100vh',
      background: '#f7f7f7',
    },
    header: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 , color: '#000' },
    control: { display: 'flex', marginBottom: 24 },
    input: {
      flex: 1,
      padding: 8,
      border: '1px solid #ccc',
      borderRadius: 4,
      background: '#fff',
      color: '#000', 
    },
    button: {
      marginLeft: 8,
      padding: '8px 16px',
      background: '#007bff',
      color: '#fff',
      border: 'none',
      borderRadius: 4,
      cursor: 'pointer',
    },
    grid: { display: 'flex', flexWrap: 'wrap', gap: 16 },
    card: {
      width: 'calc(25% - 16px)',
      background: '#fff',
      borderRadius: 4,
      overflow: 'hidden',
      boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
      cursor: 'pointer',
    },
    thumbnail: {
      width: '100%',
      height: 200,
      objectFit: 'cover',
      background: '#eee',
    },
    modalOverlay: {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    },
    modalContent: {
      position: 'relative',
      background: '#fff',
      borderRadius: 8,
      padding: 16,
      maxWidth: '90%',
      maxHeight: '90%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
    },
    modalImage: {
      maxWidth: '100%',
      maxHeight: '80vh',
      marginBottom: 12,
    },
    storyButton: {
      padding: '8px 16px',
      background: '#405de6',
      color: '#fff',
      border: 'none',
      borderRadius: 4,
      cursor: 'pointer',
      fontSize: 16,
    },
    closeButton: {
      position: 'absolute',
      top: 8,
      right: 8,
      background: 'transparent',
      border: 'none',
      fontSize: 24,
      color: '#333',
      cursor: 'pointer',
    },
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>무한도전 밈 추천기</h1>
      <form
      style={styles.control}
      onSubmit={(e) => {
        e.preventDefault();
        fetchMemes();
      }}
    >
      <input
        type="text"
        placeholder="문장을 입력하세요 (AI가 감정 분석 → 밈 추천)"
        value={emotion}
        onChange={(e) => setEmotion(e.target.value)}
        style={styles.input}
      />
      <button
        type="submit"               // ← submit 타입으로 변경
        disabled={loading}
        style={{ ...styles.button, opacity: loading ? 0.6 : 1 }}
      >
        {loading ? '추천 중...' : '추천 받기'}
      </button>
    </form>
      <div style={styles.grid}>
        {memes.map((m) => (
          <div
            key={m.id}
            style={styles.card}
            onClick={() => setSelectedImage(m.id)}
          >
            <img
              src={m.id}
              alt={m.title}
              style={styles.thumbnail}
            />
          </div>
        ))}
      </div>

      {selectedImage && (
        <div style={styles.modalOverlay} onClick={() => setSelectedImage(null)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <button
              style={styles.closeButton}
              onClick={() => setSelectedImage(null)}
            >
              &times;
            </button>
            <img
              src={selectedImage}
              alt="Enlarged meme"
              style={styles.modalImage}
            />
            <button
              style={styles.storyButton}
              onClick={() => shareToInstagramStory(selectedImage)}
            >
              인스타 스토리 공유
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
