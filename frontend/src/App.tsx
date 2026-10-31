import { useEffect, useState } from "react";
import { TriangleAlert, ShieldAlert, ShieldCheck } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
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

const alertLook = (level: string) =>
  level === "HIGH RISK"
    ? { style: "bg-red-700", Icon: ShieldAlert }
    : level === "SUSPICIOUS"
      ? { style: "bg-amber-700", Icon: TriangleAlert }
      : { style: "bg-green-700", Icon: ShieldCheck };

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

const barColour = (level: string) =>
  level === "HIGH RISK"
    ? "bg-red-500"
    : level === "SUSPICIOUS"
      ? "bg-amber-500"
      : "bg-emerald-500";

export default function App() {
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
        "Something went wrong while checking that message. Is the backend running?"
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

  // Turn each finding into a card for the Watermelon accordion
  const accordionItems = result?.findings.map((f, i) => ({
    id: i + 1,
    title: `${f.reason} (adds ${Math.round(f.weight * 100)}% risk)`,
    icon: <TriangleAlert size={22} />,
    content: f.why,
  }));

  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-3xl font-semibold tracking-tight">
        Phishing Message Checker
      </h1>
      <p className="mt-3 text-muted-foreground">
        Got a text or email you're not sure about? Paste it below and this tool
        will estimate how likely it is to be a scam, and explain why.
      </p>
      <p className="mt-2 text-sm text-muted-foreground">
        This tool does not save the messages you paste. Even so, please don't
        paste anything containing passwords or card numbers.
      </p>

      <label className="mt-8 block text-sm font-medium">Try an example</label>
      <select
        className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2"
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

      <label className="mt-6 block text-sm font-medium">
        Paste the message here
      </label>
      <textarea
        className="mt-1 h-60 w-full rounded-lg border border-border bg-background p-3"
        maxLength={10000}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Paste the text message or email here. For emails, include the From: line if you can."
      />

      <div className="mt-4 flex gap-3">
        <button
          onClick={check}
          disabled={loading}
          className="rounded-lg bg-primary px-5 py-2 font-medium text-primary-foreground disabled:opacity-60"
        >
          {loading ? "Checking…" : "Check message"}
        </button>
        <button
          onClick={clearAll}
          className="rounded-lg border border-border px-5 py-2"
        >
          Clear
        </button>
      </div>

      {error && (
        <div
          role="alert"
          className="mt-6 rounded-lg border border-red-500/40 bg-red-500/10 p-4"
        >
          {error}
        </div>
      )}

      {result && (
        <section className="mt-8 space-y-6">
          <div>
            <p className="text-sm text-muted-foreground">Phishing risk</p>
            <p className="text-4xl font-semibold">{result.score}%</p>
            <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-muted">
              <div
                className={`h-full ${barColour(result.level)}`}
                style={{ width: `${result.score}%` }}
              />
            </div>
          </div>

          <ResultAlert level={result.level} advice={result.advice} />

          {result.notes.map((note, i) => (
            <div
              key={i}
              className="rounded-lg border border-border bg-muted p-4 text-sm"
            >
              {note}
            </div>
          ))}

          <div>
            <h2 className="text-xl font-semibold">Why this result?</h2>
            {result.findings.length === 0 ? (
              <p className="mt-2">No warning signs were found.</p>
            ) : (
              <AccordionApp items={accordionItems} />
            )}
          </div>

          {result.links.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold">
                Links found in the message
              </h2>
              <p className="text-sm text-muted-foreground">
                Shown as plain text on purpose. Do not type or click these.
              </p>
              <div className="mt-3 space-y-2">
                {result.links.map((l, i) => (
                  <code
                    key={i}
                    className="block break-all rounded-md bg-muted px-3 py-2 text-sm select-all"
                  >
                    {l}
                  </code>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      <hr className="my-10 border-border" />
      <details className="mb-3">
        <summary className="cursor-pointer font-medium">
          How does this work?
        </summary>
        <p className="mt-2 text-muted-foreground">
          The checker looks for warning signs that scam messages often share:
          pressure to act quickly, links that go to look-alike or number-only
          websites, senders pretending to be a well-known company, fake job and
          prize offers, claims that you are owed money, and wording that has
          been disguised to get past spam filters. Each warning sign adds to the
          risk score.
        </p>
        <p className="mt-2 text-muted-foreground">
          It is a guide, not a guarantee. A low score does not prove a message
          is safe, and a high score does not prove it is a scam. If in doubt,
          contact the company using a phone number or website you already trust.
        </p>
      </details>
      <details>
        <summary className="cursor-pointer font-medium">
          Think it's a scam? Report it
        </summary>
        <p className="mt-2 text-muted-foreground">
          In the UK you can forward suspicious texts to 7726 (it's free) and
          suspicious emails to report@phishing.gov.uk.
        </p>
      </details>
    </main>
  );
}
