import {
  ArrowRight,
  Briefcase,
  Building2,
  ClipboardPaste,
  Clock,
  EyeOff,
  Link2,
  ListChecks,
  PoundSterling,
  ScanSearch,
  ShieldCheck,
  TriangleAlert,
  Type,
} from "lucide-react";

const BURGUNDY = "bg-[#8a1538] hover:bg-[#a31a42]";

const steps = [
  {
    icon: ClipboardPaste,
    title: "Paste it",
    text: "Copy the text or email you're unsure about and paste it in. For emails, include the From: line if you can.",
  },
  {
    icon: ScanSearch,
    title: "We check it",
    text: "The checker looks for the warning signs scam messages often share and adds them up into a risk score.",
  },
  {
    icon: ListChecks,
    title: "See why",
    text: "You get a clear result and a plain-English explanation of every warning sign it found.",
  },
];

const signs = [
  { icon: Clock, title: "Pressure to act fast", text: "“Your account closes in 24 hours.” Scammers rush you so you don't stop to think." },
  { icon: Link2, title: "Look-alike links", text: "Web addresses that imitate a real company or are just a string of numbers." },
  { icon: Building2, title: "Fake senders", text: "Messages pretending to be a bank, delivery firm or well-known brand." },
  { icon: Briefcase, title: "Fake job and prize offers", text: "Easy money for a few minutes of work, or a prize you never entered for." },
  { icon: PoundSterling, title: "Claims you're owed money", text: "Refunds, rebates and payments that need you to click or hand over details." },
  { icon: Type, title: "Disguised wording", text: "Odd spellings and symbols used to slip past spam filters." },
];

function HeroGraphic() {
  return (
    <div className="relative mx-auto w-full max-w-md">
      {/* glow */}
      <div className="absolute -inset-10 animate-pulse rounded-full bg-[#8a1538]/30 blur-3xl" />

      <div className="relative rounded-3xl border border-white/10 bg-neutral-950 p-5 shadow-2xl">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-xs uppercase tracking-widest text-white/40">
            Example message
          </span>
          <span className="flex gap-1.5">
            <span className="size-2.5 rounded-full bg-white/15" />
            <span className="size-2.5 rounded-full bg-white/15" />
            <span className="size-2.5 rounded-full bg-[#8a1538]" />
          </span>
        </div>

        {/* message bubble */}
        <div className="rounded-2xl rounded-tl-sm bg-neutral-900 p-4 text-sm leading-relaxed text-white/80">
          <span className="rounded bg-[#8a1538]/40 px-1">PARCEL COULD NOT BE DELIVERED</span>{" "}
          Reschedule your missed delivery now at:{" "}
          <span className="break-all rounded bg-[#8a1538]/40 px-1 underline decoration-[#d6366a]">
            https://evr.i275103uk.com
          </span>
        </div>

        {/* result chip */}
        <div className="mt-4 flex items-center gap-4 rounded-2xl border border-red-500/30 bg-red-500/10 p-4">
          <div className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-red-700">
            <TriangleAlert className="size-6" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-white/50">Phishing risk</p>
            <p className="text-2xl font-bold leading-none">High risk</p>
          </div>
          <ShieldCheck className="ml-auto size-8 text-[#d6366a]" />
        </div>

        <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
          <div className="h-full w-[88%] rounded-full bg-red-600" />
        </div>
        <p className="mt-2 text-xs text-white/40">Illustration only</p>
      </div>
    </div>
  );
}

