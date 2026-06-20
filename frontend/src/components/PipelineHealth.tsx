import { useEffect, useState } from "react";
import { getPipelineHealth } from "../api/client";

export default function PipelineHealth() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    getPipelineHealth().then(setHealth);
  }, []);

  if (!health) return <p>Loading pipeline health...</p>;

  return (
    <div style={{ marginBottom: "3rem" }}>
      <h2>Pipeline Health</h2>
      <ul>
        <li>Lakehouse: <strong>{health.lakehouse_status}</strong></li>
        <li>Snowflake: <strong>{health.snowflake_status}</strong></li>
        <li>Last drift check: <strong>{health.last_drift_check}</strong></li>
        <li>Model version: <strong>{health.model_version}</strong></li>
        <li>API latency p50: <strong>{health.api_latency_ms_p50}ms</strong></li>
        <li>API latency p95: <strong>{health.api_latency_ms_p95}ms</strong></li>
      </ul>
    </div>
  );
}
