import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

const tiers = [
  {
    name: "Starter",
    price: "$9",
    period: "/month",
    description: "For individuals getting started with the basics.",
    features: [
      "5 projects",
      "10GB storage",
      "Basic analytics",
      "Email support",
    ],
    cta: "Start free trial",
    variant: "outline" as const,
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$29",
    period: "/month",
    description: "For growing teams that need more power and flexibility.",
    features: [
      "Unlimited projects",
      "100GB storage",
      "Advanced analytics",
      "Priority support",
      "Custom integrations",
      "Team collaboration",
    ],
    cta: "Get started",
    variant: "default" as const,
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "$99",
    period: "/month",
    description: "For organizations with advanced security and scale needs.",
    features: [
      "Unlimited everything",
      "1TB storage",
      "Custom analytics",
      "Dedicated support",
      "SSO & SAML",
      "SLA guarantee",
      "Audit logs",
    ],
    cta: "Contact sales",
    variant: "outline" as const,
    highlighted: false,
  },
] as const;

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-background">
      <section
        className="mx-auto max-w-5xl px-4 py-16 sm:px-6 sm:py-24"
        aria-labelledby="pricing-heading"
      >
        <div className="text-center">
          <Badge variant="secondary" className="mb-4">
            Pricing
          </Badge>
          <h1
            id="pricing-heading"
            className="text-3xl font-bold tracking-tight text-foreground sm:text-5xl"
          >
            Simple, transparent pricing
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-muted-foreground sm:text-lg">
            Choose the plan that fits your needs. All plans include a 14-day
            free trial with no credit card required.
          </p>
        </div>

        <div className="mt-12 grid gap-6 sm:mt-16 sm:grid-cols-2 lg:grid-cols-3">
          {tiers.map((tier) => (
            <Card
              key={tier.name}
              className={cn(
                "relative flex flex-col",
                tier.highlighted &&
                  "border-primary shadow-md ring-1 ring-primary/20"
              )}
            >
              {tier.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge>Most popular</Badge>
                </div>
              )}
              <CardHeader>
                <CardTitle className="text-lg">{tier.name}</CardTitle>
                <CardDescription>{tier.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1">
                <p className="flex items-baseline gap-1">
                  <span className="text-4xl font-bold tracking-tight text-foreground">
                    {tier.price}
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {tier.period}
                  </span>
                </p>
                <ul
                  className="mt-6 space-y-3"
                  role="list"
                  aria-label={`${tier.name} plan features`}
                >
                  {tier.features.map((feature) => (
                    <li
                      key={feature}
                      className="flex items-start gap-2 text-sm text-foreground"
                    >
                      <Check
                        className="mt-0.5 size-4 shrink-0 text-primary"
                        aria-hidden="true"
                      />
                      {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button variant={tier.variant} className="w-full" size="lg">
                  {tier.cta}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </section>
    </main>
  );
}
