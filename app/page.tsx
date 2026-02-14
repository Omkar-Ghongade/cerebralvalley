"use client";

import { useState } from "react";
import { Loader2, Terminal, BookOpen } from "lucide-react";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [solutionSteps, setSolutionSteps] = useState<string | null>(null);
  const [manimScript, setManimScript] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!prompt) return;

    setLoading(true);
    setError(null);
    setSolutionSteps(null);
    setManimScript(null);
    setVideoUrl(null);

    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate solution");
      }

      const data = await response.json();
      if (data.status === "success" || data.status === "partial_success") {
        setSolutionSteps(data.solution_steps);
        setManimScript(data.manim_script);
        if (data.video_url) {
          setVideoUrl(data.video_url);
        }
      } else {
        setError("Something went wrong with generation.");
      }
    } catch (err: any) {
      setError(err.message || "Error connecting to server. Make sure backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-start p-24 bg-neutral-950 text-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 dark:from-inherit lg:static lg:w-auto  lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30">
          Manim Math Solver&nbsp;
          <code className="font-mono font-bold">by Gemini</code>
        </p>
      </div>

      <div className="mt-12 w-full max-w-4xl flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <label className="font-semibold text-lg">Enter your Math/Physics Question</label>
          <textarea
            className="w-full h-32 p-4 rounded-lg bg-neutral-900 border border-neutral-700 focus:ring-2 focus:ring-blue-600 outline-none transition-all placeholder:text-neutral-600"
            placeholder="e.g. A ball is thrown at 45 degrees with 10m/s velocity. Calculate the range."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading || !prompt}
          className="w-full p-4 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-800 disabled:text-neutral-500 font-bold transition-all flex items-center justify-center gap-2"
        >
          {loading ? <><Loader2 className="animate-spin" /> Solving...</> : "Solve & Generate Script"}
        </button>

        {error && (
          <div className="p-4 bg-red-900/50 border border-red-500/50 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {/* Video Player */}
        {videoUrl && (
          <div className="mt-8 flex flex-col gap-2">
            <h2 className="text-xl font-bold">Generated Animation</h2>
            <div className="w-full aspect-video bg-black rounded-lg overflow-hidden border border-neutral-800 shadow-2xl shadow-blue-900/20">
              <video controls src={videoUrl} className="w-full h-full" autoPlay loop />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
