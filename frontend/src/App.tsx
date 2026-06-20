import CostAnalysis from "./components/CostAnalysis";
import ThresholdSimulator from "./components/ThresholdSimulator";
import PipelineHealth from "./components/PipelineHealth";

function App() {
  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>RiskFlow Dashboard</h1>
      <CostAnalysis />
      <ThresholdSimulator />
      <PipelineHealth />
    </div>
  );
}

export default App;
