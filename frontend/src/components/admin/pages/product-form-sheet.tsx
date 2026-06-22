"use client";

import { useEffect, useMemo, useState } from "react";
import { ImagePlus, Trash2 } from "lucide-react";

import { FormField } from "@/components/ui/form-field";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import type { AdminProduct, AdminProductWritePayload } from "@/lib/api/admin/types";
import { useAdminBrands, useAdminCategories } from "@/lib/api/admin/hooks";

interface ProductImageDraft {
  url: string;
  altText: string;
  isPrimary: boolean;
}

interface ProductFormSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  product?: AdminProduct | null;
  onSubmit: (payload: AdminProductWritePayload) => Promise<void>;
  isSubmitting?: boolean;
}

const EMPTY_IMAGE: ProductImageDraft = { url: "", altText: "", isPrimary: false };

function centsToAudInput(cents: number): string {
  return (cents / 100).toFixed(2);
}

function audInputToCents(value: string): number {
  const parsed = Number.parseFloat(value);
  if (Number.isNaN(parsed)) return 0;
  return Math.round(parsed * 100);
}

function ProductFormSheet({
  open,
  onOpenChange,
  product,
  onSubmit,
  isSubmitting,
}: ProductFormSheetProps) {
  const isEdit = Boolean(product);
  const { data: brands } = useAdminBrands();
  const { data: categories } = useAdminCategories();

  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [sku, setSku] = useState("");
  const [brandId, setBrandId] = useState<string>("none");
  const [categoryId, setCategoryId] = useState<string>("none");
  const [sellPriceAud, setSellPriceAud] = useState("0.00");
  const [costPriceAud, setCostPriceAud] = useState("0.00");
  const [stock, setStock] = useState("0");
  const [isActive, setIsActive] = useState(true);
  const [shortDescription, setShortDescription] = useState("");
  const [description, setDescription] = useState("");
  const [images, setImages] = useState<ProductImageDraft[]>([{ ...EMPTY_IMAGE, isPrimary: true }]);

  useEffect(() => {
    if (!open) return;
    if (product) {
      setName(product.name);
      setSlug(product.slug);
      setSku(product.sku);
      setBrandId(product.brandId ?? "none");
      setCategoryId(product.categoryId ?? "none");
      setSellPriceAud(centsToAudInput(product.sellPriceExGstCents));
      setCostPriceAud(centsToAudInput(product.costPriceCents));
      setStock(String(product.stock));
      setIsActive(product.isActive);
      setShortDescription(product.shortDescription);
      setDescription(product.description);
      setImages(
        product.images.length
          ? product.images.map((image) => ({
              url: image.url,
              altText: image.altText,
              isPrimary: image.isPrimary,
            }))
          : [{ ...EMPTY_IMAGE, isPrimary: true }]
      );
      return;
    }
    setName("");
    setSlug("");
    setSku("");
    setBrandId("none");
    setCategoryId("none");
    setSellPriceAud("0.00");
    setCostPriceAud("0.00");
    setStock("0");
    setIsActive(true);
    setShortDescription("");
    setDescription("");
    setImages([{ ...EMPTY_IMAGE, isPrimary: true }]);
  }, [open, product]);

  const gstPreview = useMemo(() => {
    const exGst = audInputToCents(sellPriceAud);
    const gstRate = Number.parseFloat(product?.gstRate ?? "0.1");
    const gstCents = Math.round(exGst * gstRate);
    return {
      exGst,
      gstCents,
      incGst: exGst + gstCents,
      gstRate,
    };
  }, [sellPriceAud, product?.gstRate]);

  const handleImageChange = (index: number, field: keyof ProductImageDraft, value: string | boolean) => {
    setImages((current) =>
      current.map((image, i) => (i === index ? { ...image, [field]: value } : image))
    );
  };

  const handleSetPrimaryImage = (index: number) => {
    setImages((current) =>
      current.map((image, i) => ({ ...image, isPrimary: i === index }))
    );
  };

  const handleAddImage = () => {
    setImages((current) => [...current, { ...EMPTY_IMAGE }]);
  };

  const handleRemoveImage = (index: number) => {
    setImages((current) => {
      const next = current.filter((_, i) => i !== index);
      if (!next.length) return [{ ...EMPTY_IMAGE, isPrimary: true }];
      if (!next.some((image) => image.isPrimary) && next[0]) {
        next[0] = { url: next[0].url, altText: next[0].altText, isPrimary: true };
      }
      return next;
    });
  };

  const handleSubmit = async () => {
    const imagePayload = images
      .filter((image) => image.url.trim())
      .map((image, index) => ({
        url: image.url.trim(),
        alt_text: image.altText.trim(),
        sort_order: index,
        is_primary: image.isPrimary,
      }));

    await onSubmit({
      name: name.trim(),
      slug: slug.trim() || undefined,
      sku: sku.trim(),
      brand_id: brandId === "none" ? null : brandId,
      category_id: categoryId === "none" ? null : categoryId,
      sell_price_ex_gst_cents: audInputToCents(sellPriceAud),
      cost_price_cents: audInputToCents(costPriceAud),
      stock: Number.parseInt(stock, 10) || 0,
      is_active: isActive,
      short_description: shortDescription.trim(),
      description: description.trim(),
      images: imagePayload,
    });
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full overflow-y-auto sm:max-w-2xl">
        <SheetHeader>
          <SheetTitle>{isEdit ? "Edit product" : "Create product"}</SheetTitle>
          <SheetDescription>
            Manage catalog details, pricing, stock, and product images.
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6 pb-24">
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField id="product-name" label="Product name" required>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </FormField>
            <FormField id="product-sku" label="SKU" required>
              <Input value={sku} onChange={(e) => setSku(e.target.value)} />
            </FormField>
            <FormField id="product-slug" label="Slug" hint="Auto-generated from name if left blank.">
              <Input value={slug} onChange={(e) => setSlug(e.target.value)} />
            </FormField>
            <FormField id="product-stock" label="Inventory quantity">
              <Input
                type="number"
                min={0}
                value={stock}
                onChange={(e) => setStock(e.target.value)}
              />
            </FormField>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <FormField id="product-brand" label="Brand">
              <Select value={brandId} onValueChange={setBrandId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select brand" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No brand</SelectItem>
                  {(brands ?? []).map((brand) => (
                    <SelectItem key={brand.id} value={brand.id}>
                      {brand.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
            <FormField id="product-category" label="Category">
              <Select value={categoryId} onValueChange={setCategoryId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No category</SelectItem>
                  {(categories ?? []).map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <FormField id="product-sell-price" label="Sell price (ex GST, AUD)" required>
              <Input
                type="number"
                min={0}
                step="0.01"
                value={sellPriceAud}
                onChange={(e) => setSellPriceAud(e.target.value)}
              />
            </FormField>
            <FormField id="product-cost-price" label="Cost price (AUD)">
              <Input
                type="number"
                min={0}
                step="0.01"
                value={costPriceAud}
                onChange={(e) => setCostPriceAud(e.target.value)}
              />
            </FormField>
          </div>

          <div className="rounded-md border bg-muted/40 p-4 text-sm">
            <p className="font-medium">GST preview</p>
            <div className="mt-2 grid gap-1 text-muted-foreground sm:grid-cols-3">
              <span>Ex GST: ${(gstPreview.exGst / 100).toFixed(2)}</span>
              <span>GST ({(gstPreview.gstRate * 100).toFixed(0)}%): ${(gstPreview.gstCents / 100).toFixed(2)}</span>
              <span>Inc GST: ${(gstPreview.incGst / 100).toFixed(2)}</span>
            </div>
          </div>

          <FormField id="product-short-description" label="Short description">
            <Textarea
              rows={2}
              value={shortDescription}
              onChange={(e) => setShortDescription(e.target.value)}
            />
          </FormField>

          <FormField id="product-description" label="Description">
            <Textarea rows={4} value={description} onChange={(e) => setDescription(e.target.value)} />
          </FormField>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Product images</p>
              <Button type="button" size="sm" variant="outline" onClick={handleAddImage}>
                <ImagePlus className="mr-2 size-4" />
                Add image
              </Button>
            </div>
            {images.map((image, index) => (
              <div key={index} className="space-y-2 rounded-md border p-3">
                <FormField id={`product-image-url-${index}`} label={`Image URL ${index + 1}`}>
                  <Input
                    value={image.url}
                    onChange={(e) => handleImageChange(index, "url", e.target.value)}
                    placeholder="https://..."
                  />
                </FormField>
                <FormField id={`product-image-alt-${index}`} label="Alt text">
                  <Input
                    value={image.altText}
                    onChange={(e) => handleImageChange(index, "altText", e.target.value)}
                  />
                </FormField>
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-sm">
                    <Checkbox
                      checked={image.isPrimary}
                      onCheckedChange={() => handleSetPrimaryImage(index)}
                    />
                    Primary image
                  </label>
                  {images.length > 1 ? (
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => handleRemoveImage(index)}
                    >
                      <Trash2 className="mr-2 size-4" />
                      Remove
                    </Button>
                  ) : null}
                </div>
              </div>
            ))}
          </div>

          <label className="flex items-center gap-2 text-sm">
            <Checkbox checked={isActive} onCheckedChange={(checked) => setIsActive(checked === true)} />
            Active (visible in catalog)
          </label>
        </div>

        <SheetFooter className="sticky bottom-0 border-t bg-background pt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => void handleSubmit()}
            disabled={isSubmitting || !name.trim() || !sku.trim()}
          >
            {isSubmitting ? "Saving…" : isEdit ? "Save changes" : "Create product"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}

export { ProductFormSheet };
