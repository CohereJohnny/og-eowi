"use client";

import type { CitationChunk } from "@/lib/types";
import { citationLabel } from "@/lib/citations";

export function CitationChip({
  chunkId,
  chunk,
  onClick
}: {
  chunkId: string;
  chunk?: CitationChunk;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={chunk ? `${chunk.section_path}: ${chunk.chunk_text.slice(0, 200)}` : chunkId}
      className="mx-1 rounded-full border border-sky-400/60 bg-sky-400/10 px-2 py-0.5 text-xs font-medium text-sky-200 hover:bg-sky-400/20"
    >
      {citationLabel(chunkId)}
    </button>
  );
}
