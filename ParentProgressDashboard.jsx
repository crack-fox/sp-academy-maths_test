import React from "react";

function HeroSection({ onStartAssessment }) {
  return (
    <section id="hero" className="section hero">
      <div className="heroContent">
        <p className="eyebrow">Primary Maths Confidence</p>
        <h1>Find out if your child is falling behind in maths — in 2 minutes</h1>
        <p>
          Get clear answers fast with a parent-friendly diagnostic that highlights exactly
          where your child needs support before small gaps become major setbacks.
        </p>
        <button className="ctaButton" onClick={onStartAssessment}>
          Start Free Assessment
        </button>
      </div>
    </section>
  );
}

function ProblemSection() {
  return (
    <section id="problem" className="section">
      <h2>Small maths gaps don&apos;t stay small</h2>
      <p>
        In primary school, each new topic builds on earlier skills. When a child misses one core
        concept, the next lesson becomes harder, confidence drops, and progress slows.
      </p>
      <p>
        A weak foundation in multiplication today can become struggles with fractions,
        word problems, and algebra tomorrow. Early clarity gives you the power to act now.
      </p>
    </section>
  );
}

function SolutionSection() {
  const steps = [
    {
      title: "1) Assessment",
      description: "Your child completes a short, adaptive maths check in about 2 minutes."
    },
    {
      title: "2) Report",
      description: "You receive a simple diagnostic report showing strengths and urgent learning gaps."
    },
    {
      title: "3) Personalised plan",
      description: "Get a week-by-week action plan tailored to your child&apos;s exact needs."
    }
  ];

  return (
    <section id="solution" className="section">
      <h2>How it works</h2>
      <div className="threeColGrid">
        {steps.map((step) => (
          <article key={step.title} className="card">
            <h3>{step.title}</h3>
            <p>{step.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function ExampleReportSection() {
  return (
    <section id="report" className="section highlight">
      <h2>Example parent insight</h2>
      <div className="reportBox">
        <p className="reportLabel">Sample finding</p>
        <p className="reportInsight">1.5 years behind in multiplication</p>
        <p>
          We translate assessment results into plain English so you instantly understand the academic
          risk level and what to do next.
        </p>
      </div>
    </section>
  );
}

function ProductPreviewSection() {
  return (
    <section id="preview" className="section">
      <h2>What your child gets after the report</h2>
      <div className="twoColGrid">
        <article className="card">
          <h3>Targeted worksheets</h3>
          <p>
            Practice sheets focus on the exact skills your child is missing, so every minute of study
            moves them forward.
          </p>
        </article>
        <article className="card">
          <h3>Adaptive learning path</h3>
          <p>
            As your child improves, the platform updates difficulty automatically to keep challenge high
            and frustration low.
          </p>
        </article>
      </div>
    </section>
  );
}

function PricingSection({ onStartAssessment }) {
  return (
    <section id="pricing" className="section">
      <h2>Simple pricing for every family</h2>
      <div className="twoColGrid">
        <article className="card pricingCard">
          <h3>Free</h3>
          <p className="price">$0</p>
          <ul>
            <li>2-minute diagnostic assessment</li>
            <li>Gap snapshot for key maths strands</li>
            <li>One sample worksheet</li>
          </ul>
          <button className="secondaryButton" onClick={onStartAssessment}>
            Start Free Assessment
          </button>
        </article>
        <article className="card pricingCard premium">
          <h3>Premium</h3>
          <p className="price">$19/month</p>
          <ul>
            <li>Full personalised report</li>
            <li>Weekly adaptive worksheets</li>
            <li>Progress tracking and parent guidance</li>
          </ul>
          <button className="ctaButton" onClick={onStartAssessment}>
            Start Free Assessment
          </button>
        </article>
      </div>
    </section>
  );
}

function FinalCTASection({ onStartAssessment }) {
  return (
    <section id="final-cta" className="section finalCta">
      <h2>Every week you wait makes catching up harder.</h2>
      <p>
        Start the free assessment today and get immediate clarity on your child&apos;s maths progress
        before the next school term compounds the gap.
      </p>
      <button className="ctaButton" onClick={onStartAssessment}>
        Start Free Assessment
      </button>
    </section>
  );
}

export function MathsLandingPage() {
  const startAssessment = () => {
    if (typeof window !== "undefined") {
      const pricing = document.getElementById("pricing");
      if (pricing) {
        pricing.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    // Placeholder functional hook for future checkout or quiz routing.
    console.log("startAssessment() triggered");
  };

  return (
    <main className="pageRoot">
      <style>{`
        * { box-sizing: border-box; }
        html, body, #root { margin: 0; padding: 0; }
        .pageRoot {
          font-family: Arial, sans-serif;
          color: #0f172a;
          background: #f8fafc;
          scroll-behavior: smooth;
          line-height: 1.5;
        }
        .section {
          max-width: 980px;
          margin: 0 auto;
          padding: 64px 20px;
        }
        .hero {
          padding-top: 80px;
          text-align: center;
        }
        .heroContent {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 16px;
          padding: 48px 24px;
        }
        h1, h2, h3 { margin-top: 0; }
        h1 { font-size: 2rem; margin-bottom: 16px; }
        h2 { font-size: 1.65rem; margin-bottom: 12px; }
        h3 { font-size: 1.1rem; margin-bottom: 8px; }
        p { margin: 0 0 12px; }
        .eyebrow {
          text-transform: uppercase;
          font-size: 0.8rem;
          letter-spacing: 0.08em;
          color: #2563eb;
          font-weight: 700;
        }
        .threeColGrid, .twoColGrid {
          display: grid;
          gap: 16px;
        }
        .threeColGrid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .twoColGrid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .card {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          padding: 20px;
        }
        .highlight .reportBox {
          background: #fff7ed;
          border: 1px solid #fed7aa;
          border-radius: 12px;
          padding: 20px;
        }
        .reportLabel {
          font-size: 0.85rem;
          color: #9a3412;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          font-weight: 700;
          margin-bottom: 8px;
        }
        .reportInsight {
          font-size: 1.5rem;
          font-weight: 700;
          color: #7c2d12;
          margin-bottom: 10px;
        }
        ul { margin: 0 0 18px 18px; padding: 0; }
        .price {
          font-size: 1.8rem;
          font-weight: 700;
          margin-bottom: 10px;
        }
        .premium {
          border-color: #93c5fd;
          background: #eff6ff;
        }
        .ctaButton, .secondaryButton {
          border: none;
          border-radius: 10px;
          padding: 12px 18px;
          font-size: 1rem;
          font-weight: 700;
          cursor: pointer;
          width: 100%;
          transition: opacity 0.2s ease;
        }
        .ctaButton { background: #2563eb; color: #ffffff; }
        .secondaryButton { background: #e2e8f0; color: #0f172a; }
        .ctaButton:hover, .secondaryButton:hover { opacity: 0.9; }
        .finalCta {
          text-align: center;
          padding-bottom: 80px;
        }

        @media (max-width: 768px) {
          .section { padding: 48px 16px; }
          h1 { font-size: 1.6rem; }
          h2 { font-size: 1.35rem; }
          .threeColGrid, .twoColGrid { grid-template-columns: 1fr; }
          .heroContent { padding: 32px 18px; }
        }
      `}</style>

      <HeroSection onStartAssessment={startAssessment} />
      <ProblemSection />
      <SolutionSection />
      <ExampleReportSection />
      <ProductPreviewSection />
      <PricingSection onStartAssessment={startAssessment} />
      <FinalCTASection onStartAssessment={startAssessment} />
    </main>
  );
}

export default MathsLandingPage;
