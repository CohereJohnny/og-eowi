import { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const backendUrl = process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

  const response = await fetch(`${backendUrl}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache"
    }
  });
}
