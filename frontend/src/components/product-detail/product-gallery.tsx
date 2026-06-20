"use client";

import * as React from "react";
import { RemoteImage } from "@/components/ui/remote-image";
import { ChevronLeft, ChevronRight, Expand, ZoomIn } from "lucide-react";

import type { ProductImage } from "@/config/product-detail";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog";

export interface ProductGalleryProps {
  images: ProductImage[];
  productName: string;
  brand: string;
  className?: string;
}

const ZOOM_SCALE = 2.5;

function GalleryImage({
  image,
  alt,
  className,
  zooming,
  zoomPosition,
  priority = false,
  scale = 2,
}: {
  image: ProductImage;
  alt: string;
  className?: string;
  zooming?: boolean;
  zoomPosition?: { x: number; y: number };
  priority?: boolean;
  scale?: number;
}) {
  return (
    <RemoteImage
      src={image.src}
      alt={alt}
      fill
      sizes="(max-width: 1024px) 100vw, 50vw"
      priority={priority}
      className={cn(
        "object-cover transition-transform duration-150 ease-out",
        className
      )}
      style={
        zooming && zoomPosition
          ? {
              transform: `scale(${scale})`,
              transformOrigin: `${zoomPosition.x}% ${zoomPosition.y}%`,
            }
          : undefined
      }
    />
  );
}

