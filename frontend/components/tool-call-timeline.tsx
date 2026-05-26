"use client";

import type { ToolEvent } from "@/lib/types";

export function ToolCallTimeline({ events }: { events: ToolEvent[] }) {
  return (
    <aside className="h-full overflow-auto border-l border-slate-800 bg-slate-950/70 p-4">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">Tool-call timeline</h2>
      <div className="space-y-3">
        {events
          .filter((event) => event.type === "tool_call" || event.type === "tool_result" || event.type === "thinking")
          .map((event, index) => (
            <div key={`${event.type}-${index}`} className="rounded-lg border border-slate-800 bg-slate-900/80 p-3">
              <div className="text-xs uppercase tracking-wide text-sky-300">{event.type.replace("_", " ")}</div>
              <div className="mt-1 text-sm font-medium text-slate-100">{event.name ?? event.text}</div>
              {event.params ? (
                <pre className="mt-2 whitespace-pre-wrap rounded bg-slate-950 p-2 text-xs text-slate-300">
                  {JSON.stringify(event.params, null, 2)}
                </pre>
              ) : null}
              {event.summary ? <p className="mt-2 text-xs text-slate-400">{event.summary}</p> : null}
            </div>
          ))}
      </div>
    </aside>
  );
}
