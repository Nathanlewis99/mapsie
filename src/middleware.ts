import { NextResponse, type NextRequest } from "next/server";

// Basic password protection for the admin area. Set ADMIN_PASSWORD in production;
// without it the admin area only works in local development.
export function middleware(req: NextRequest) {
  const pass = process.env.ADMIN_PASSWORD;
  if (!pass) {
    if (process.env.NODE_ENV === "development") return NextResponse.next();
    return new NextResponse("Admin disabled: set ADMIN_PASSWORD", { status: 403 });
  }
  const auth = req.headers.get("authorization") ?? "";
  const [, encoded] = auth.split(" ");
  const supplied = encoded ? atob(encoded).split(":").slice(1).join(":") : "";
  if (supplied === pass) return NextResponse.next();
  return new NextResponse("Authentication required", { status: 401, headers: { "WWW-Authenticate": 'Basic realm="Mapsie admin"' } });
}

export const config = { matcher: ["/admin/:path*", "/api/admin/:path*"] };
