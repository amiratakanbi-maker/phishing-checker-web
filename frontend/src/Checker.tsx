import { useEffect, useState } from "react";
import { TriangleAlert, ShieldAlert, ShieldCheck, Loader2, ArrowLeft } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AccordionApp } from "@/components/card-split-accordian";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type Finding = { reason: string; why: string; weight: number };
type Result = {
  score: number;
  level: string;
  advice: string;
  notes: string[];
  findings: Finding[];
  links: string[];
};

// Brand colours (burgundy). Change these two lines to re-colour the whole page.
const BURGUNDY = "bg-[#8a1538] hover:bg-[#a31a42]";
const FOCUS = "focus:border-[#b3204d] focus:outline-none focus:ring-2 focus:ring-[#b3204d]/40";

const alertLook = (level: string) =>
  level === "HIGH RISK"
    ? { style: "bg-red-700", Icon: ShieldAlert }
    : level === "SUSPICIOUS"
      ? { style: "bg-amber-700", Icon: TriangleAlert }
      : { style: "bg-green-700", Icon: ShieldCheck };

const barColour = (level: string) =>
  level === "HIGH RISK"
    ? "bg-red-600"
    : level === "SUSPICIOUS"
      ? "bg-amber-500"
      : "bg-green-500";

function ResultAlert({ level, advice }: { level: string; advice: string }) {
  const { style, Icon } = alertLook(level);
  return (
    <Alert className={`border-none text-white ${style}`}>
      <Icon className="size-4" />
      <AlertTitle>{level}</AlertTitle>
      <AlertDescription className="text-white/80">{advice}</AlertDescription>
    </Alert>
  );
}

