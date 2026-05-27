import { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const backendUrl = process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8001";

  let response: Response;
  try {
    response = await fetch(`${backendUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body
    });
  } catch (error) {
    const warning = JSON.stringify({
      type: "warning",
      text: `Backend chat proxy unavailable: ${error instanceof Error ? error.message : "unknown error"}`
    });
    return new Response(`data: ${warning}\n\n`, {
      status: 200,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache"
      }
    });
  }

  if (!response.ok || !response.body) {
    const warning = JSON.stringify({
      type: "warning",
      text: `Backend chat proxy returned ${response.status}.`
    });
    return new Response(`data: ${warning}\n\n`, {
      status: 200,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache"
      }
    });
  }

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache"
    }
  });
}
