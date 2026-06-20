"use client";

import { Share2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";

export interface WishlistShareButtonProps {
  className?: string;
}

function WishlistShareButton({ className }: WishlistShareButtonProps) {
  const handleShare = async () => {
    const url = typeof window !== "undefined" ? window.location.href : "/wishlist";

    try {
      if (typeof navigator !== "undefined" && navigator.share) {
        await navigator.share({
          title: "My A2Z Tools wishlist",
          text: "Products I've saved on A2Z Tools",
          url,
        });
        return;
      }

      await navigator.clipboard.writeText(url);
      toast.success("Wishlist link copied", {
        description: "Share this link with your team or purchasing manager.",
      });
    } catch {
      toast.error("Could not share wishlist");
    }
  };

  return (
    <Button
      type="button"
      variant="outline"
      className={className}
      onClick={handleShare}
    >
      <Share2 className="size-4" />
      Share wishlist
    </Button>
  );
}

export { WishlistShareButton };
