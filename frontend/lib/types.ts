export type ToolEvent = {
  type: "thinking" | "tool_call" | "tool_result" | "final" | "warning";
  text?: string;
  name?: string;
  params?: Record<string, unknown>;
  summary?: string;
  data?: Record<string, unknown>;
};

export type CitationChunk = {
  chunk_id: string;
  doc_id: string;
  page_start: number;
  page_end: number;
  section_path: string;
  chunk_text: string;
  bbox: number[];
};
