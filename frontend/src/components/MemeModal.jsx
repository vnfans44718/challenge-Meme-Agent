import { useState } from "react";

export default function MemeModal({ imageUrl, onClose }) {
  const [imgError, setImgError] = useState(false);

  return (
    <div
      className="fixed inset-0 bg-black/80 flex items-center justify-center z-[1000]"
      onClick={onClose}
    >
      <div
        className="relative bg-white rounded-lg p-4 max-w-[90%] max-h-[90%] flex flex-col items-center"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute top-2 right-2 bg-transparent border-none text-2xl text-gray-800 cursor-pointer"
          onClick={onClose}
        >
          &times;
        </button>
        {imgError ? (
          <p className="mb-3 text-gray-600">이미지를 표시할 수 없습니다.</p>
        ) : (
          <img
            src={imageUrl}
            alt="Enlarged meme"
            referrerPolicy="no-referrer"
            className="max-w-full max-h-[80vh] mb-3"
            onError={() => setImgError(true)}
          />
        )}
      </div>
    </div>
  );
}
