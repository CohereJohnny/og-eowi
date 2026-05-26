"use client";

import type { CitationChunk } from "@/lib/types";
import { extractCitationIds, findChunk } from "@/lib/citations";
import { CitationChip } from "./citation-chip";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Text } from "@/components/ui/text";

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
      <Card className="border-dashed">
        <CardContent>
          <Text className="text-muted-foreground">Ask about drilling, formations, lessons learned, or design vs execution.</Text>
        </CardContent>
      </Card>
    );
  }

  const citationIds = extractCitationIds(text);
  const parts = text.split(/(\[[^\]]+\])/g);

  return (
    <Card>
      <CardContent>
      <div className="whitespace-pre-wrap text-p leading-7 text-foreground">
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
      </CardContent>
      {citationIds.length ? (
        <CardFooter className="border-t border-border pt-4 text-caption text-muted-foreground">
          Citations in this brief: {Array.from(new Set(citationIds)).length}
        </CardFooter>
      ) : null}
    </Card>
  );
}
