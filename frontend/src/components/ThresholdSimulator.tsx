import { useEffect, useState } from "react";
import { getThresholdSimulation } from "../api/client";

const card: React.CSSProperties = {
  background: "var(--bg-card)",
  border: "1px solid var(--border-color)",
  borderRadius: "var(--radius-lg)",
  padding: "1.5rem",
  marginBottom: "1.5rem",
};

const row: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  padding: "0.75rem 0",
  borderBottom: "1px solid var(--border-color)",
};

export default function ThresholdSimulator() {
  const [threshold, setThreshold] = useState(0.5);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    getThresholdSimulation(threshold).then(setResult);
  }, [threshold]);

  const fmt = (n: number) => `$${Math.round(n).toLocaleString()}`;

  return (
    <div style={card}>
      <h2 style={{ margin: "0 0 0.25rem", fontSize: "1.125rem", fontWeight: 600 }}>Threshold simulator</h2>
      <p style={{ margin: "0 0 1.25rem", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
        See how a fixed fraud-probability threshold would have performed historically
      </p>
      <input
        type="range"
        min="0.05"
        max="0.95"
        step="0.05"
        value={threshold}
        onChange={(e) => setThreshold(parseFloat(e.target.value))}
        style={{ width: "100%" }}
      />
      <p style={{ textAlign: "center", margin: "0.75rem 0 1.25rem", color: "var(--text-secondary)" }}>
        Threshold: <strong style={{ color: "var(--text-primary)" }}>{threshold.toFixed(2)}</strong>
      </p>
      {result && (
        <div>
          <div style={row}>
            <span style={{ color: "var(--text-secondary)" }}>Fraud caught (count)</span>
            <strong>{result.fraud_caught_count}</strong>
          </div>
          <div style={row}>
            <span style={{ color: "var(--text-secondary)" }}>Fraud caught (value)</span>
            <strong style={{ color: "var(--accent-green)" }}>{fmt(result.fraud_caught_value)}</strong>
          </div>
          <div style={row}>
            <span style={{ color: "var(--text-secondary)" }}>Fraud missed (value)</span>
            <strong style={{ color: "var(--accent-red)" }}>{fmt(result.fraud_missed_value)}</strong>
          </div>
          <div style={{ ...row, borderBottom: "none" }}>
            <span style={{ color: "var(--text-secondary)" }}>False declines</span>
            <strong>{result.false_declines}</strong>
          </div>
        </div>
      )}
    </div>
  );
}
