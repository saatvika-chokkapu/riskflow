import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getCostAnalysis } from "../api/client";

export default function CostAnalysis() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCostAnalysis().then((d) => {
      setData(d);
      setLoading(false);
    });
  }, []);

  if (loading) return <p>Loading cost analysis...</p>;

  const totalRiskflow = data.reduce((sum, d) => sum + d.riskflow_total_cost, 0);
  const totalNaive = data.reduce((sum, d) => sum + d.naive_total_cost, 0);
  const savings = totalNaive - totalRiskflow;

  return (
    <div style={{ marginBottom: "3rem" }}>
      <h2>Cost Analysis: RiskFlow vs Naive Threshold</h2>
      <p>
        Total RiskFlow cost: <strong>${totalRiskflow.toLocaleString(undefined, { maximumFractionDigits: 0 })}</strong> |
        Total Naive cost: <strong>${totalNaive.toLocaleString(undefined, { maximumFractionDigits: 0 })}</strong> |
        Savings: <strong style={{ color: savings > 0 ? "green" : "red" }}>
          ${savings.toLocaleString(undefined, { maximumFractionDigits: 0 })}
        </strong>
      </p>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="txn_date" tick={{ fontSize: 10 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="riskflow_total_cost" stroke="#2563eb" name="RiskFlow Cost" dot={false} />
          <Line type="monotone" dataKey="naive_total_cost" stroke="#dc2626" name="Naive Cost" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
