"use client";

import * as React from "react";
import Image, { type ImageProps } from "next/image";

import { fallbackImage } from "@/config/visual-assets";

export interface RemoteImageProps extends Omit<ImageProps, "onError" | "src"> {
  src: string;
  fallbackSrc?: string;
  fallbackAlt?: string;
}

/**
 * next/image wrapper that swaps to a verified fallback when a remote URL fails.
 */
function RemoteImage({
  src,
  fallbackSrc = fallbackImage.src,
  fallbackAlt,
  alt,
  ...props
}: RemoteImageProps) {
  const [currentSrc, setCurrentSrc] = React.useState(src);
  const [hasFailed, setHasFailed] = React.useState(false);

  React.useEffect(() => {
    setCurrentSrc(src);
    setHasFailed(false);
  }, [src]);

  const resolvedAlt = hasFailed ? (fallbackAlt ?? fallbackImage.alt) : alt;

  return (
    <Image
      {...props}
      src={currentSrc}
      alt={resolvedAlt}
      onError={() => {
        if (currentSrc !== fallbackSrc) {
          setHasFailed(true);
          setCurrentSrc(fallbackSrc);
        }
      }}
    />
  );
}

export { RemoteImage };
