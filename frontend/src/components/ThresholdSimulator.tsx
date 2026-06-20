import { useEffect, useState } from "react";
import { getThresholdSimulation } from "../api/client";

export default function ThresholdSimulator() {
  const [threshold, setThreshold] = useState(0.5);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    getThresholdSimulation(threshold).then(setResult);
  }, [threshold]);

  return (
    <div style={{ marginBottom: "3rem" }}>
      <h2>Threshold Simulator</h2>
      <p>Move the slider to see how a fixed fraud-probability threshold would have performed historically.</p>
      <input
        type="range"
        min="0.05"
        max="0.95"
        step="0.05"
        value={threshold}
        onChange={(e) => setThreshold(parseFloat(e.target.value))}
        style={{ width: "100%" }}
      />
      <p>Threshold: <strong>{threshold.toFixed(2)}</strong></p>
      {result && (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
          <tbody>
            <tr><td>Fraud caught (count)</td><td><strong>{result.fraud_caught_count}</strong></td></tr>
            <tr><td>Fraud caught (value)</td><td><strong>${result.fraud_caught_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}</strong></td></tr>
            <tr><td>Fraud missed (value)</td><td><strong style={{ color: "red" }}>${result.fraud_missed_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}</strong></td></tr>
            <tr><td>False declines</td><td><strong>{result.false_declines}</strong></td></tr>
          </tbody>
        </table>
      )}
    </div>
  );
}
