"use client";

import { useMemo, useState } from "react";
import { BriefRenderer } from "./brief-renderer";
import { PdfViewerModal } from "./pdf-viewer-modal";
import { ToolCallTimeline } from "./tool-call-timeline";
import type { CitationChunk, ToolEvent } from "@/lib/types";

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
    <main className="grid min-h-screen grid-cols-[1fr_360px] bg-slate-950 text-slate-100">
      <section className="flex min-w-0 flex-col">
        <header className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
          <div>
            <h1 className="text-lg font-semibold">End-of-Well Intelligence</h1>
            <p className="text-sm text-slate-400">Cited engineering briefings over Volve drilling history</p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={wellId}
              onChange={(event) => setWellId(event.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
            >
              <option value="15/9-F-11">15/9-F-11</option>
              <option value="15/9-F-14">15/9-F-14</option>
            </select>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400">Cohere</span>
          </div>
        </header>

        <div className="flex-1 space-y-5 overflow-auto p-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              rows={3}
              className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 p-3 text-sm outline-none focus:border-sky-400"
            />
            <div className="mt-3 flex items-center gap-3">
              <button
                onClick={() => void submit()}
                disabled={isRunning}
                className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50"
              >
                {isRunning ? "Running..." : "Ask"}
              </button>
              <button
                onClick={askFollowUp}
                disabled={isRunning}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-200 disabled:opacity-50"
              >
                Ask design vs execution
              </button>
            </div>
          </div>

          <BriefRenderer text={brief} chunks={chunks} onCitationClick={setSelectedChunk} />
        </div>
      </section>

      <ToolCallTimeline events={events} />
      <PdfViewerModal chunk={selectedChunk} onClose={() => setSelectedChunk(null)} />
    </main>
  );
}
