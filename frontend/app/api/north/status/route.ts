import { NextRequest } from "next/server";

function backendUrl() {
  return process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8001";
}

export async function GET() {
  const response = await fetch(`${backendUrl()}/north/status`, { cache: "no-store" });
  return Response.json(await response.json(), { status: response.status });
}

export async function POST(request: NextRequest) {
  const body = await request.text();
  const response = await fetch(`${backendUrl()}/north/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body
  });
  return Response.json(await response.json(), { status: response.status });
}
