import React, { useState } from "react";
import logo from "./assets/infinite-meme-logo.png";

export default function MemeRecommendationApp() {
  const [emotion, setEmotion] = useState("");
  const [memes, setMemes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const isInitial = memes.length === 0;

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
    const shareUrl = `https://www.instagram.com/create/story/?url=${encodeURIComponent(
      url
    )}`;
    window.open(shareUrl, "_blank");
  };

  const styles = {
    // 초기화면용 전체 중앙 레이아웃
    outer: {
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      background: "#f7f7f7",
      fontFamily: "sans-serif",
    },
    // 검색 후 일반 컨테이너 (왼쪽 정렬)
    container: {
      maxWidth: 960,
      margin: "40px auto",
      padding: 20,
      background: "#f7f7f7",
      fontFamily: "sans-serif",
      minHeight: "100vh",
      textAlign: "left",
    },
    // 헤더 그룹 (제목 + 로고) — 항상 왼쪽
    headerGroup: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      width: "80%",
      maxWidth: 600,
      justifyContent: isInitial ? "flex-start" : "flex-start",
      margin: isInitial
        ? "0 auto 24px auto" // 초기: 가로 중앙 + 아래 24px
        : "0 0 24px 0", // 검색 후: 좌측 붙이고 아래만 24px
      cursor: "pointer",
    },
    header: {
      fontSize: 28,
      fontWeight: "bold",
      color: "#000",
      margin: 0,
    },
    logo: {
      width: 48,
      height: 48,
    },
    // 검색 폼
    form: {
      display: "flex",
      width: isInitial ? "80%" : "80%",
      maxWidth: 600,
      margin: isInitial ? "0 auto 24px auto" : "0 0 40px 0",
      justifyContent: isInitial ? "center" : "flex-start",
    },
    input: {
      flex: 1,
      padding: 10,
      border: "1px solid #ccc",
      borderRadius: 4,
      background: "#fff",
      color: "#000",
      fontSize: 16,
    },
    button: {
      marginLeft: 8,
      padding: "10px 20px",
      background: "#007bff",
      color: "#fff",
      border: "none",
      borderRadius: 4,
      cursor: "pointer",
      fontSize: 16,
    },
    // 추천 결과 그리드 (왼쪽 정렬)
    grid: {
      display: "flex",
      flexWrap: "wrap",
      gap: 16,
      justifyContent: "flex-start",
      alignItems: "flex-start",
    },
    card: {
      width: "calc(25% - 16px)",
      height: 200,
      background: "#fff",
      borderRadius: 4,
      overflow: "hidden",
      boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
      cursor: "pointer",
    },
    thumbnail: {
      width: "100%",
      height: "100%",
      objectFit: "cover",
      background: "#eee",
    },
    // 모달
    modalOverlay: {
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0,0,0,0.8)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
    },
    modalContent: {
      position: "relative",
      background: "#fff",
      borderRadius: 8,
      padding: 16,
      maxWidth: "90%",
      maxHeight: "90%",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    },
    modalImage: {
      maxWidth: "100%",
      maxHeight: "80vh",
      marginBottom: 12,
    },
    storyButton: {
      padding: "8px 16px",
      background: "#405de6",
      color: "#fff",
      border: "none",
      borderRadius: 4,
      cursor: "pointer",
      fontSize: 16,
    },
    closeButton: {
      position: "absolute",
      top: 8,
      right: 8,
      background: "transparent",
      border: "none",
      fontSize: 24,
      color: "#333",
      cursor: "pointer",
    },
  };

  const reset = () => {
    setMemes([]);
    setEmotion("");
    setSelectedImage(null);
  };

  return (
    <div style={isInitial ? styles.outer : styles.container}>
      {/* 헤더: 제목 클릭 시 초기화 */}
      <div style={styles.headerGroup} onClick={reset}>
        <h1 style={styles.header}>Infinite Challenge Meme Finder</h1>
        <img src={logo} alt="logo" style={styles.logo} />
      </div>

      {/* 검색 폼 */}
      <form
        style={styles.form}
        onSubmit={(e) => {
          e.preventDefault();
          fetchMemes();
        }}
      >
        <input
          type="text"
          placeholder="Type a sentence (AI will analyze and suggest a meme)"
          value={emotion}
          onChange={(e) => setEmotion(e.target.value)}
          style={styles.input}
        />
        <button type="submit" disabled={loading} style={styles.button}>
          {loading ? "Recommending..." : "Get Meme"}
        </button>
      </form>

      {/* 추천 결과 */}
      {!isInitial && (
        <div style={styles.grid}>
          {memes.map((m) => (
            <div
              key={m.id}
              style={styles.card}
              onClick={() => setSelectedImage(m.id)}
            >
              <img src={m.id} alt={m.title} style={styles.thumbnail} />
            </div>
          ))}
        </div>
      )}

      {/* 모달 */}
      {!isInitial && selectedImage && (
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
              Share to Instagram Story
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
