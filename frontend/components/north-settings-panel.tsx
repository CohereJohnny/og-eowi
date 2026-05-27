"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Text } from "@/components/ui/text";

type NorthStatus = {
  mode: "auto" | "north" | "local";
  active_mode: "north" | "local";
  base_url: string;
  token_configured: boolean;
  agent_id?: string | null;
  library_id?: string | null;
  north_ready: boolean;
  source: "env" | "runtime";
  message: string;
};

const DEFAULT_BASE_URL = "https://demo.north.cohere.com/api";

export function NorthSettingsPanel() {
  const [status, setStatus] = useState<NorthStatus | null>(null);
  const [baseUrl, setBaseUrl] = useState(DEFAULT_BASE_URL);
  const [bearerToken, setBearerToken] = useState("");
  const [agentId, setAgentId] = useState("");
  const [libraryId, setLibraryId] = useState("");
  const [mode, setMode] = useState<"auto" | "north" | "local">("auto");
  const [isSaving, setIsSaving] = useState(false);

  async function loadStatus() {
    const response = await fetch("/api/north/status", { cache: "no-store" });
    const nextStatus = (await response.json()) as NorthStatus;
    setStatus(nextStatus);
    setBaseUrl(nextStatus.base_url || DEFAULT_BASE_URL);
    setAgentId(nextStatus.agent_id ?? "");
    setLibraryId(nextStatus.library_id ?? "");
    setMode(nextStatus.mode);
  }

  useEffect(() => {
    void loadStatus();
  }, []);

  async function saveSettings() {
    setIsSaving(true);
    const response = await fetch("/api/north/status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        base_url: baseUrl,
        bearer_token: bearerToken || undefined,
        agent_id: agentId || undefined,
        library_id: libraryId || undefined,
        mode
      })
    });
    const nextStatus = (await response.json()) as NorthStatus;
    setStatus(nextStatus);
    setBearerToken("");
    setIsSaving(false);
  }

  return (
    <Card>
      <CardContent className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <Text className="font-semibold">North runtime settings</Text>
            <Text styleAs="caption" className="text-muted-foreground">
              Bearer tokens are submitted to the backend only and are not stored in browser storage.
            </Text>
          </div>
          <Badge variant={status?.active_mode === "north" ? "default" : "outline"}>
            {status?.active_mode === "north" ? "North" : "Local fallback"}
          </Badge>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <label className="space-y-1">
            <Label>North base URL</Label>
            <Input value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} />
          </label>
          <label className="space-y-1">
            <Label>Runtime mode</Label>
            <select
              value={mode}
              onChange={(event) => setMode(event.target.value as "auto" | "north" | "local")}
              className="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm outline-none transition-[color,box-shadow] focus-visible:border-ring focus-visible:outline-[3px] focus-visible:outline-ring/50"
            >
              <option value="auto">Auto</option>
              <option value="north">North</option>
              <option value="local">Local fallback</option>
            </select>
          </label>
          <label className="space-y-1">
            <Label>North agent ID</Label>
            <Input value={agentId} onChange={(event) => setAgentId(event.target.value)} placeholder="Created by setup script" />
          </label>
          <label className="space-y-1">
            <Label>North library ID</Label>
            <Input value={libraryId} onChange={(event) => setLibraryId(event.target.value)} placeholder="Created by setup script" />
          </label>
          <label className="space-y-1 md:col-span-2">
            <Label>Bearer token</Label>
            <Input
              value={bearerToken}
              onChange={(event) => setBearerToken(event.target.value)}
              type="password"
              autoComplete="off"
              placeholder={status?.token_configured ? "Token configured server-side" : "Paste token for this backend session"}
            />
          </label>
        </div>

        <div className="flex items-center justify-between gap-4">
          <Text styleAs="caption" className="text-muted-foreground">
            {status?.message ?? "Loading North status..."}
          </Text>
          <Button type="button" onClick={() => void saveSettings()} disabled={isSaving}>
            {isSaving ? "Saving..." : "Save North settings"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
