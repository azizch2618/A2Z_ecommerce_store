"use client";

import * as React from "react";
import { CreditCard, Landmark, Truck, Wallet } from "lucide-react";
import { toast } from "sonner";

import type { CheckoutAddress, CheckoutFormErrors, CheckoutFormState } from "@/types/checkout";
import { brand } from "@/config/brand";
import {
  checkoutBreadcrumbs,
  defaultCheckoutForm,
  getEstimatedDelivery,
  getShippingPriceIncGst,
  paymentMethods,
  shippingMethods,
} from "@/config/checkout-page";
import { calculateCheckoutSummary, formatAud } from "@/lib/cart";
import { useCart } from "@/lib/api/hooks/use-cart";
import { useCreateOrder } from "@/lib/api/hooks/use-orders";
import { usePaymentConfig } from "@/lib/api/hooks/use-payments";
import { mapApiCartToUiItems } from "@/lib/api/mappers/cart-mapper";
import {
  getPhoneError,
  getPostcodeError,
  isValidEmail,
} from "@/lib/australian-address";
import { CheckoutAddressFields } from "@/components/checkout/checkout-address-fields";
import { CheckoutMobileBar } from "@/components/checkout/checkout-mobile-bar";
import { CheckoutOrderSummary } from "@/components/checkout/checkout-order-summary";
import { CheckoutSection } from "@/components/checkout/checkout-section";
import { Container } from "@/components/layout/container";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { cn } from "@/lib/utils";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import type { ApiAddress } from "@/lib/api/types/common";
import { useRouter } from "next/navigation";
import { StripePaymentForm } from "@/components/checkout/stripe-payment-form";

const paymentIcons = {
  card: CreditCard,
  paypal: Wallet,
  bank_transfer: Landmark,
} as const;

function validateAddress(
  address: CheckoutAddress
): Partial<Record<keyof CheckoutAddress, string>> {
  const errors: Partial<Record<keyof CheckoutAddress, string>> = {};
  if (!address.line1.trim()) errors.line1 = "Address line 1 is required";
  if (!address.city.trim()) errors.city = "City is required";
  if (!address.state) errors.state = "Select a state";
  const postcodeError = getPostcodeError(address.postcode);
  if (postcodeError) errors.postcode = postcodeError;
  return errors;
}

function validateCheckoutForm(
  form: CheckoutFormState,
  options?: { stripeCardEnabled?: boolean }
): CheckoutFormErrors {
  const errors: CheckoutFormErrors = {};

  const customerErrors: NonNullable<CheckoutFormErrors["customer"]> = {};
  if (!form.customer.firstName.trim()) {
    customerErrors.firstName = "First name is required";
  }
  if (!form.customer.lastName.trim()) {
    customerErrors.lastName = "Last name is required";
  }
  if (!form.customer.email.trim()) {
    customerErrors.email = "Email is required";
  } else if (!isValidEmail(form.customer.email)) {
    customerErrors.email = "Enter a valid email address";
  }
  const phoneError = getPhoneError(form.customer.phone);
  if (phoneError) customerErrors.phone = phoneError;
  if (Object.keys(customerErrors).length > 0) errors.customer = customerErrors;

  const shippingErrors = validateAddress(form.shipping);
  if (Object.keys(shippingErrors).length > 0) errors.shipping = shippingErrors;

  if (form.paymentMethodId === "card" && !options?.stripeCardEnabled) {
    const paymentErrors: NonNullable<CheckoutFormErrors["payment"]> = {};
    if (!form.cardName.trim()) paymentErrors.cardName = "Name on card is required";
    const digits = form.cardNumber.replace(/\D/g, "");
    if (digits.length < 15) paymentErrors.cardNumber = "Enter a valid card number";
    if (!/^\d{2}\/\d{2}$/.test(form.cardExpiry.trim())) {
      paymentErrors.cardExpiry = "Use MM/YY format";
    }
    if (!/^\d{3,4}$/.test(form.cardCvc.trim())) {
      paymentErrors.cardCvc = "Enter a valid CVC";
    }
    if (Object.keys(paymentErrors).length > 0) errors.payment = paymentErrors;
  }

  return errors;
}

function formatCardNumber(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 16);
  return digits.replace(/(\d{4})(?=\d)/g, "$1 ").trim();
}

function formatCardExpiry(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 4);
  if (digits.length <= 2) return digits;
  return `${digits.slice(0, 2)}/${digits.slice(2)}`;
}

