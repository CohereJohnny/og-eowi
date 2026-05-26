"use client";

import type { CitationChunk } from "@/lib/types";
import { extractCitationIds, findChunk } from "@/lib/citations";
import { CitationChip } from "./citation-chip";

export function BriefRenderer({
  text,
  chunks,
  onCitationClick
}: {
  text: string;
  chunks: CitationChunk[];
  onCitationClick: (chunk: CitationChunk) => void;
}) {
  if (!text) {
    return (
      <div className="rounded-xl border border-dashed border-slate-700 p-8 text-slate-400">
        Ask about drilling, formations, lessons learned, or design vs execution.
      </div>
    );
  }

  const citationIds = extractCitationIds(text);
  const parts = text.split(/(\[[^\]]+\])/g);

  return (
    <article className="prose prose-invert max-w-none rounded-xl border border-slate-800 bg-slate-900/70 p-6">
      <div className="whitespace-pre-wrap text-sm leading-7 text-slate-100">
        {parts.map((part, index) => {
          const match = part.match(/^\[([^\]]+)\]$/);
          if (!match) {
            return <span key={index}>{part}</span>;
          }
          const chunk = findChunk(match[1], chunks);
          return (
            <CitationChip
              key={`${match[1]}-${index}`}
              chunkId={match[1]}
              chunk={chunk}
              onClick={() => chunk && onCitationClick(chunk)}
            />
          );
        })}
      </div>
      {citationIds.length ? (
        <div className="mt-6 border-t border-slate-800 pt-4 text-xs text-slate-400">
          Citations in this brief: {Array.from(new Set(citationIds)).length}
        </div>
      ) : null}
    </article>
  );
}
