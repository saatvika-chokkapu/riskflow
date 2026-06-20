import CostAnalysis from "./components/CostAnalysis";
import ThresholdSimulator from "./components/ThresholdSimulator";
import PipelineHealth from "./components/PipelineHealth";

function App() {
  return (
    <div style={{ minHeight: "100vh" }}>
      <header style={{
        borderBottom: "1px solid var(--border-color)",
        padding: "1.5rem 2rem",
        background: "var(--bg-secondary)",
      }}>
        <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 600 }}>RiskFlow</h1>
        <p style={{ margin: "0.25rem 0 0", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
          Real-time payment risk and cost-optimized decisioning
        </p>
      </header>
      <main style={{ maxWidth: "1000px", margin: "0 auto", padding: "2rem 1.5rem" }}>
        <CostAnalysis />
        <ThresholdSimulator />
        <PipelineHealth />
      </main>
    </div>
  );
}

export default App;
