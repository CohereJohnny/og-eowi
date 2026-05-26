"use client";

import type { CitationChunk } from "@/lib/types";

export function PdfViewerModal({ chunk, onClose }: { chunk: CitationChunk | null; onClose: () => void }) {
  if (!chunk) {
    return null;
  }

  const [x, y, width, height] = chunk.bbox;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-8">
      <div className="relative h-full max-h-[760px] w-full max-w-4xl rounded-xl border border-slate-700 bg-slate-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-700 px-5 py-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-100">Source PDF drill-down</h2>
            <p className="text-xs text-slate-400">
              {chunk.doc_id}, page {chunk.page_start} · {chunk.section_path}
            </p>
          </div>
          <button className="rounded-md border border-slate-600 px-3 py-1 text-sm text-slate-200" onClick={onClose}>
            Close
          </button>
        </div>
        <div className="flex h-[680px] justify-center overflow-auto bg-slate-800 p-8">
          <div className="relative h-[620px] w-[480px] bg-white text-slate-950 shadow-xl">
            <div
              className="absolute bg-yellow-300/50"
              style={{
                left: `${Math.min(x / 6, 70)}%`,
                top: `${Math.min(y / 8, 70)}%`,
                width: `${Math.max(Math.min(width / 8, 70), 35)}%`,
                height: `${Math.max(Math.min(height / 5, 18), 8)}%`
              }}
            />
            <div className="p-10 text-sm leading-7">
              <p className="mb-6 font-semibold">Mock source page {chunk.page_start}</p>
              <p>{chunk.chunk_text}</p>
              <p className="mt-8 text-xs text-slate-500">
                Real Volve PDFs mount at `data/curated/pdfs` when the Databricks export is complete. This modal preserves the
                v1 block-level highlight behavior and swaps to react-pdf for real PDFs.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
