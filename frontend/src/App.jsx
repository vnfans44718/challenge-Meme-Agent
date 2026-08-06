import { useCallback, useEffect, useReducer, useRef, useState } from "react";
import Header from "./components/Header";
import SearchForm from "./components/SearchForm";
import MemeGrid from "./components/MemeGrid";
import MemeModal from "./components/MemeModal";
import { API_BASE_URL } from "./config";

const initialSearchState = {
  hasSearched: false,
  memes: [],
  emotionKey: null,
  classifiedEmotion: null,
  offset: 0,
  hasMore: false,
};

function searchReducer(state, action) {
  switch (action.type) {
    case "search_success":
      return {
        hasSearched: true,
        memes: action.memes,
        emotionKey: action.emotionKey,
        classifiedEmotion: action.classifiedEmotion,
        offset: action.memes.length,
        hasMore: action.hasMore,
      };
    case "load_more_success":
      return {
        ...state,
        memes: [...state.memes, ...action.memes],
        offset: state.offset + action.memes.length,
        hasMore: action.hasMore,
      };
    case "reset":
      return initialSearchState;
    default:
      return state;
  }
}

export default function MemeRecommendationApp() {
  const [emotion, setEmotion] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [error, setError] = useState(null);
  const [search, dispatch] = useReducer(searchReducer, initialSearchState);

  const sentinelRef = useRef(null);

  const isInitial = !search.hasSearched;

  const fetchMemes = async () => {
    if (!emotion.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_BASE_URL}/api/memes?emotion_text=${encodeURIComponent(emotion)}`
      );
      if (!res.ok) throw new Error(`요청이 실패했습니다 (${res.status})`);
      const data = await res.json();
      dispatch({
        type: "search_success",
        memes: data.memes || [],
        emotionKey: data.emotion || null,
        classifiedEmotion: data.classifiedEmotion || null,
        hasMore: Boolean(data.hasMore),
      });
    } catch (err) {
      console.error(err);
      setError("짤을 불러오지 못했어요. 잠시 후 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  };

  const loadMoreMemes = useCallback(async () => {
    if (!search.emotionKey || !search.hasMore || loadingMore) return;
    setLoadingMore(true);
    try {
      const res = await fetch(
        `${API_BASE_URL}/api/memes/by-emotion?emotion=${encodeURIComponent(search.emotionKey)}&offset=${search.offset}`
      );
      if (!res.ok) throw new Error(`요청이 실패했습니다 (${res.status})`);
      const data = await res.json();
      dispatch({
        type: "load_more_success",
        memes: data.memes || [],
        hasMore: Boolean(data.hasMore),
      });
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingMore(false);
    }
  }, [search.emotionKey, search.hasMore, search.offset, loadingMore]);

  useEffect(() => {
    if (!sentinelRef.current) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMoreMemes();
        }
      },
      { rootMargin: "200px" }
    );
    observer.observe(sentinelRef.current);
    return () => observer.disconnect();
  }, [loadMoreMemes]);

  const reset = () => {
    setEmotion("");
    setSelectedImage(null);
    setError(null);
    dispatch({ type: "reset" });
  };

  const showEmptyState =
    !isInitial && !loading && !error && search.memes.length === 0;

  return (
    <div
      className={
        isInitial
          ? "flex flex-col justify-center items-center h-screen bg-[#f7f7f7] font-sans"
          : "max-w-[960px] mx-auto my-10 p-5 bg-[#f7f7f7] font-sans min-h-screen text-left"
      }
    >
      <Header isInitial={isInitial} onReset={reset} />

      <SearchForm
        isInitial={isInitial}
        emotion={emotion}
        loading={loading}
        onChange={setEmotion}
        onSubmit={(e) => {
          e.preventDefault();
          fetchMemes();
        }}
      />

      {error && (
        <p className={`text-red-600 text-sm mb-4 ${isInitial ? "mx-auto" : ""}`}>
          {error}
        </p>
      )}

      {!isInitial && search.classifiedEmotion && (
        <p className="text-sm text-gray-600 mb-4">감정: {search.classifiedEmotion}</p>
      )}

      {showEmptyState && (
        <p className="text-sm text-gray-600 mb-4">
          해당 감정에 맞는 짤을 찾지 못했어요.
        </p>
      )}

      {!isInitial && search.memes.length > 0 && (
        <MemeGrid memes={search.memes} onSelect={setSelectedImage} />
      )}

      {!isInitial && search.hasMore && (
        <div ref={sentinelRef} className="h-10 flex items-center justify-center">
          {loadingMore && (
            <p className="text-sm text-gray-500">더 불러오는 중...</p>
          )}
        </div>
      )}

      {!isInitial && selectedImage && (
        <MemeModal
          key={selectedImage}
          imageUrl={selectedImage}
          onClose={() => setSelectedImage(null)}
        />
      )}
    </div>
  );
}
