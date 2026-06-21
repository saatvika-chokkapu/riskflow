import { useState } from "react";
import CostAnalysis from "./components/CostAnalysis";
import ThresholdSimulator from "./components/ThresholdSimulator";
import PipelineHealth from "./components/PipelineHealth";

function App() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  return (
    <div data-theme={theme} style={{
      minHeight: "100vh",
      background: "var(--page)",
      color: "var(--text)",
      fontFamily: "'IBM Plex Sans', sans-serif",
      transition: "background .3s, color .3s",
    }}>
      <div style={{ maxWidth: "1060px", margin: "0 auto", padding: "38px 28px 60px" }}>

        <header style={{
          display: "flex", justifyContent: "space-between", alignItems: "flex-end",
          flexWrap: "wrap", gap: "20px", marginBottom: "28px", paddingBottom: "24px",
          borderBottom: "1px solid var(--border)",
        }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "11px" }}>
              <span style={{ position: "relative", width: 34, height: 40, display: "inline-block", flex: "none", animation: "mascotBob 2.8s ease-in-out infinite" }}>
                <span style={{ position: "absolute", left: "50%", top: 1, width: 3, height: 10, background: "var(--blue)", borderRadius: 2, transform: "translateX(-50%)" }} />
                <span style={{ position: "absolute", left: "calc(50% + 1px)", top: 0, width: 12, height: 9, background: "var(--teal)", borderRadius: "0 90% 10% 90%", transformOrigin: "left bottom", animation: "leafSway 3.4s ease-in-out infinite" }} />
                <span style={{ position: "absolute", left: 0, bottom: 0, width: 34, height: 30, background: "linear-gradient(160deg,var(--blue),color-mix(in oklab,var(--teal) 55%,var(--blue)))", borderRadius: "48% 48% 46% 46%", boxShadow: "inset 0 -3px 7px rgba(0,0,0,.14)" }} />
                <span style={{ position: "absolute", left: 9, bottom: 13, width: 6, height: 7, background: "#0d2018", borderRadius: "50%", animation: "mascotBlink 4.2s infinite" }} />
                <span style={{ position: "absolute", left: 19, bottom: 13, width: 6, height: 7, background: "#0d2018", borderRadius: "50%", animation: "mascotBlink 4.2s infinite" }} />
                <span style={{ position: "absolute", left: 13, bottom: 8, width: 8, height: 4, borderBottom: "2px solid #0d2018", borderRadius: "0 0 9px 9px" }} />
              </span>
              <h1 style={{ margin: 0, font: "600 26px 'IBM Plex Sans'", letterSpacing: "-.02em", color: "var(--text)" }}>RiskFlow</h1>
            </div>
            <p style={{ margin: "10px 0 0", font: "400 14px 'IBM Plex Sans'", color: "var(--muted)" }}>
              Real-time payment risk and cost-optimized decisioning
            </p>
          </div>

          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "12px" }}>
            <div className="seg">
              <button className={theme === "light" ? "seg-active" : ""} onClick={() => setTheme("light")}>Light</button>
              <button className={theme === "dark" ? "seg-active" : ""} onClick={() => setTheme("dark")}>Dark</button>
            </div>
            <span style={{
              display: "inline-flex", alignItems: "center", gap: "7px",
              font: "500 11px 'IBM Plex Mono',monospace", letterSpacing: ".08em", textTransform: "uppercase",
              color: "var(--teal)", border: "1px solid color-mix(in oklab,var(--teal) 35%,var(--border))",
              borderRadius: "999px", padding: "6px 11px",
            }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--teal)", animation: "pulseDot 2.2s ease-out infinite" }} />
              Live · Snowflake
            </span>
          </div>
        </header>

        <CostAnalysis />
        <ThresholdSimulator />
        <PipelineHealth />

        <p style={{ margin: "22px 2px 0", font: "400 11px 'IBM Plex Mono',monospace", color: "var(--muted)" }}>
          Live values streamed from a Snowflake warehouse via the RiskFlow API.
        </p>
      </div>
    </div>
  );
}

export default App;
