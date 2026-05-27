"use client";

import { useState, useEffect, useRef } from "react";

// ── Types ──────────────────────────────────────────────────────────────────────

interface VoiceDimension {
  name: string;
  description: string;
}

interface CaptionPattern {
  name: string;
  frequency: string;
  description: string;
  examples: string[];
}

interface ToneOfVoice {
  username: string;
  posts_analyzed: number;
  persona_summary: string;
  archetype: string;
  voice_dimensions: VoiceDimension[];
  language: {
    primary: string;
    secondary: string | null;
    mixing_note: string | null;
  };
  caption_patterns: CaptionPattern[];
  motifs: {
    themes: string[];
    places: string[];
    sensory: string[];
  };
  dos: string[];
  donts: string[];
  signature_elements: {
    punctuation: string;
    hashtags: string;
    phrases: string[];
  };
}

const API_URL = "/api";

// ── Loading steps ──────────────────────────────────────────────────────────────

const STEPS = [
  "Connecting to Instagram…",
  "Fetching recent posts…",
  "Reading between the lines…",
  "Identifying voice patterns…",
  "Building your tone of voice profile…",
  "Almost there…",
];

// ── Small helpers ──────────────────────────────────────────────────────────────

function Tag({ label }: { label: string }) {
  return (
    <span className="inline-block px-2.5 py-1 rounded-md bg-stone-100 text-stone-700 text-xs">
      {label}
    </span>
  );
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-[10px] font-semibold tracking-[0.12em] uppercase text-stone-400 mb-4">
      {children}
    </h2>
  );
}

// ── Input view ─────────────────────────────────────────────────────────────────

function InputView({
  onAnalyze,
  error,
}: {
  onAnalyze: (v: string) => void;
  error: string | null;
}) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) onAnalyze(value.trim());
  };

  return (
    <div className="min-h-screen bg-stone-50 flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-10 text-center">
          <div className="inline-block w-8 h-px bg-stone-300 mb-6" />
          <h1 className="text-2xl font-semibold text-stone-900 tracking-tight mb-2">
            Tone of Voice
          </h1>
          <p className="text-stone-500 text-sm leading-relaxed">
            Paste any public Instagram profile — get a detailed
            <br />
            tone of voice guide in ~2 minutes.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={submit} className="space-y-3">
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="username or instagram.com/username"
            className="w-full px-4 py-3.5 bg-white border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 text-sm focus:outline-none focus:ring-2 focus:ring-stone-800 focus:border-transparent transition"
          />
          {error && (
            <p className="text-red-600 text-xs px-1">{error}</p>
          )}
          <button
            type="submit"
            disabled={!value.trim()}
            className="w-full py-3.5 bg-stone-900 text-white rounded-xl text-sm font-medium hover:bg-stone-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Analyze Profile
          </button>
        </form>

        <p className="text-center text-stone-400 text-xs mt-5">
          Works with public profiles only
        </p>
      </div>
    </div>
  );
}

// ── Loading view ───────────────────────────────────────────────────────────────

function LoadingView() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const id = setInterval(
      () => setStep((s) => Math.min(s + 1, STEPS.length - 1)),
      18000
    );
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen bg-stone-50 flex flex-col items-center justify-center gap-5 px-4">
      <div className="w-6 h-6 border-2 border-stone-900 border-t-transparent rounded-full animate-spin" />
      <div className="text-center">
        <p className="text-stone-800 text-sm font-medium">{STEPS[step]}</p>
        <p className="text-stone-400 text-xs mt-1">
          Usually takes 1–2 minutes
        </p>
      </div>
      {/* Progress dots */}
      <div className="flex gap-1.5 mt-2">
        {STEPS.map((_, i) => (
          <div
            key={i}
            className={`w-1.5 h-1.5 rounded-full transition-colors duration-500 ${
              i <= step ? "bg-stone-700" : "bg-stone-300"
            }`}
          />
        ))}
      </div>
    </div>
  );
}

// ── Result view ────────────────────────────────────────────────────────────────

