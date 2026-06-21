import { useEffect, useState } from "react";
import { getPipelineHealth } from "../api/client";

const card: React.CSSProperties = {
  background: "var(--card)", border: "1px solid var(--border)", borderRadius: "var(--radius)",
  padding: "var(--card-pad)", boxShadow: "var(--shadow)",
};
const tile: React.CSSProperties = {
  background: "var(--tile)", border: "1px solid var(--border)", borderRadius: "var(--radius)",
  padding: "var(--tile-pad)",
};
const labelText: React.CSSProperties = {
  font: "500 11px 'IBM Plex Mono',monospace", letterSpacing: ".12em", textTransform: "uppercase",
  color: "var(--muted)", marginBottom: 13,
};

function StatusPill({ value }: { value: string }) {
  const label = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 7,
      background: "color-mix(in oklab,var(--teal) 15%,transparent)", color: "var(--teal)",
      padding: "6px 12px", borderRadius: 999, font: "600 13px 'IBM Plex Mono',monospace",
    }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--teal)" }} />
      {label}
    </span>
  );
}

export default function PipelineHealth() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    getPipelineHealth().then(setHealth);
  }, []);

  if (!health) return <div style={card}>Loading pipeline health...</div>;

  return (
    <section style={card}>
      <h2 style={{ margin: "0 0 22px", font: "600 19px 'IBM Plex Sans'", letterSpacing: "-.01em" }}>Pipeline health</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "var(--gap)" }}>
        <div style={tile}>
          <div style={labelText}>Lakehouse</div>
          <StatusPill value={health.lakehouse_status} />
        </div>
        <div style={tile}>
          <div style={labelText}>Snowflake</div>
          <StatusPill value={health.snowflake_status} />
        </div>
        <div style={tile}>
          <div style={labelText}>Drift check</div>
          <StatusPill value={health.last_drift_check} />
        </div>
        <div style={tile}>
          <div style={labelText}>Model version</div>
          <div style={{ font: "500 20px 'IBM Plex Mono',monospace", color: "var(--text)" }}>{health.model_version}</div>
        </div>
        <div style={tile}>
          <div style={labelText}>Latency p50</div>
          <div style={{ font: "500 20px 'IBM Plex Mono',monospace", color: "var(--text)" }}>
            {health.api_latency_ms_p50}<span style={{ fontSize: 13, color: "var(--muted)", marginLeft: 1 }}>ms</span>
          </div>
        </div>
        <div style={tile}>
          <div style={labelText}>Latency p95</div>
          <div style={{ font: "500 20px 'IBM Plex Mono',monospace", color: "var(--text)" }}>
            {health.api_latency_ms_p95}<span style={{ fontSize: 13, color: "var(--muted)", marginLeft: 1 }}>ms</span>
          </div>
        </div>
      </div>
    </section>
  );
}
