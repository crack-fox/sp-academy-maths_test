import React from "react";

const STATUS_STYLES = {
  onTrack: { label: "On Track", color: "#166534", bg: "#dcfce7" },
  developing: { label: "Developing", color: "#92400e", bg: "#fef3c7" },
  needsSupport: { label: "Needs Support", color: "#991b1b", bg: "#fee2e2" }
};

const clamp = (value, min = 0, max = 100) => Math.max(min, Math.min(max, value));

function Header({ studentName, yearLevel, reportDate }) {
  return (
    <header style={styles.header}>
      <div>
        <h1 style={styles.title}>Student Progress Report</h1>
        <p style={styles.subtitle}>Parent dashboard view</p>
      </div>
      <div style={styles.headerMeta}>
        <p style={styles.metaLine}><strong>Student:</strong> {studentName}</p>
        <p style={styles.metaLine}><strong>Year:</strong> {yearLevel}</p>
        <p style={styles.metaLine}><strong>Report date:</strong> {reportDate}</p>
      </div>
    </header>
  );
}

function ProgressOverview({ strandProgress }) {
  return (
    <section style={styles.card}>
      <h2 style={styles.sectionTitle}>Progress Overview</h2>
      <div style={styles.stack}>
        {strandProgress.map((strand) => {
          const progress = clamp(strand.progress);
          return (
            <div key={strand.name}>
              <div style={styles.rowBetween}>
                <span style={styles.rowLabel}>{strand.name}</span>
                <span style={styles.rowValue}>{progress}%</span>
              </div>
              <div style={styles.track}>
                <div style={{ ...styles.fill, width: `${progress}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function GapAlert({ gapSummary }) {
  return (
    <section style={{ ...styles.card, ...styles.alertCard }}>
      <h2 style={styles.sectionTitle}>Gap Alert</h2>
      <p style={styles.alertText}>{gapSummary.summary}</p>
      <ul style={styles.ul}>
        {gapSummary.majorGaps.map((gap) => (
          <li key={gap}>{gap}</li>
        ))}
      </ul>
    </section>
  );
}

function SkillBreakdown({ skills }) {
  return (
    <section style={styles.card}>
      <h2 style={styles.sectionTitle}>Skill Breakdown</h2>
      <div style={styles.stack}>
        {skills.map((skill) => {
          const statusStyle = STATUS_STYLES[skill.status] || STATUS_STYLES.developing;
          return (
            <div key={skill.name} style={styles.skillRow}>
              <div>
                <p style={styles.skillName}>{skill.name}</p>
                <p style={styles.skillNote}>Mastery: {clamp(skill.mastery)}%</p>
              </div>
              <span
                style={{
                  ...styles.badge,
                  backgroundColor: statusStyle.bg,
                  color: statusStyle.color
                }}
              >
                {statusStyle.label}
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function ActionPlan({ recommendedPlan }) {
  return (
    <section style={styles.card}>
      <h2 style={styles.sectionTitle}>Recommended Action Plan</h2>
      <ol style={styles.ol}>
        {recommendedPlan.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
    </section>
  );
}

function WorksheetPreview({ worksheetPreview }) {
  return (
    <section style={styles.card}>
      <h2 style={styles.sectionTitle}>Worksheet Preview</h2>
      <p style={styles.metaLine}><strong>Title:</strong> {worksheetPreview.title}</p>
      <p style={styles.metaLine}><strong>Focus:</strong> {worksheetPreview.focus}</p>
      <ul style={styles.ul}>
        {worksheetPreview.sampleQuestions.map((question) => (
          <li key={question}>{question}</li>
        ))}
      </ul>
    </section>
  );
}

function CTASection({ ctaLabel, onCtaClick }) {
  return (
    <section style={styles.card}>
      <button style={styles.ctaButton} onClick={onCtaClick}>
        {ctaLabel}
      </button>
    </section>
  );
}

export function ParentProgressDashboard({ report }) {
  const isMobile =
    typeof window !== "undefined" ? window.matchMedia("(max-width: 768px)").matches : false;

  return (
    <main style={styles.page}>
      <div style={styles.container}>
        <Header
          studentName={report.studentName}
          yearLevel={report.yearLevel}
          reportDate={report.reportDate}
        />

        <div
          style={{
            ...styles.grid,
            gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr"
          }}
        >
          <ProgressOverview strandProgress={report.strandProgress} />
          <GapAlert gapSummary={report.gapSummary} />
          <SkillBreakdown skills={report.skillBreakdown} />
          <ActionPlan recommendedPlan={report.actionPlan} />
          <WorksheetPreview worksheetPreview={report.worksheetPreview} />
          <CTASection
            ctaLabel={report.cta.label}
            onCtaClick={report.cta.onClick}
          />
        </div>
      </div>
    </main>
  );
}

export const mockReport = {
  studentName: "Maya Johnson",
  yearLevel: "Year 4",
  reportDate: "April 7, 2026",
  strandProgress: [
    { name: "Number & Algebra", progress: 78 },
    { name: "Measurement & Geometry", progress: 62 },
    { name: "Statistics & Probability", progress: 71 }
  ],
  gapSummary: {
    summary:
      "Maya is progressing well overall, with the largest learning gaps in fractions and multi-step problem solving.",
    majorGaps: [
      "Equivalent fractions and ordering fractions",
      "Selecting operations in two-step word problems",
      "Converting perimeter understanding into area strategy"
    ]
  },
  skillBreakdown: [
    { name: "Place value to 10,000", mastery: 86, status: "onTrack" },
    { name: "Equivalent fractions", mastery: 49, status: "needsSupport" },
    { name: "Perimeter vs area", mastery: 57, status: "developing" },
    { name: "Interpreting bar graphs", mastery: 82, status: "onTrack" }
  ],
  actionPlan: [
    "Complete two short fraction fluency sessions each week (10–12 minutes each).",
    "Use visual models (fraction strips/circles) before symbolic fraction comparison.",
    "Practice one multi-step word problem nightly and explain the chosen operations aloud.",
    "Review teacher feedback every Friday and set one micro-goal for the following week."
  ],
  worksheetPreview: {
    title: "Fractions Foundations Pack",
    focus: "Equivalent fractions, comparison, and visual reasoning",
    sampleQuestions: [
      "Circle all fractions equivalent to 3/4: 6/8, 9/12, 12/18, 15/20.",
      "Order these fractions from least to greatest: 2/3, 5/6, 3/4.",
      "Shade a model to show 4/8 and explain why it equals 1/2."
    ]
  },
  cta: {
    label: "Unlock Maya's Personalized Worksheet Plan",
    onClick: () => alert("CTA clicked: proceed to worksheet checkout")
  }
};

export function ExampleUsage() {
  return <ParentProgressDashboard report={mockReport} />;
}

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#f8fafc",
    padding: "20px"
  },
  container: {
    maxWidth: "1040px",
    margin: "0 auto",
    display: "flex",
    flexDirection: "column",
    gap: "16px"
  },
  header: {
    backgroundColor: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "16px",
    display: "flex",
    justifyContent: "space-between",
    gap: "16px",
    flexWrap: "wrap"
  },
  headerMeta: {
    minWidth: "220px"
  },
  title: {
    margin: 0,
    fontSize: "1.4rem",
    color: "#0f172a"
  },
  subtitle: {
    margin: "4px 0 0 0",
    color: "#475569"
  },
  metaLine: {
    margin: "4px 0",
    color: "#334155"
  },
  grid: {
    display: "grid",
    gap: "16px"
  },
  card: {
    backgroundColor: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "16px"
  },
  alertCard: {
    border: "1px solid #fecaca",
    backgroundColor: "#fff7ed"
  },
  sectionTitle: {
    margin: "0 0 12px 0",
    color: "#0f172a",
    fontSize: "1rem"
  },
  stack: {
    display: "flex",
    flexDirection: "column",
    gap: "12px"
  },
  rowBetween: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: "4px"
  },
  rowLabel: {
    color: "#1e293b",
    fontWeight: 500
  },
  rowValue: {
    color: "#334155",
    fontWeight: 600
  },
  track: {
    width: "100%",
    height: "10px",
    backgroundColor: "#e2e8f0",
    borderRadius: "9999px",
    overflow: "hidden"
  },
  fill: {
    height: "100%",
    backgroundColor: "#2563eb",
    borderRadius: "9999px"
  },
  alertText: {
    margin: "0 0 8px 0",
    color: "#7f1d1d"
  },
  ul: {
    margin: "0 0 0 18px",
    color: "#334155",
    padding: 0
  },
  ol: {
    margin: "0 0 0 18px",
    color: "#334155",
    padding: 0
  },
  skillRow: {
    display: "flex",
    justifyContent: "space-between",
    gap: "12px",
    alignItems: "flex-start",
    borderBottom: "1px solid #f1f5f9",
    paddingBottom: "10px"
  },
  skillName: {
    margin: 0,
    color: "#0f172a",
    fontWeight: 600
  },
  skillNote: {
    margin: "4px 0 0 0",
    color: "#64748b",
    fontSize: "0.9rem"
  },
  badge: {
    fontSize: "0.75rem",
    fontWeight: 700,
    borderRadius: "9999px",
    padding: "4px 10px",
    whiteSpace: "nowrap"
  },
  ctaButton: {
    width: "100%",
    border: "none",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    padding: "12px 14px",
    borderRadius: "10px",
    fontSize: "1rem",
    fontWeight: 700,
    cursor: "pointer"
  }
};
