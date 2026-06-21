import { useEffect, useState } from "react";
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { getCostAnalysis } from "../api/client";

const card: React.CSSProperties = {
  background: "var(--card)", border: "1px solid var(--border)", borderRadius: "var(--radius)",
  padding: "var(--card-pad)", boxShadow: "var(--shadow)", marginBottom: "18px",
};
const tile: React.CSSProperties = {
  background: "var(--tile)", border: "1px solid var(--border)", borderRadius: "var(--radius)",
  padding: "var(--tile-pad)",
};
const tileLabel = (color: string): React.CSSProperties => ({
  display: "flex", alignItems: "center", gap: 8, marginBottom: 16,
});
const dot = (color: string): React.CSSProperties => ({ width: 7, height: 7, borderRadius: 2, background: color });
const labelText: React.CSSProperties = {
  font: "500 11px 'IBM Plex Mono',monospace", letterSpacing: ".14em", textTransform: "uppercase", color: "var(--muted)",
};
const bigNumber = (color: string): React.CSSProperties => ({
  font: "500 30px/1 'IBM Plex Mono',monospace", color, fontVariantNumeric: "tabular-nums", letterSpacing: "-.01em",
});

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload || !payload.length) return null;
  const rf = payload.find((p: any) => p.dataKey === "riskflow_total_cost");
  const naive = payload.find((p: any) => p.dataKey === "naive_total_cost");
  return (
    <div style={{
      background: "var(--card)", border: "1px solid var(--border)", borderRadius: 8,
      padding: "9px 12px", boxShadow: "0 6px 20px var(--shadow-color)", minWidth: 128,
    }}>
      <div style={{ font: "500 10px 'IBM Plex Mono',monospace", color: "var(--muted)", letterSpacing: ".1em", textTransform: "uppercase", marginBottom: 7 }}>
        {label}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 14, marginBottom: 4 }}>
        <span style={{ font: "400 11px 'IBM Plex Sans'", color: "var(--muted)" }}>RiskFlow</span>
        <span style={{ font: "600 12px 'IBM Plex Mono',monospace", color: "var(--blue)" }}>${Math.round(rf?.value || 0).toLocaleString()}</span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 14 }}>
        <span style={{ font: "400 11px 'IBM Plex Sans'", color: "var(--muted)" }}>Naive</span>
        <span style={{ font: "600 12px 'IBM Plex Mono',monospace", color: "var(--violet)" }}>${Math.round(naive?.value || 0).toLocaleString()}</span>
      </div>
    </div>
  );
}

export default function CostAnalysis() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCostAnalysis().then((d) => { setData(d); setLoading(false); });
  }, []);

  if (loading) return <div style={card}>Loading cost analysis...</div>;

  const totalRiskflow = data.reduce((s, d) => s + d.riskflow_total_cost, 0);
  const totalNaive = data.reduce((s, d) => s + d.naive_total_cost, 0);
  const savings = totalNaive - totalRiskflow;
  const savingsPct = ((savings / totalNaive) * 100).toFixed(1);
  const fmt = (n: number) => `$${Math.round(n).toLocaleString()}`;

  return (
    <section style={card}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, font: "600 19px 'IBM Plex Sans'", letterSpacing: "-.01em" }}>Cost analysis</h2>
          <p style={{ margin: "7px 0 0", font: "400 13px 'IBM Plex Sans'", color: "var(--muted)", maxWidth: 520 }}>
            RiskFlow's cost-aware decisioning vs. a naive fixed-threshold baseline.
          </p>
        </div>
        <span style={{ font: "500 11px 'IBM Plex Mono',monospace", color: "var(--muted)", letterSpacing: ".08em", textTransform: "uppercase", border: "1px solid var(--border)", borderRadius: 999, padding: "6px 12px", whiteSpace: "nowrap" }}>
          {data.length} days
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "var(--gap)" }}>
        <div style={tile}>
          <div style={tileLabel("var(--blue)")}><span style={dot("var(--blue)")} /><span style={labelText}>RiskFlow cost</span></div>
          <div style={bigNumber("var(--blue)")}>{fmt(totalRiskflow)}</div>
          <div style={{ marginTop: 9, font: "400 12px 'IBM Plex Sans'", color: "var(--muted)" }}>cost-aware decisioning</div>
        </div>
        <div style={tile}>
          <div style={tileLabel("var(--violet)")}><span style={dot("var(--violet)")} /><span style={labelText}>Naive cost</span></div>
          <div style={bigNumber("var(--violet)")}>{fmt(totalNaive)}</div>
          <div style={{ marginTop: 9, font: "400 12px 'IBM Plex Sans'", color: "var(--muted)" }}>fixed 0.50 threshold</div>
        </div>
        <div style={tile}>
          <div style={tileLabel("var(--teal)")}><span style={dot("var(--teal)")} /><span style={labelText}>Savings</span></div>
          <div style={{ font: "600 30px/1 'IBM Plex Mono',monospace", color: "var(--teal)", fontVariantNumeric: "tabular-nums" }}>{fmt(savings)}</div>
          <div style={{ marginTop: 11, display: "inline-flex", alignItems: "center", gap: 5, background: "color-mix(in oklab,var(--teal) 16%,transparent)", color: "var(--teal)", padding: "4px 9px", borderRadius: 999, font: "600 11px 'IBM Plex Mono',monospace" }}>
            <span>↓</span>{savingsPct}% lower cost
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <ComposedChart data={data} margin={{ top: 20, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="rfFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--blue)" stopOpacity={0.42} />
              <stop offset="100%" stopColor="var(--blue)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--grid)" strokeDasharray="2 5" vertical={false} />
          <XAxis dataKey="txn_date" tick={{ fontSize: 10, fill: "var(--muted)" }} />
          <YAxis tick={{ fontSize: 10, fill: "var(--muted)" }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: "var(--muted)", opacity: 0.45 }} />
          <Area type="monotone" dataKey="riskflow_total_cost" stroke="none" fill="url(#rfFill)" />
          <Line type="monotone" dataKey="naive_total_cost" stroke="var(--violet)" strokeWidth={2} dot={false} activeDot={{ r: 5, stroke: "var(--card)", strokeWidth: 2 }} />
          <Line type="monotone" dataKey="riskflow_total_cost" stroke="var(--blue)" strokeWidth={2.5} dot={false} activeDot={{ r: 5, stroke: "var(--card)", strokeWidth: 2 }} />
        </ComposedChart>
      </ResponsiveContainer>

      <div style={{ display: "flex", gap: 22, marginTop: 16, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ width: 15, height: 3, borderRadius: 2, background: "var(--blue)" }} />
          <span style={{ font: "400 12px 'IBM Plex Sans'", color: "var(--muted)" }}>RiskFlow — cost-aware</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ width: 15, height: 3, borderRadius: 2, background: "var(--violet)" }} />
          <span style={{ font: "400 12px 'IBM Plex Sans'", color: "var(--muted)" }}>Naive — fixed threshold</span>
        </div>
      </div>
    </section>
  );
}
