"use client";
/* eslint-disable @next/next/no-img-element */
import { useState, type ImgHTMLAttributes } from "react";

/**
 * An image for sticker tiles: shows a soft placeholder (never alt text) while it
 * loads, and retries a couple of times if the download fails, which happens on
 * slow mobile connections when a search shows dozens of stickers at once.
 */
export default function SafeImg({ src, className = "", style, ...rest }: ImgHTMLAttributes<HTMLImageElement> & { src: string }) {
  const [tries, setTries] = useState(0);
  const [loaded, setLoaded] = useState(false);
  const url = tries ? `${src}${src.includes("?") ? "&" : "?"}retry=${tries}` : src;
  return (
    <img
      {...rest}
      key={src}
      src={url}
      alt=""
      loading="lazy"
      decoding="async"
      draggable={false}
      onLoad={() => setLoaded(true)}
      onError={() => tries < 2 && setTimeout(() => setTries((t) => t + 1), 600 * (tries + 1))}
      className={`${className} ${loaded ? "" : "rounded-full bg-ink/5 animate-pulse"}`}
      style={{ ...style, color: "transparent" }}
    />
  );
}
