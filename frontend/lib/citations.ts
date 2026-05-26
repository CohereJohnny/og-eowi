import type { CitationChunk } from "./types";

export function extractCitationIds(text: string): string[] {
  return Array.from(text.matchAll(/\[([^\]]+)\]/g)).map((match) => match[1]);
}

export function citationLabel(chunkId: string): string {
  const parts = chunkId.split("::");
  return parts.length >= 2 ? `${parts[0]} ${parts[1]}` : chunkId;
}

export function findChunk(chunkId: string, chunks: CitationChunk[]): CitationChunk | undefined {
  return chunks.find((chunk) => chunk.chunk_id === chunkId);
}
