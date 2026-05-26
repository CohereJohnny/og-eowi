"use client";

import type { ReactNode } from "react";
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

  return (
    <Card>
      <CardContent>
        <MarkdownBrief text={text} chunks={chunks} onCitationClick={onCitationClick} />
      </CardContent>
      {citationIds.length ? (
        <CardFooter className="border-t border-border pt-4 text-caption text-muted-foreground">
          Citations in this brief: {Array.from(new Set(citationIds)).length}
        </CardFooter>
      ) : null}
    </Card>
  );
}

function MarkdownBrief({
  text,
  chunks,
  onCitationClick
}: {
  text: string;
  chunks: CitationChunk[];
  onCitationClick: (chunk: CitationChunk) => void;
}) {
  const lines = text.split("\n");
  const blocks: ReactNode[] = [];
  let listItems: ReactNode[] = [];
  let listType: "ul" | "ol" | null = null;
  let paragraph: string[] = [];

  function flushParagraph() {
    if (!paragraph.length) {
      return;
    }

    blocks.push(
      <p key={`p-${blocks.length}`} className="leading-7 text-foreground">
        {renderInline(paragraph.join(" "), chunks, onCitationClick)}
      </p>
    );
    paragraph = [];
  }

  function flushList() {
    if (!listType || !listItems.length) {
      return;
    }

    const ListTag = listType;
    blocks.push(
      <ListTag key={`list-${blocks.length}`} className="ml-5 space-y-2 leading-7 text-foreground">
        {listItems}
      </ListTag>
    );
    listItems = [];
    listType = null;
  }

  lines.forEach((line) => {
    const trimmed = line.trim();

    if (!trimmed) {
      flushParagraph();
      flushList();
      return;
    }

    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      const className =
        level === 1
          ? "text-title-2 font-semibold text-foreground"
          : level === 2
            ? "text-title-3 font-semibold text-foreground"
            : "text-p font-semibold text-foreground";
      blocks.push(
        <div key={`h-${blocks.length}`} className={className}>
          {renderInline(heading[2], chunks, onCitationClick)}
        </div>
      );
      return;
    }

    const unordered = trimmed.match(/^[-*]\s+(.+)$/);
    const ordered = trimmed.match(/^\d+\.\s+(.+)$/);
    const item = unordered?.[1] ?? ordered?.[1];
    const nextListType = unordered ? "ul" : ordered ? "ol" : null;

    if (item && nextListType) {
      flushParagraph();
      if (listType && listType !== nextListType) {
        flushList();
      }
      listType = nextListType;
      listItems.push(
        <li key={`li-${blocks.length}-${listItems.length}`} className={nextListType === "ul" ? "list-disc" : "list-decimal"}>
          {renderInline(item, chunks, onCitationClick)}
        </li>
      );
      return;
    }

    flushList();
    paragraph.push(trimmed);
  });

  flushParagraph();
  flushList();

  return <div className="space-y-5 text-p">{blocks}</div>;
}

function renderInline(text: string, chunks: CitationChunk[], onCitationClick: (chunk: CitationChunk) => void): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|\[[^\]]+\])/g);

  return parts.map((part, index) => {
    const citation = part.match(/^\[([^\]]+)\]$/);
    if (citation) {
      const chunk = findChunk(citation[1], chunks);
      return (
        <CitationChip
          key={`${citation[1]}-${index}`}
          chunkId={citation[1]}
          chunk={chunk}
          onClick={() => chunk && onCitationClick(chunk)}
        />
      );
    }

    const bold = part.match(/^\*\*([^*]+)\*\*$/);
    if (bold) {
      return (
        <strong key={`${bold[1]}-${index}`} className="font-semibold text-foreground">
          {bold[1]}
        </strong>
      );
    }

    return <span key={`${part}-${index}`}>{part}</span>;
  });
}
