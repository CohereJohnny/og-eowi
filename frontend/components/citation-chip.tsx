"use client";

import type { CitationChunk } from "@/lib/types";
import { citationLabel } from "@/lib/citations";
import { Button } from "@/components/ui/button";

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
    <Button
      type="button"
      variant="outline"
      size="sm"
      onClick={onClick}
      title={chunk ? `${chunk.section_path}: ${chunk.chunk_text.slice(0, 200)}` : chunkId}
      className="mx-1 inline-flex h-6 rounded-full px-2 py-0 text-caption text-link"
    >
      {citationLabel(chunkId)}
    </Button>
  );
}
