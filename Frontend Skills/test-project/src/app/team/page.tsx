import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const teamMembers = [
  {
    name: "Josh Kopelman",
    role: "Partner",
    location: "New York",
    category: "Healthcare",
    stage: "Seed",
    company: "Pomelo Care",
    founder: "Marta Bralic Kerns",
    founderRole: "Founder",
    description:
      "Imagine if motherhood came with a care team that actually understood you — that's what Pomelo is building.",
  },
  {
    name: "Brett Berson",
    role: "Partner",
    location: "San Francisco",
    category: "Enterprise / AI",
    stage: "Seed",
    company: "Baseten",
    founder: "Tuhin Srivastava",
    founderRole: "Co-Founder & CEO",
    description:
      "The infrastructure layer for deploying ML models at scale — making production AI accessible to every team.",
  },
  {
    name: "Phin Barnes",
    role: "Partner",
    location: "Portland",
    category: "Developer Tools",
    stage: "Seed",
    company: "Railway",
    founder: "Jake Cooper",
    founderRole: "Founder & CEO",
    description:
      "Deploy anything, anywhere. Railway is rethinking how developers ship software from first line to production.",
  },
];

const navItems = ["Portfolio", "Team", "Platform", "Perspectives"];

export default function TeamPage() {
  return (
    <div
      className="min-h-screen font-sans"
      style={{ backgroundColor: "var(--figma-bg-cream)" }}
    >
      <header
        className="border-b px-6 py-5 lg:px-16"
        style={{ borderColor: "var(--figma-border-warm)" }}
      >
        <nav className="mx-auto flex max-w-7xl items-center justify-between">
          <a
            href="/"
            className="inline-flex min-h-[44px] items-center text-2xl font-semibold tracking-tight"
            style={{ color: "var(--figma-text-body)" }}
          >
            First Round
          </a>
          <ul className="hidden gap-2 md:flex" role="list">
            {navItems.map((item) => (
              <li key={item}>
                <Button
                  variant="outline"
                  size="sm"
                  className="rounded-sm border font-normal"
                  style={{
                    borderColor: "var(--figma-border-warm)",
                    color: "var(--figma-text-nav)",
                    backgroundColor: "var(--figma-bg-cream)",
                  }}
                >
                  {item}
                </Button>
              </li>
            ))}
          </ul>
        </nav>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-12 lg:px-16 lg:py-20">
        <div className="mb-12 max-w-2xl lg:mb-16">
          <h1
            className="font-semibold leading-tight tracking-tight"
            style={{
              fontSize: "var(--figma-heading-size)",
              color: "var(--figma-text-body)",
            }}
          >
            Our Team
          </h1>
          <p
            className="mt-4 max-w-lg leading-relaxed"
            style={{
              fontSize: "var(--figma-body-size)",
              color: "var(--figma-text-muted)",
            }}
          >
            We partner with founders at the earliest stages, helping them build
            companies that reshape industries.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {teamMembers.map((member) => (
            <Card
              key={member.name}
              className="overflow-hidden border-0 shadow-none transition-transform duration-200 hover:-translate-y-0.5"
              style={{ backgroundColor: "var(--figma-bg-light)" }}
            >
              <div
                className="relative aspect-[4/3] w-full"
                style={{ backgroundColor: "var(--figma-card-warm)" }}
              >
                <div
                  className="absolute inset-0 opacity-60"
                  style={{
                    background: `linear-gradient(to bottom, transparent 40%, var(--figma-card-warm-dark))`,
                  }}
                />
                <div className="absolute bottom-4 left-4 right-4">
                  <p className="text-sm font-medium text-white/80">
                    {member.location}
                  </p>
                  <p className="text-lg font-semibold text-white">
                    {member.name}
                  </p>
                  <p className="text-sm text-white/70">{member.role}</p>
                </div>
              </div>

              <CardHeader className="gap-3 px-5 pt-5 pb-0">
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className="rounded-sm text-xs font-normal"
                    style={{
                      borderColor: "var(--figma-border-warm)",
                      color: "var(--figma-text-nav)",
                    }}
                  >
                    {member.stage}
                  </Badge>
                  <Badge
                    variant="outline"
                    className="rounded-sm text-xs font-normal"
                    style={{
                      borderColor: "var(--figma-border-warm)",
                      color: "var(--figma-text-nav)",
                    }}
                  >
                    {member.category}
                  </Badge>
                </div>
                <h2
                  className="text-base font-semibold leading-none"
                  style={{ color: "var(--figma-text-body)" }}
                >
                  {member.company}
                </h2>
              </CardHeader>

              <CardContent className="px-5 pt-2 pb-0">
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "var(--figma-text-muted)" }}
                >
                  {member.description}
                </p>
                <p
                  className="mt-3 text-xs"
                  style={{ color: "var(--figma-card-warm-mid)" }}
                >
                  <span className="font-medium">{member.founder}</span>
                  {" — "}
                  {member.founderRole}
                </p>
              </CardContent>

              <CardFooter className="px-5 pt-4 pb-5">
                <a
                  href="#"
                  aria-label={`Read the story about ${member.company}`}
                  className="inline-flex min-h-[44px] items-center gap-1 text-sm font-medium underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2"
                  style={{ color: "var(--figma-card-warm-dark)" }}
                >
                  Read the story
                  <span aria-hidden="true">&rarr;</span>
                </a>
              </CardFooter>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
