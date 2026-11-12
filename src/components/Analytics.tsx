"use client";
import { useEffect } from "react";
import { trackVisit } from "@/lib/track";

export default function Analytics() {
  useEffect(() => trackVisit(), []);
  return null;
}
