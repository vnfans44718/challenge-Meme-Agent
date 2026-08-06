import { useState } from "react";

export default function MemeGrid({ memes, onSelect }) {
  const [brokenIds, setBrokenIds] = useState(new Set());

  return (
    <div className="flex flex-wrap gap-4 justify-start items-start">
      {memes
        .filter((m) => !brokenIds.has(m.id))
        .map((m) => (
          <div
            key={m.id}
            className="w-[calc(25%-16px)] h-[200px] bg-white rounded overflow-hidden shadow-md cursor-pointer"
            onClick={() => onSelect(m.imageUrl)}
          >
            <img
              src={m.imageUrl}
              alt={m.title}
              referrerPolicy="no-referrer"
              className="w-full h-full object-cover bg-gray-200"
              onError={() =>
                setBrokenIds((prev) => new Set(prev).add(m.id))
              }
            />
          </div>
        ))}
    </div>
  );
}
