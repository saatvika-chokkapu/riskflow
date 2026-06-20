import { useEffect, useState } from "react";
import { getPipelineHealth } from "../api/client";

const card: React.CSSProperties = {
  background: "var(--bg-card)",
  border: "1px solid var(--border-color)",
  borderRadius: "var(--radius-lg)",
  padding: "1.5rem",
};

const pill = (color: string): React.CSSProperties => ({
  display: "inline-block",
  padding: "0.2rem 0.6rem",
  borderRadius: "999px",
  fontSize: "0.75rem",
  fontWeight: 600,
  background: `${color}22`,
  color: color,
});

export default function PipelineHealth() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    getPipelineHealth().then(setHealth);
  }, []);

  if (!health) return <div style={card}>Loading pipeline health...</div>;

  return (
    <div style={card}>
      <h2 style={{ margin: "0 0 1.25rem", fontSize: "1.125rem", fontWeight: 600 }}>Pipeline health</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" }}>
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.4rem" }}>Lakehouse</div>
          <span style={pill("#3ecf8e")}>{health.lakehouse_status}</span>
        </div>
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.4rem" }}>Snowflake</div>
          <span style={pill("#3ecf8e")}>{health.snowflake_status}</span>
        </div>
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.4rem" }}>Drift check</div>
          <span style={pill("#3ecf8e")}>{health.last_drift_check}</span>
        </div>
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.4rem" }}>Model version</div>
          <strong>{health.model_version}</strong>
        </div>
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.4rem" }}>Latency p50</div>
          <strong>{health.api_latency_ms_p50}ms</strong>
        </div>
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.4rem" }}>Latency p95</div>
          <strong>{health.api_latency_ms_p95}ms</strong>
        </div>
      </div>
    </div>
  );
}