function ProductGallery({
  images,
  productName,
  brand,
  className,
}: ProductGalleryProps) {
  const [activeIndex, setActiveIndex] = React.useState(0);
  const [isZooming, setIsZooming] = React.useState(false);
  const [zoomPosition, setZoomPosition] = React.useState({ x: 50, y: 50 });
  const [lightboxOpen, setLightboxOpen] = React.useState(false);
  const imageRef = React.useRef<HTMLDivElement>(null);

  const activeImage = images[activeIndex] ?? images[0];

  const goTo = React.useCallback(
    (index: number) => {
      setActiveIndex(Math.max(0, Math.min(images.length - 1, index)));
    },
    [images.length]
  );

  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (lightboxOpen) {
        if (event.key === "ArrowLeft") goTo(activeIndex - 1);
        if (event.key === "ArrowRight") goTo(activeIndex + 1);
        return;
      }
      if (event.key === "ArrowLeft") goTo(activeIndex - 1);
      if (event.key === "ArrowRight") goTo(activeIndex + 1);
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeIndex, goTo, images.length, lightboxOpen]);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!imageRef.current) return;
    const rect = imageRef.current.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    setZoomPosition({
      x: Math.min(100, Math.max(0, x)),
      y: Math.min(100, Math.max(0, y)),
    });
  };

  const renderThumbnail = (image: ProductImage, index: number, layout: "row" | "column") => {
    const isActive = index === activeIndex;
    return (
      <button
        key={image.id}
        type="button"
        role="tab"
        aria-selected={isActive}
        aria-label={image.label ?? image.alt}
        onClick={() => setActiveIndex(index)}
        className={cn(
          "relative shrink-0 overflow-hidden rounded-lg border-2 transition-all",
          layout === "column" ? "size-16 lg:size-[4.5rem]" : "size-16 sm:size-20",
          isActive
            ? "border-brand-blue shadow-sm ring-2 ring-brand-blue/20"
            : "border-border hover:border-brand-blue/40"
        )}
      >
        <RemoteImage
          src={image.src}
          alt=""
          fill
          sizes="80px"
          className="object-cover"
          aria-hidden
        />
      </button>
    );
  };

  if (!activeImage) return null;

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex gap-3 md:gap-4">
        <div
          className="hidden shrink-0 flex-col gap-2 md:flex"
          role="tablist"
          aria-label="Product image thumbnails"
          aria-orientation="vertical"
        >
          {images.map((image, index) => renderThumbnail(image, index, "column"))}
        </div>

        <div className="relative min-w-0 flex-1">
          <div className="xl:grid xl:grid-cols-[minmax(0,1fr)_minmax(0,0.85fr)] xl:gap-4">
            <div
              ref={imageRef}
              className={cn(
                "relative aspect-square overflow-hidden rounded-xl border border-border bg-neutral-100",
                isZooming && "cursor-crosshair"
              )}
              onMouseEnter={() => setIsZooming(true)}
              onMouseLeave={() => setIsZooming(false)}
              onMouseMove={handleMouseMove}
            >
              <GalleryImage
                image={activeImage}
                alt={activeImage.alt ?? productName}
                zooming={isZooming}
                zoomPosition={zoomPosition}
                priority
                scale={2}
              />

              {isZooming ? (
                <div
                  className="pointer-events-none absolute size-24 rounded border-2 border-brand-blue/60 bg-brand-blue/10 shadow-sm"
                  style={{
                    left: `calc(${zoomPosition.x}% - 3rem)`,
                    top: `calc(${zoomPosition.y}% - 3rem)`,
                  }}
                  aria-hidden
                />
              ) : null}

              <Button
                type="button"
                variant="secondary"
                size="icon-sm"
                className="absolute right-3 top-3 size-9 bg-white/90 shadow-sm lg:hidden"
                onClick={() => setLightboxOpen(true)}
                aria-label="Expand image"
              >
                <Expand className="size-4" />
              </Button>

              <Button
                type="button"
                variant="secondary"
                size="icon-sm"
                className="absolute left-3 top-1/2 hidden -translate-y-1/2 bg-white/90 shadow-sm md:flex xl:hidden"
                onClick={() => goTo(activeIndex - 1)}
                disabled={activeIndex === 0}
                aria-label="Previous image"
              >
                <ChevronLeft className="size-4" />
              </Button>
              <Button
                type="button"
                variant="secondary"
                size="icon-sm"
                className="absolute right-3 top-1/2 hidden -translate-y-1/2 bg-white/90 shadow-sm md:flex xl:hidden"
                onClick={() => goTo(activeIndex + 1)}
                disabled={activeIndex === images.length - 1}
                aria-label="Next image"
              >
                <ChevronRight className="size-4" />
              </Button>

              <div className="pointer-events-none absolute bottom-3 left-3 hidden items-center gap-1.5 rounded-full bg-brand-navy/80 px-3 py-1.5 text-xs font-medium text-white backdrop-blur-sm lg:flex">
                <ZoomIn className="size-3.5" />
                Hover to zoom
              </div>

              <p className="absolute bottom-3 right-3 rounded-md bg-white/90 px-2 py-1 text-[10px] font-medium tabular-nums text-muted-foreground shadow-sm">
                {activeIndex + 1} / {images.length}
              </p>
            </div>

            <div
              className={cn(
                "relative hidden aspect-square overflow-hidden rounded-xl border border-border bg-neutral-100 xl:block",
                !isZooming && "opacity-0"
              )}
              aria-hidden={!isZooming}
            >
              {isZooming ? (
                <GalleryImage
                  image={activeImage}
                  alt=""
                  zooming
                  zoomPosition={zoomPosition}
                  scale={ZOOM_SCALE}
                />
              ) : (
                <div className="flex h-full items-center justify-center p-6 text-center text-sm text-muted-foreground">
                  <p>
                    <span className="font-medium text-brand-navy">{brand}</span>
                    <br />
                    Move cursor over the image to magnify
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div
        className="flex gap-2 overflow-x-auto pb-1 md:hidden"
        role="tablist"
        aria-label="Product images"
      >
        {images.map((image, index) => renderThumbnail(image, index, "row"))}
      </div>

      <Dialog open={lightboxOpen} onOpenChange={setLightboxOpen}>
        <DialogContent className="max-w-lg p-2 sm:max-w-2xl">
          <DialogTitle className="sr-only">{activeImage.alt}</DialogTitle>
          <div className="relative aspect-square overflow-hidden rounded-lg bg-neutral-100">
            <GalleryImage image={activeImage} alt={activeImage.alt} />
          </div>
          <div className="flex justify-center gap-2 overflow-x-auto pt-2">
            {images.map((image, index) => (
              <button
                key={image.id}
                type="button"
                onClick={() => setActiveIndex(index)}
                className={cn(
                  "relative size-12 shrink-0 overflow-hidden rounded-md border-2",
                  index === activeIndex ? "border-brand-blue" : "border-border"
                )}
              >
                <RemoteImage
                  src={image.src}
                  alt=""
                  fill
                  sizes="48px"
                  className="object-cover"
                  aria-hidden
                />
              </button>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export { ProductGallery };