export default function Landing({ onStart }: { onStart: () => void }) {
  return (
    <div className="dark min-h-screen bg-black text-white">
      {/* Nav */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-[#8a1538]">
            <ShieldCheck className="size-5" />
          </div>
          <span className="text-sm font-semibold uppercase tracking-[0.2em] text-white/70">
            Message Checker
          </span>
        </div>
        <button
          onClick={onStart}
          className="rounded-full border border-white/20 px-5 py-2 text-sm font-medium hover:bg-white/10"
        >
          Check a message
        </button>
      </header>

      {/* Hero */}
      <section className="mx-auto grid max-w-6xl items-center gap-12 px-4 pb-20 pt-10 md:grid-cols-2 md:pt-20">
        <div>
          <p className="mb-4 inline-block rounded-full border border-[#8a1538] bg-[#8a1538]/20 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-[#f08aa9]">
            Free scam checker
          </p>
          <h1 className="text-5xl font-bold leading-[1.05] tracking-tight sm:text-6xl">
            Not sure about
            <br />
            that message?
            <br />
            <span className="text-[#d6366a]">Check it first.</span>
          </h1>
          <p className="mt-6 max-w-lg text-lg text-white/70">
            Paste a text or email and find out how likely it is to be a scam,
            with a clear explanation of exactly why.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <button
              onClick={onStart}
              className={`${BURGUNDY} flex items-center gap-2 rounded-full px-8 py-4 text-lg font-semibold text-white transition active:scale-95`}
            >
              Check a message <ArrowRight className="size-5" />
            </button>
            <button
              onClick={() =>
                document.getElementById("how")?.scrollIntoView({ behavior: "smooth" })
              }
              className="rounded-full px-6 py-4 text-white/70 hover:text-white"
            >
              How it works
            </button>
          </div>
          <p className="mt-6 flex items-center gap-2 text-sm text-white/50">
            <EyeOff className="size-4" />
            This tool does not save the messages you paste.
          </p>
        </div>
        <HeroGraphic />
      </section>

      {/* How it works */}
      <section id="how" className="border-t border-white/10 bg-neutral-950 py-20">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="text-3xl font-bold sm:text-4xl">Three simple steps</h2>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {steps.map((s, i) => (
              <div key={s.title} className="rounded-2xl border border-white/10 bg-black p-6">
                <div className="flex items-center justify-between">
                  <div className="flex size-12 items-center justify-center rounded-xl bg-[#8a1538]">
                    <s.icon className="size-6" />
                  </div>
                  <span className="text-5xl font-bold text-white/10">{i + 1}</span>
                </div>
                <h3 className="mt-5 text-xl font-semibold">{s.title}</h3>
                <p className="mt-2 text-white/60">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Warning signs */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="text-3xl font-bold sm:text-4xl">
            The warning signs we look for
          </h2>
          <p className="mt-3 max-w-2xl text-white/60">
            Scam messages tend to share the same tricks. Knowing them helps you
            spot one even without a tool.
          </p>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {signs.map((s) => (
              <div
                key={s.title}
                className="rounded-2xl border border-white/10 bg-neutral-950 p-6 transition hover:border-[#8a1538]"
              >
                <s.icon className="size-7 text-[#d6366a]" />
                <h3 className="mt-4 text-lg font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm text-white/60">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Honest note + report */}
      <section className="border-t border-white/10 bg-neutral-950 py-20">
        <div className="mx-auto grid max-w-6xl gap-5 px-4 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-black p-7">
            <h3 className="text-xl font-semibold">A guide, not a guarantee</h3>
            <p className="mt-3 text-white/60">
              A low score does not prove a message is safe, and a high score does
              not prove it is a scam. If in doubt, contact the company using a
              phone number or website you already trust. Please don't paste
              passwords or card numbers.
            </p>
          </div>
          <div className="rounded-2xl border border-[#8a1538] bg-[#8a1538]/10 p-7">
            <h3 className="text-xl font-semibold">Think it's a scam? Report it</h3>
            <p className="mt-3 text-white/70">
              In the UK you can forward suspicious texts to{" "}
              <strong>7726</strong> (it's free) and suspicious emails to{" "}
              <strong>report@phishing.gov.uk</strong>.
            </p>
          </div>
        </div>
      </section>

      {/* Final call to action */}
      <section className="py-24 text-center">
        <h2 className="mx-auto max-w-2xl px-4 text-4xl font-bold sm:text-5xl">
          Got a message on your phone right now?
        </h2>
        <button
          onClick={onStart}
          className={`${BURGUNDY} mt-8 inline-flex items-center gap-2 rounded-full px-10 py-4 text-lg font-semibold text-white transition active:scale-95`}
        >
          Check a message <ArrowRight className="size-5" />
        </button>
      </section>

      <footer className="border-t border-white/10 py-8 text-center text-sm text-white/40">
        Phishing Message Checker
      </footer>
    </div>
  );
}
