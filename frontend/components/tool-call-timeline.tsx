"use client";

import type { ToolEvent } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Text } from "@/components/ui/text";

export function ToolCallTimeline({ events }: { events: ToolEvent[] }) {
  return (
    <aside className="h-full overflow-auto border-l border-border bg-card p-4">
      <Text as="h2" styleAs="label" className="mb-4 text-muted-foreground">
        Tool-call timeline
      </Text>
      <div className="space-y-3">
        {events
          .filter((event) => event.type === "tool_call" || event.type === "tool_result" || event.type === "thinking")
          .map((event, index) => (
            <Card key={`${event.type}-${index}`} className="py-3">
              <CardContent className="space-y-2 px-3">
              <Badge variant={event.type === "tool_result" ? "success" : "info"}>{event.type.replace("_", " ")}</Badge>
              <Text styleAs="p-sm" className="font-medium">
                {event.name ?? event.text}
              </Text>
              {event.params ? (
                <pre className="whitespace-pre-wrap rounded-md border border-border bg-background p-2 text-caption text-muted-foreground">
                  {JSON.stringify(event.params, null, 2)}
                </pre>
              ) : null}
              {event.summary ? <Text styleAs="caption" className="text-muted-foreground">{event.summary}</Text> : null}
              </CardContent>
            </Card>
          ))}
      </div>
    </aside>
  );
}
