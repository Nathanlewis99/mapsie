import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

// A fresh SQLite database per test file, never the developer's own data.
process.env.DATA_DIR = mkdtempSync(path.join(tmpdir(), "mapsie-test-"));
delete process.env.DATABASE_URL;
process.env.SESSION_SECRET = "test-secret-0123456789abcdef0123456789";
