import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getCostAnalysis } from "../api/client";

const card: React.CSSProperties = {
  background: "var(--bg-card)",
  border: "1px solid var(--border-color)",
  borderRadius: "var(--radius-lg)",
  padding: "1.5rem",
  marginBottom: "1.5rem",
};

const metricBox: React.CSSProperties = {
  background: "var(--bg-secondary)",
  borderRadius: "var(--radius-md)",
  padding: "1rem",
  flex: 1,
};

export default function CostAnalysis() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCostAnalysis().then((d) => {
      setData(d);
      setLoading(false);
    });
  }, []);

  if (loading) return <div style={card}>Loading cost analysis...</div>;

  const totalRiskflow = data.reduce((sum, d) => sum + d.riskflow_total_cost, 0);
  const totalNaive = data.reduce((sum, d) => sum + d.naive_total_cost, 0);
  const savings = totalNaive - totalRiskflow;
  const fmt = (n: number) => `$${Math.round(n).toLocaleString()}`;

  return (
    <div style={card}>
      <h2 style={{ margin: "0 0 0.25rem", fontSize: "1.125rem", fontWeight: 600 }}>Cost analysis</h2>
      <p style={{ margin: "0 0 1.25rem", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
        RiskFlow's cost-aware decisioning vs. a naive fixed-threshold baseline
      </p>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <div style={metricBox}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.25rem" }}>RiskFlow cost</div>
          <div style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--accent-blue)" }}>{fmt(totalRiskflow)}</div>
        </div>
        <div style={metricBox}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.25rem" }}>Naive cost</div>
          <div style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--accent-red)" }}>{fmt(totalNaive)}</div>
        </div>
        <div style={metricBox}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "0.25rem" }}>Savings</div>
          <div style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--accent-green)" }}>{fmt(savings)}</div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
          <XAxis dataKey="txn_date" tick={{ fontSize: 10, fill: "var(--text-tertiary)" }} />
          <YAxis tick={{ fontSize: 10, fill: "var(--text-tertiary)" }} />
          <Tooltip contentStyle={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "8px" }} />
          <Legend />
          <Line type="monotone" dataKey="riskflow_total_cost" stroke="#4d8af0" name="RiskFlow" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="naive_total_cost" stroke="#ef5b5b" name="Naive" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
