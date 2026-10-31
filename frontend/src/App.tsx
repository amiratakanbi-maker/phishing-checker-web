import { useEffect, useState } from "react";
import Landing from "@/Landing";
import Checker from "@/Checker";

type View = "home" | "check";

const readView = (): View =>
  window.location.hash === "#check" ? "check" : "home";

export default function App() {
  const [view, setView] = useState<View>(readView());

  // Use the dark theme everywhere (Watermelon/shadcn parts follow the "dark" class)
  useEffect(() => {
    document.documentElement.classList.add("dark");
  }, []);

  // Keep the page in step with the browser's back/forward buttons
  useEffect(() => {
    const onChange = () => {
      setView(readView());
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  const go = (v: View) => {
    window.location.hash = v;
  };

  return view === "check" ? (
    <Checker onHome={() => go("home")} />
  ) : (
    <Landing onStart={() => go("check")} />
  );
}
