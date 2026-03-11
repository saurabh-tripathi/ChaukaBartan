import crypto from "crypto";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { password } = await request.json();

  if (!process.env.APP_PASSWORD || password !== process.env.APP_PASSWORD) {
    return NextResponse.json({ detail: "Wrong password" }, { status: 401 });
  }

  const token = crypto
    .createHmac("sha256", process.env.SECRET_KEY!)
    .update("cb_valid_session")
    .digest("hex");

  const res = NextResponse.json({ ok: true });
  res.cookies.set("cb_session", token, {
    httpOnly: false, // must be readable by JS to send as Authorization header
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30, // 30 days
  });
  return res;
}