export default function Checker({ onHome }: { onHome: () => void }) {
  const [message, setMessage] = useState("");
  const [examples, setExamples] = useState<Record<string, string>>({});
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/examples`)
      .then((r) => r.json())
      .then(setExamples)
      .catch(() => {});
  }, []);

  async function check() {
    setError("");
    setResult(null);
    if (!message.trim()) {
      setError("Please paste a message first.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok) throw new Error();
      setResult(await res.json());
    } catch {
      setError(
        "Something went wrong while checking that message. Please try again with just the message text."
      );
    } finally {
      setLoading(false);
    }
  }

  function clearAll() {
    setMessage("");
    setResult(null);
    setError("");
  }

  const accordionItems = result?.findings.map((f, i) => ({
    id: i + 1,
    title: `${f.reason} (adds ${Math.round(f.weight * 100)}% risk)`,
    icon: <TriangleAlert size={22} />,
    content: f.why,
  }));

  return (
    <div className="dark min-h-screen bg-black text-white">
      <main className="mx-auto max-w-2xl px-4 py-10 sm:py-16">
        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={onHome}
            className="flex items-center gap-3 text-left"
            aria-label="Back to home page"
          >
            <div className="flex size-11 items-center justify-center rounded-xl bg-[#8a1538]">
              <ShieldCheck className="size-6" />
            </div>
            <span className="text-sm font-semibold uppercase tracking-[0.2em] text-white/60">
              Message Checker
            </span>
          </button>
          <button
            onClick={onHome}
            className="flex items-center gap-1 text-sm text-white/60 hover:text-white"
          >
            <ArrowLeft className="size-4" /> Home
          </button>
        </div>

        <h1 className="mt-8 text-4xl font-bold leading-tight tracking-tight sm:text-5xl">
          Is that message
          <br />
          <span className="text-[#d6366a]">a scam?</span>
        </h1>
        <p className="mt-5 max-w-xl text-lg text-white/70">
          Got a text or email you're not sure about? Paste it below and this tool
          will estimate how likely it is to be a scam, and explain why.
        </p>
        <p className="mt-3 text-sm text-white/50">
          This tool does not save the messages you paste. Even so, please don't
          paste anything containing passwords or card numbers.
        </p>

        {/* Input card */}
        <section className="mt-10 rounded-2xl border border-white/10 bg-neutral-950 p-5 sm:p-7">
          <label className="block text-sm font-medium text-white/80">
            Try an example
          </label>
          <select
            className={`mt-2 w-full rounded-xl border border-white/15 bg-neutral-900 px-4 py-3 text-white ${FOCUS}`}
            value=""
            onChange={(e) => {
              setMessage(examples[e.target.value] ?? "");
              setResult(null);
              setError("");
            }}
          >
            <option value="">Choose an example…</option>
            {Object.keys(examples).map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>

          <label className="mt-6 block text-sm font-medium text-white/80">
            Paste the message here
          </label>
          <textarea
            className={`mt-2 h-56 w-full resize-y rounded-xl border border-white/15 bg-neutral-900 p-4 text-white placeholder:text-white/35 ${FOCUS}`}
            maxLength={10000}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Paste the text message or email here. For emails, include the From: line if you can."
          />

          <div className="mt-5 flex flex-wrap gap-3">
            <Button
              size="lg"
              onClick={check}
              disabled={loading}
              className={`${BURGUNDY} px-8 text-white`}
            >
              {loading && <Loader2 className="mr-2 size-4 animate-spin" />}
              {loading ? "Checking…" : "Check message"}
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={clearAll}
              className="border-white/20 bg-transparent text-white hover:bg-white/10 hover:text-white"
            >
              Clear
            </Button>
          </div>

          {error && (
            <div
              role="alert"
              className="mt-5 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-200"
            >
              {error}
            </div>
          )}
        </section>

        {/* Result */}
        {result && (
          <section className="mt-8 space-y-6 rounded-2xl border border-white/10 bg-neutral-950 p-5 sm:p-7">
            <div>
              <p className="text-sm uppercase tracking-widest text-white/50">
                Phishing risk
              </p>
              <p className="mt-1 text-6xl font-bold tracking-tight">
                {result.score}%
              </p>
              <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-white/10">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${barColour(result.level)}`}
                  style={{ width: `${result.score}%` }}
                />
              </div>
            </div>

            <ResultAlert level={result.level} advice={result.advice} />

            {result.notes.map((note, i) => (
              <div
                key={i}
                className="rounded-xl border border-white/10 bg-neutral-900 p-4 text-sm text-white/80"
              >
                {note}
              </div>
            ))}

            <div>
              <h2 className="text-2xl font-bold">Why this result?</h2>
              {result.findings.length === 0 ? (
                <p className="mt-2 text-white/70">No warning signs were found.</p>
              ) : (
                <AccordionApp items={accordionItems} />
              )}
            </div>

            {result.links.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold">Links found in the message</h2>
                <p className="mt-1 text-sm text-white/50">
                  Shown as plain text on purpose. Do not type or click these.
                </p>
                <div className="mt-3 space-y-2">
                  {result.links.map((l, i) => (
                    <code
                      key={i}
                      className="block break-all rounded-lg border border-white/10 bg-neutral-900 px-3 py-2 text-sm text-white/90 select-all"
                    >
                      {l}
                    </code>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {/* Footer info */}
        <div className="mt-12 space-y-3">
          <details className="rounded-2xl border border-white/10 bg-neutral-950 p-5">
            <summary className="cursor-pointer font-semibold">
              How does this work?
            </summary>
            <p className="mt-3 text-white/70">
              The checker looks for warning signs that scam messages often share:
              pressure to act quickly, links that go to look-alike or number-only
              websites, senders pretending to be a well-known company, fake job
              and prize offers, claims that you are owed money, and wording that
              has been disguised to get past spam filters. Each warning sign adds
              to the risk score.
            </p>
            <p className="mt-3 text-white/70">
              It is a guide, not a guarantee. A low score does not prove a
              message is safe, and a high score does not prove it is a scam. If
              in doubt, contact the company using a phone number or website you
              already trust.
            </p>
          </details>
          <details className="rounded-2xl border border-white/10 bg-neutral-950 p-5">
            <summary className="cursor-pointer font-semibold">
              Think it's a scam? Report it
            </summary>
            <p className="mt-3 text-white/70">
              In the UK you can forward suspicious texts to 7726 (it's free) and
              suspicious emails to report@phishing.gov.uk.
            </p>
          </details>
        </div>
      </main>
    </div>
  );
}
