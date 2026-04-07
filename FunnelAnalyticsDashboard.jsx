import React from "react";

function MetricCard({ label, value }) {
  return (
    <div style={styles.metricCard}>
      <p style={styles.metricLabel}>{label}</p>
      <p style={styles.metricValue}>{value}</p>
    </div>
  );
}

export function FunnelAnalyticsDashboard({ dashboard }) {
  const funnel = dashboard.summary.funnel_metrics;
  const dropoff = dashboard.summary.dropoff;

  return (
    <main style={styles.page}>
      <section style={styles.panel}>
        <h1 style={styles.title}>Funnel Analytics Dashboard</h1>
        <p style={styles.subtitle}>Daily view: {dashboard.summary.date}</p>

        <div style={styles.metricsGrid}>
          <MetricCard label="Sessions" value={funnel.totals.sessions} />
          <MetricCard label="Start Rate" value={`${(funnel.start_rate * 100).toFixed(1)}%`} />
          <MetricCard label="Completion Rate" value={`${(funnel.completion_rate * 100).toFixed(1)}%`} />
          <MetricCard label="Upgrade Rate" value={`${(funnel.upgrade_rate * 100).toFixed(1)}%`} />
          <MetricCard label="Conversion Rate" value={`${(funnel.conversion_rate * 100).toFixed(1)}%`} />
        </div>
      </section>

      <section style={styles.panel}>
        <h2 style={styles.sectionTitle}>Drop-off Insights</h2>
        <p style={styles.bodyText}>
          Largest drop-off: <strong>{dropoff.from_stage}</strong> → <strong>{dropoff.to_stage}</strong> ({(dropoff.drop_rate * 100).toFixed(1)}%)
        </p>
        <p style={styles.bodyText}>{dashboard.summary.biggest_issue}</p>
      </section>

      <section style={styles.panel}>
        <h2 style={styles.sectionTitle}>Recommended Action</h2>
        <p style={styles.bodyText}>{dashboard.summary.recommended_action}</p>
      </section>
    </main>
  );
}

export const sampleDashboardData = {
  summary: {
    date: "2026-04-07",
    funnel_metrics: {
      totals: { sessions: 3, started: 3, completed: 2, upgraded: 2, converted: 1 },
      stage_counts: { start: 3, complete: 2, upgrade: 2, convert: 1 },
      start_rate: 1,
      completion_rate: 0.6667,
      upgrade_rate: 1,
      conversion_rate: 0.3333
    },
    deltas_vs_previous_day: {
      start_rate: 0,
      completion_rate: 0.1667,
      upgrade_rate: 1,
      conversion_rate: 0.3333
    },
    biggest_issue: "Largest drop-off occurs between start and complete (33.33%).",
    recommended_action: "Improve task completion: add progress nudges and simplify difficult question flows.",
    dropoff: {
      from_stage: "start",
      to_stage: "complete",
      drop_count: 1,
      drop_rate: 0.3333
    }
  }
};

export function FunnelDashboardExample() {
  return <FunnelAnalyticsDashboard dashboard={sampleDashboardData} />;
}

const styles = {
  page: {
    background: "#f8fafc",
    minHeight: "100vh",
    padding: "24px",
    display: "grid",
    gap: "16px"
  },
  panel: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "16px"
  },
  title: { margin: 0, color: "#0f172a" },
  subtitle: { marginTop: "8px", color: "#475569" },
  sectionTitle: { margin: 0, marginBottom: "8px", color: "#0f172a" },
  bodyText: { margin: "6px 0", color: "#334155" },
  metricsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
    gap: "10px",
    marginTop: "12px"
  },
  metricCard: {
    border: "1px solid #cbd5e1",
    borderRadius: "10px",
    padding: "12px",
    background: "#f8fafc"
  },
  metricLabel: { margin: 0, color: "#475569", fontSize: "0.85rem" },
  metricValue: { margin: "4px 0 0 0", fontWeight: 700, color: "#0f172a", fontSize: "1.1rem" }
};
