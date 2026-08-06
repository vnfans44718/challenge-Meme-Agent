export default function SearchForm({ isInitial, emotion, loading, onChange, onSubmit }) {
  return (
    <form
      className={`flex w-4/5 max-w-[600px] mb-10 ${
        isInitial ? "mx-auto justify-center" : "mx-0 justify-start"
      }`}
      onSubmit={onSubmit}
    >
      <input
        type="text"
        placeholder="문장을 입력하세요 (AI가 분석해서 짤을 추천해드려요)"
        value={emotion}
        onChange={(e) => onChange(e.target.value)}
        className="flex-1 p-2.5 border border-gray-300 rounded bg-white text-black text-base"
      />
      <button
        type="submit"
        disabled={loading}
        className="ml-2 px-5 py-2.5 bg-[#007bff] text-white rounded text-base cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {loading ? "추천 중..." : "추천받기"}
      </button>
    </form>
  );
}
