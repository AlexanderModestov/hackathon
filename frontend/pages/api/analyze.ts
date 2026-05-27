import type { NextApiRequest, NextApiResponse } from "next";

const RAILWAY_URL =
  process.env.RAILWAY_API_URL ||
  "https://hackathon-production-b299.up.railway.app";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).end();
  }

  const upstream = await fetch(`${RAILWAY_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req.body),
  });

  const data = await upstream.json();
  res.status(upstream.status).json(data);
}
