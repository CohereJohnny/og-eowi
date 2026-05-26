"use client";

import { useMemo, useState } from "react";
import { BriefRenderer } from "./brief-renderer";
import { PdfViewerModal } from "./pdf-viewer-modal";
import { ToolCallTimeline } from "./tool-call-timeline";
import type { CitationChunk, ToolEvent } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Text } from "@/components/ui/text";

const DEMO_QUESTION =
  "I'm planning a new well in the Hugin Formation. What are the three things I most need to know from how 15/9-F-11 was drilled?";

export function DemoShell() {
  const [message, setMessage] = useState(DEMO_QUESTION);
  const [wellId, setWellId] = useState("15/9-F-11");
  const [events, setEvents] = useState<ToolEvent[]>([]);
  const [brief, setBrief] = useState("");
  const [chunks, setChunks] = useState<CitationChunk[]>([]);
  const [selectedChunk, setSelectedChunk] = useState<CitationChunk | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const sessionId = useMemo(() => `demo-${Math.random().toString(16).slice(2)}`, []);

  async function submit(nextMessage = message) {
    setIsRunning(true);
    setEvents([]);
    setBrief("");
    setChunks([]);

    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: nextMessage, session_id: sessionId, well_id: wellId })
    });

    if (!response.body) {
      setIsRunning(false);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        const line = frame.split("\n").find((candidate) => candidate.startsWith("data: "));
        if (!line) continue;
        const event = JSON.parse(line.slice(6)) as ToolEvent;
        setEvents((current) => [...current, event]);
        if (event.type === "final") {
          setBrief(event.text ?? "");
          const eventChunks = event.data?.chunks;
          if (Array.isArray(eventChunks)) {
            setChunks(eventChunks as CitationChunk[]);
          }
        }
      }
    }
    setIsRunning(false);
  }

  function askFollowUp() {
    const followUp = "Of those issues, which were avoidable through better well design vs. better execution?";
    setMessage(followUp);
    void submit(followUp);
  }

  return (
    <main className="grid min-h-screen grid-cols-[1fr_360px] bg-background text-foreground">
      <section className="flex min-w-0 flex-col">
        <header className="flex items-center justify-between border-b border-border bg-card px-6 py-4">
          <div>
            <Text as="h1" styleAs="h5-small">
              End-of-Well Intelligence
            </Text>
            <Text className="text-muted-foreground">Cited engineering briefings over Volve drilling history</Text>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={wellId}
              onChange={(event) => setWellId(event.target.value)}
              className="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm outline-none transition-[color,box-shadow] focus-visible:border-ring focus-visible:outline-[3px] focus-visible:outline-ring/50"
            >
              <option value="15/9-F-11">15/9-F-11</option>
              <option value="15/9-F-14">15/9-F-14</option>
            </select>
            <Badge variant="outline">Cohere</Badge>
          </div>
        </header>

        <div className="flex-1 space-y-5 overflow-auto p-6">
          <Card>
            <CardContent className="space-y-3">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              rows={3}
              className="w-full resize-none rounded-md border border-input bg-background p-3 text-sm outline-none transition-[color,box-shadow] placeholder:text-muted-foreground focus-visible:border-ring focus-visible:outline-[3px] focus-visible:outline-ring/50"
            />
            <div className="flex items-center gap-3">
              <Button
                onClick={() => void submit()}
                disabled={isRunning}
              >
                {isRunning ? "Running..." : "Ask"}
              </Button>
              <Button
                variant="outline"
                onClick={askFollowUp}
                disabled={isRunning}
              >
                Ask design vs execution
              </Button>
            </div>
            </CardContent>
          </Card>

          <BriefRenderer text={brief} chunks={chunks} onCitationClick={setSelectedChunk} />
        </div>
      </section>

      <ToolCallTimeline events={events} />
      <PdfViewerModal chunk={selectedChunk} onClose={() => setSelectedChunk(null)} />
    </main>
  );
}