function ResultView({
  result,
  onReset,
}: {
  result: ToneOfVoice;
  onReset: () => void;
}) {
  return (
    <div className="min-h-screen bg-stone-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white/90 backdrop-blur border-b border-stone-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-stone-900 text-sm">
            @{result.username}
          </span>
          <span className="text-stone-400 text-xs">
            {result.posts_analyzed} posts
          </span>
        </div>
        <button
          onClick={onReset}
          className="text-xs text-stone-500 hover:text-stone-900 transition-colors"
        >
          ← New analysis
        </button>
      </div>

      <div className="max-w-2xl mx-auto px-6 py-10 space-y-10">

        {/* Persona */}
        <section>
          <div className="mb-3">
            <span className="inline-block px-3 py-1 bg-stone-900 text-white text-xs font-medium rounded-full">
              {result.archetype}
            </span>
          </div>
          <p className="text-stone-700 text-sm leading-7">
            {result.persona_summary}
          </p>
        </section>

        <hr className="border-stone-200" />

        {/* Voice dimensions */}
        <section>
          <SectionHeader>Voice Dimensions</SectionHeader>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {result.voice_dimensions.map((d, i) => (
              <div
                key={i}
                className="bg-white border border-stone-200 rounded-xl p-4"
              >
                <div className="text-stone-900 text-sm font-medium mb-1.5">
                  {d.name}
                </div>
                <div className="text-stone-500 text-xs leading-5">
                  {d.description}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Language */}
        {(result.language.primary || result.language.secondary) && (
          <section>
            <SectionHeader>Language</SectionHeader>
            <div className="bg-white border border-stone-200 rounded-xl divide-y divide-stone-100">
              <Row label="Primary" value={result.language.primary} />
              {result.language.secondary && (
                <Row label="Secondary" value={result.language.secondary} />
              )}
              {result.language.mixing_note && (
                <Row label="Mixing" value={result.language.mixing_note} />
              )}
            </div>
          </section>
        )}

        {/* Caption patterns */}
        <section>
          <SectionHeader>Caption Patterns</SectionHeader>
          <div className="space-y-3">
            {result.caption_patterns.map((p, i) => (
              <div
                key={i}
                className="bg-white border border-stone-200 rounded-xl p-4"
              >
                <div className="flex items-baseline justify-between mb-1.5">
                  <span className="text-stone-900 text-sm font-medium">
                    {p.name}
                  </span>
                  <span className="text-stone-400 text-xs">{p.frequency}</span>
                </div>
                <p className="text-stone-600 text-xs leading-5 mb-3">
                  {p.description}
                </p>
                {p.examples.length > 0 && (
                  <div className="space-y-1.5">
                    {p.examples.map((ex, j) => (
                      <div
                        key={j}
                        className="text-stone-500 text-xs italic pl-3 border-l-2 border-stone-200"
                      >
                        &ldquo;{ex}&rdquo;
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Motifs */}
        <section>
          <SectionHeader>Themes & Motifs</SectionHeader>
          <div className="bg-white border border-stone-200 rounded-xl p-4 space-y-4">
            {result.motifs.themes.length > 0 && (
              <MotifGroup label="Themes" items={result.motifs.themes} />
            )}
            {result.motifs.places.length > 0 && (
              <MotifGroup label="Places" items={result.motifs.places} />
            )}
            {result.motifs.sensory.length > 0 && (
              <MotifGroup label="Sensory anchors" items={result.motifs.sensory} />
            )}
          </div>
        </section>

        {/* Dos & Don'ts */}
        <section>
          <SectionHeader>The Rules</SectionHeader>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
              <div className="text-emerald-700 text-[10px] font-semibold tracking-widest uppercase mb-3">
                Do
              </div>
              <ul className="space-y-2.5">
                {result.dos.map((item, i) => (
                  <li key={i} className="flex gap-2 text-emerald-800 text-xs leading-5">
                    <span className="mt-0.5 flex-shrink-0">✓</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-red-50 border border-red-100 rounded-xl p-4">
              <div className="text-red-700 text-[10px] font-semibold tracking-widest uppercase mb-3">
                Don&apos;t
              </div>
              <ul className="space-y-2.5">
                {result.donts.map((item, i) => (
                  <li key={i} className="flex gap-2 text-red-800 text-xs leading-5">
                    <span className="mt-0.5 flex-shrink-0">✗</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* Signature elements */}
        <section>
          <SectionHeader>Signature Elements</SectionHeader>
          <div className="bg-white border border-stone-200 rounded-xl divide-y divide-stone-100">
            <Row label="Punctuation" value={result.signature_elements.punctuation} />
            <Row label="Hashtags" value={result.signature_elements.hashtags} />
            {result.signature_elements.phrases.length > 0 && (
              <div className="px-4 py-3">
                <div className="text-stone-400 text-xs mb-2">Phrases</div>
                <div className="flex flex-wrap gap-1.5">
                  {result.signature_elements.phrases.map((p, i) => (
                    <span
                      key={i}
                      className="inline-block px-2.5 py-1 bg-stone-100 text-stone-700 text-xs rounded-md italic"
                    >
                      &ldquo;{p}&rdquo;
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Footer */}
        <div className="pt-4 pb-10 text-center text-stone-400 text-xs">
          Tone of Voice · Powered by Claude
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-4 px-4 py-3">
      <span className="text-stone-400 text-xs w-24 flex-shrink-0 pt-px">{label}</span>
      <span className="text-stone-800 text-xs leading-5">{value}</span>
    </div>
  );
}

function MotifGroup({ label, items }: { label: string; items: string[] }) {
  return (
    <div>
      <div className="text-stone-400 text-xs mb-2">{label}</div>
      <div className="flex flex-wrap gap-1.5">
        {items.map((t, i) => (
          <Tag key={i} label={t} />
        ))}
      </div>
    </div>
  );
}

// ── Root ───────────────────────────────────────────────────────────────────────

type AppState = "idle" | "loading" | "result";

export default function Home() {
  const [state, setState] = useState<AppState>("idle");
  const [result, setResult] = useState<ToneOfVoice | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (username: string) => {
    setState("loading");
    setError(null);

    try {
      const resp = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });

      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || `Error ${resp.status}`);
      }

      const data: ToneOfVoice = await resp.json();
      setResult(data);
      setState("result");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setState("idle");
    }
  };

  if (state === "loading") return <LoadingView />;
  if (state === "result" && result)
    return (
      <ResultView result={result} onReset={() => { setResult(null); setState("idle"); }} />
    );
  return <InputView onAnalyze={analyze} error={error} />;
}
