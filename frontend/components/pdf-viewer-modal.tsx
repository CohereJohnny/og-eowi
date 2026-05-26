"use client";

import type { CitationChunk } from "@/lib/types";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import { Text } from "@/components/ui/text";

export function PdfViewerModal({ chunk, onClose }: { chunk: CitationChunk | null; onClose: () => void }) {
  const isOpen = Boolean(chunk);
  if (!chunk) return null;

  const [x, y, width, height] = chunk.bbox;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="h-[min(90vh,760px)] max-w-modal-lg p-0">
        <DialogHeader className="border-b border-border px-5 py-4">
          <DialogTitle>Source PDF drill-down</DialogTitle>
          <DialogDescription>
            {chunk.doc_id}, page {chunk.page_start} · {chunk.section_path}
          </DialogDescription>
        </DialogHeader>
        <DialogBody className="flex justify-center bg-muted p-8">
          <div className="relative h-[620px] w-[480px] bg-popover text-popover-foreground shadow-lg">
            <div
              className="absolute bg-caution/40"
              style={{
                left: `${Math.min(x / 6, 70)}%`,
                top: `${Math.min(y / 8, 70)}%`,
                width: `${Math.max(Math.min(width / 8, 70), 35)}%`,
                height: `${Math.max(Math.min(height / 5, 18), 8)}%`
              }}
            />
            <div className="p-10 text-p leading-7">
              <Text className="mb-6 font-semibold">Mock source page {chunk.page_start}</Text>
              <Text>{chunk.chunk_text}</Text>
              <Text styleAs="caption" className="mt-8 text-muted-foreground">
                Real Volve PDFs mount at `data/curated/pdfs` when the Databricks export is complete. This modal preserves the
                v1 block-level highlight behavior and swaps to react-pdf for real PDFs.
              </Text>
            </div>
          </div>
        </DialogBody>
      </DialogContent>
    </Dialog>
  );
}