function CheckoutPageView() {
  const router = useRouter();
  const { data: cart } = useCart();
  const { data: paymentConfig } = usePaymentConfig();
  const createOrder = useCreateOrder();
  const stripeEnabled = Boolean(
    paymentConfig?.stripe_enabled && paymentConfig.publishable_key
  );
  const [pendingStripePayment, setPendingStripePayment] = React.useState<{
    orderId: string;
    clientSecret: string;
    orderNumber: string;
  } | null>(null);
  const cartItems = React.useMemo(
    () => (cart ? mapApiCartToUiItems(cart) : []),
    [cart]
  );
  const [form, setForm] = React.useState<CheckoutFormState>(defaultCheckoutForm);
  const [errors, setErrors] = React.useState<CheckoutFormErrors>({});

  const totals = React.useMemo(() => {
    const tradeSubtotal = cartItems.reduce(
      (sum, item) =>
        sum + (item.tradePriceValue ?? item.priceValue) * item.quantity,
      0
    );
    const shippingIncGst = getShippingPriceIncGst(
      form.shippingMethodId,
      tradeSubtotal
    );
    return calculateCheckoutSummary(cartItems, shippingIncGst);
  }, [cartItems, form.shippingMethodId]);

  const estimatedDelivery = getEstimatedDelivery(form.shippingMethodId);

  const updateCustomer = (
    field: keyof CheckoutFormState["customer"],
    value: string
  ) => {
    setForm((current) => ({
      ...current,
      customer: { ...current.customer, [field]: value },
    }));
  };

  const updateShipping = (field: keyof CheckoutAddress, value: string) => {
    setForm((current) => ({
      ...current,
      shipping: { ...current.shipping, [field]: value },
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (pendingStripePayment) {
      return;
    }

    const validationErrors = validateCheckoutForm(form, {
      stripeCardEnabled: stripeEnabled && form.paymentMethodId === "card",
    });
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      toast.error("Please fix the highlighted fields");
      return;
    }

    if (!cart?.id) {
      toast.error("Your cart is empty");
      return;
    }

    const address: ApiAddress = {
      line1: form.shipping.line1,
      line2: form.shipping.line2,
      suburb: form.shipping.city,
      state: form.shipping.state as ApiAddress["state"],
      postcode: form.shipping.postcode,
      country: form.shipping.country || "AU",
    };

    try {
      const order = await createOrder.mutateAsync({
        cart_id: cart.id,
        email: form.customer.email,
        billing_address: address,
        shipping_address: address,
        shipping_method_id: crypto.randomUUID(),
        payment_method: form.paymentMethodId === "bank_transfer" ? "bank_transfer" : "card",
      });

      const clientSecret = order.payment?.client_secret;
      if (form.paymentMethodId === "card" && clientSecret && stripeEnabled) {
        setPendingStripePayment({
          orderId: order.id,
          clientSecret,
          orderNumber: order.order_number,
        });
        toast.message("Complete your card payment below", {
          description: `Order ${order.order_number} created — awaiting payment.`,
        });
        return;
      }

      if (order.payment_status === "paid" || order.status === "paid") {
        toast.success("Order placed successfully", {
          description: `Order ${order.order_number} — ${formatAud(totals.totalIncGst)} AUD inc GST`,
        });
        router.push(`/checkout/success?order_id=${order.id}`);
        return;
      }

      toast.success("Order created", {
        description: `Order ${order.order_number} — follow payment instructions to complete.`,
      });
      router.push(`/account/orders/${order.id}`);
    } catch {
      toast.error("Checkout failed", {
        description: "Sign in with a verified account and try again.",
      });
    }
  };

  return (
    <>
      <PageBreadcrumbs items={checkoutBreadcrumbs} />

      <Container className="pb-28 pt-8 md:pb-10 md:pt-10 lg:pb-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-brand-navy md:text-3xl">Checkout</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Complete your order — secure Australian checkout with GST-inclusive pricing.
          </p>
        </div>

        <form id="checkout-form" onSubmit={handleSubmit}>
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_380px] lg:gap-10 xl:grid-cols-[minmax(0,1fr)_420px]">
            <div className="space-y-6">
              <CheckoutSection
                step={1}
                title="Customer information"
                description="Contact details for your order and tax invoice"
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <FormField
                    id="firstName"
                    label="First name"
                    required
                    error={errors.customer?.firstName}
                  >
                    <Input
                      value={form.customer.firstName}
                      onChange={(e) => updateCustomer("firstName", e.target.value)}
                      autoComplete="given-name"
                    />
                  </FormField>
                  <FormField
                    id="lastName"
                    label="Last name"
                    required
                    error={errors.customer?.lastName}
                  >
                    <Input
                      value={form.customer.lastName}
                      onChange={(e) => updateCustomer("lastName", e.target.value)}
                      autoComplete="family-name"
                    />
                  </FormField>
                  <FormField
                    id="company"
                    label="Company name"
                    className="sm:col-span-2"
                  >
                    <Input
                      value={form.customer.company}
                      onChange={(e) => updateCustomer("company", e.target.value)}
                      placeholder="Business or organisation"
                      autoComplete="organization"
                    />
                  </FormField>
                  <FormField
                    id="email"
                    label="Email"
                    required
                    error={errors.customer?.email}
                  >
                    <Input
                      type="email"
                      value={form.customer.email}
                      onChange={(e) => updateCustomer("email", e.target.value)}
                      placeholder="you@company.com.au"
                      autoComplete="email"
                    />
                  </FormField>
                  <FormField
                    id="phone"
                    label="Phone"
                    required
                    error={errors.customer?.phone}
                    hint="Australian landline or mobile"
                  >
                    <Input
                      type="tel"
                      value={form.customer.phone}
                      onChange={(e) => updateCustomer("phone", e.target.value)}
                      placeholder="02 9123 4567"
                      autoComplete="tel"
                    />
                  </FormField>
                </div>
              </CheckoutSection>

              <CheckoutSection
                step={2}
                title="Shipping address"
                description="Deliver to an Australian business or site address"
              >
                <CheckoutAddressFields
                  idPrefix="shipping"
                  address={form.shipping}
                  errors={errors.shipping}
                  onChange={updateShipping}
                />
              </CheckoutSection>

              <CheckoutSection
                step={3}
                title="Shipping method"
                description="Choose how you'd like to receive your order"
              >
                <RadioGroup
                  value={form.shippingMethodId}
                  onValueChange={(value) =>
                    setForm((current) => ({ ...current, shippingMethodId: value }))
                  }
                  className="gap-3"
                >
                  {shippingMethods.map((method) => {
                    const price = method.getPriceIncGst(totals.tradeSubtotalIncGst);
                    const id = `shipping-${method.id}`;
                    return (
                      <label
                        key={method.id}
                        htmlFor={id}
                        className={cn(
                          "flex cursor-pointer items-start gap-3 rounded-lg border p-4 transition-colors",
                          form.shippingMethodId === method.id
                            ? "border-brand-blue bg-brand-blue-light/30"
                            : "border-border hover:border-brand-blue/30"
                        )}
                      >
                        <RadioGroupItem value={method.id} id={id} className="mt-0.5" />
                        <div className="flex flex-1 flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                          <div className="flex items-start gap-2">
                            <Truck className="mt-0.5 size-4 shrink-0 text-brand-blue" />
                            <div>
                              <p className="font-medium text-brand-navy">{method.label}</p>
                              <p className="text-sm text-muted-foreground">
                                {method.description}
                              </p>
                            </div>
                          </div>
                          <p className="pl-6 text-sm font-semibold tabular-nums text-brand-navy sm:pl-0">
                            {price === 0 ? (
                              <span className="text-success">Free</span>
                            ) : (
                              formatAud(price)
                            )}
                          </p>
                        </div>
                      </label>
                    );
                  })}
                </RadioGroup>
              </CheckoutSection>

              <CheckoutSection
                step={4}
                title="Payment method"
                description={
                  stripeEnabled
                    ? "Pay securely with Stripe — card details are never stored on our servers"
                    : "Select how you'd like to pay"
                }
              >
                <RadioGroup
                  value={form.paymentMethodId}
                  onValueChange={(value) =>
                    setForm((current) => ({ ...current, paymentMethodId: value }))
                  }
                  className="gap-3"
                >
                  {paymentMethods.map((method) => {
                    const Icon = paymentIcons[method.id as keyof typeof paymentIcons];
                    const id = `payment-${method.id}`;
                    return (
                      <label
                        key={method.id}
                        htmlFor={id}
                        className={cn(
                          "flex cursor-pointer items-start gap-3 rounded-lg border p-4 transition-colors",
                          form.paymentMethodId === method.id
                            ? "border-brand-blue bg-brand-blue-light/30"
                            : "border-border hover:border-brand-blue/30"
                        )}
                      >
                        <RadioGroupItem value={method.id} id={id} className="mt-0.5" />
                        <div className="flex flex-1 items-start gap-3">
                          <Icon className="mt-0.5 size-5 shrink-0 text-brand-blue" />
                          <div>
                            <p className="font-medium text-brand-navy">{method.label}</p>
                            <p className="text-sm text-muted-foreground">
                              {method.description}
                            </p>
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </RadioGroup>

                {form.paymentMethodId === "card" && stripeEnabled && pendingStripePayment ? (
                  <div className="mt-5 space-y-4 rounded-lg border border-border bg-neutral-50/80 p-4">
                    <div className="flex items-center gap-2 text-sm font-medium text-brand-navy">
                      <CreditCard className="size-4 text-brand-blue" />
                      Secure card payment
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Order {pendingStripePayment.orderNumber} — enter your card details to
                      complete payment.
                    </p>
                    <StripePaymentForm
                      publishableKey={paymentConfig!.publishable_key}
                      clientSecret={pendingStripePayment.clientSecret}
                      orderId={pendingStripePayment.orderId}
                      isSubmitting={createOrder.isPending}
                    />
                  </div>
                ) : null}

                {form.paymentMethodId === "card" && stripeEnabled && !pendingStripePayment ? (
                  <div className="mt-5 rounded-lg border border-dashed border-border bg-neutral-50/80 p-4 text-sm text-muted-foreground">
                    Card details will appear after you place your order. Payment is processed
                    securely by Stripe.
                  </div>
                ) : null}

                {form.paymentMethodId === "card" && !stripeEnabled ? (
                  <div className="mt-5 space-y-4 rounded-lg border border-dashed border-border bg-neutral-50/80 p-4">
                    <div className="flex items-center gap-2 text-sm font-medium text-brand-navy">
                      <CreditCard className="size-4 text-brand-blue" />
                      Card details (demo only)
                    </div>
                    <FormField
                      id="cardName"
                      label="Name on card"
                      required
                      error={errors.payment?.cardName}
                    >
                      <Input
                        value={form.cardName}
                        onChange={(e) =>
                          setForm((c) => ({ ...c, cardName: e.target.value }))
                        }
                        autoComplete="cc-name"
                      />
                    </FormField>
                    <FormField
                      id="cardNumber"
                      label="Card number"
                      required
                      error={errors.payment?.cardNumber}
                    >
                      <Input
                        value={form.cardNumber}
                        onChange={(e) =>
                          setForm((c) => ({
                            ...c,
                            cardNumber: formatCardNumber(e.target.value),
                          }))
                        }
                        placeholder="4242 4242 4242 4242"
                        inputMode="numeric"
                        autoComplete="cc-number"
                      />
                    </FormField>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <FormField
                        id="cardExpiry"
                        label="Expiry"
                        required
                        error={errors.payment?.cardExpiry}
                      >
                        <Input
                          value={form.cardExpiry}
                          onChange={(e) =>
                            setForm((c) => ({
                              ...c,
                              cardExpiry: formatCardExpiry(e.target.value),
                            }))
                          }
                          placeholder="MM/YY"
                          inputMode="numeric"
                          autoComplete="cc-exp"
                        />
                      </FormField>
                      <FormField
                        id="cardCvc"
                        label="CVC"
                        required
                        error={errors.payment?.cardCvc}
                      >
                        <Input
                          value={form.cardCvc}
                          onChange={(e) =>
                            setForm((c) => ({
                              ...c,
                              cardCvc: e.target.value.replace(/\D/g, "").slice(0, 4),
                            }))
                          }
                          placeholder="123"
                          inputMode="numeric"
                          autoComplete="cc-csc"
                        />
                      </FormField>
                    </div>
                  </div>
                ) : null}

                {form.paymentMethodId === "paypal" ? (
                  <div className="mt-5 rounded-lg border border-dashed border-border bg-neutral-50/80 p-6 text-center">
                    <p className="text-sm text-muted-foreground">
                      You will be redirected to PayPal to complete payment.
                    </p>
                    <Button type="button" variant="outline" className="mt-4" disabled>
                      Pay with PayPal (demo)
                    </Button>
                  </div>
                ) : null}

                {form.paymentMethodId === "bank_transfer" ? (
                  <div className="mt-5 rounded-lg border border-border bg-neutral-50/80 p-4 text-sm">
                    <p className="font-medium text-brand-navy">Bank transfer details</p>
                    <dl className="mt-3 space-y-1 text-muted-foreground">
                      <div className="flex justify-between gap-4">
                        <dt>Account name</dt>
                        <dd className="font-medium text-foreground">{brand.legalName}</dd>
                      </div>
                      <div className="flex justify-between gap-4">
                        <dt>BSB</dt>
                        <dd className="font-mono font-medium text-foreground">062-000</dd>
                      </div>
                      <div className="flex justify-between gap-4">
                        <dt>Account</dt>
                        <dd className="font-mono font-medium text-foreground">1234 5678</dd>
                      </div>
                      <div className="flex justify-between gap-4">
                        <dt>Reference</dt>
                        <dd className="font-medium text-foreground">Your company name</dd>
                      </div>
                    </dl>
                  </div>
                ) : null}
              </CheckoutSection>
            </div>

            <CheckoutOrderSummary
              items={cartItems}
              totals={totals}
              estimatedDelivery={estimatedDelivery}
              isSubmitting={createOrder.isPending}
            />
          </div>
        </form>
      </Container>

      <CheckoutMobileBar totals={totals} isSubmitting={createOrder.isPending} />
    </>
  );
}

export { CheckoutPageView };
