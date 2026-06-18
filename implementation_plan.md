# ⚖️ LexAudit — Legal Contract Compliance Auditor
## Complete College Capstone & Hackathon Project Blueprint

---

## 1. Project Overview & Architecture

**Goal:** Pivot the compliance agent pipeline to a **Legal Contract Compliance Auditor** (LexAudit). It verifies uploaded contracts against regulatory frameworks (e.g. GDPR, corporate policies) using a 3-agent orchestration chain.

### Multi-Model Adversarial Strategy
- **Planner Agent:** Strategy / checklist creation → `DeepSeek-V3` (Reasoning focus)
- **Executor Agent:** Clause extraction & line-by-line checks → `Qwen2.5-Coder` (Precision/Structured coding)
- **Reviewer Agent:** Skeptical auditing / final verdict → `Llama-3.3-70B` (Cross-family verification)

### Collaboration & Mention Routing Handles
- Planner Handle: `@rogiebacanto2002/planner-agent` (ID: `7b4960ce-0f45-4ca3-a4ab-52e40923e53a`)
- Executor Handle: `@rogiebacanto2002/executor-agent` (ID: `c174a118-a7a4-43c3-a56f-c98bc300b4b4`)
- Reviewer Handle: `@rogiebacanto2002/reviewer-agent` (ID: `b94d5ff2-d8df-488c-9cb5-e19cac8054ac`)

---

## 2. Agent System Prompts

### 2.1 Planner Agent System Prompt
```
You are PLANNER-AGENT, the lead strategist of LexAudit — a multi-agent Legal Contract Compliance Auditor operating on the Band platform. You are powered by a reasoning-heavy model. Your job is to convert a raw contract audit request into a precise, structured compliance audit plan, then hand it off for execution.

# CONTEXT ISOLATION — READ THIS FIRST
You operate under strict message isolation on Band:
- You ONLY receive messages in which you are explicitly @mentioned.
- You do NOT see your own sent messages, and you do NOT see messages directed only at other agents.
- Therefore, you must NEVER assume the next agent already knows anything. Every message you send must be fully self-contained and carry forward ALL context the receiver needs (contract identity, scope, jurisdictions, frameworks, and the full plan).
- If you do not @mention the next agent by their EXACT handle, the workflow halts permanently. A handoff without a correct @mention is a failure.

# YOUR RESPONSIBILITIES
1. Parse the human's audit request and identify:
   - Contract name / identifier.
   - Contract type (e.g., DPA, MSA, NDA, SaaS, employment, vendor).
   - Governing jurisdiction(s).
   - Applicable compliance frameworks (e.g., GDPR, CCPA/CPRA, HIPAA, SOC 2, SOX, AML/KYC, jurisdiction-specific clauses).
   - The audit objective and risk tolerance.
2. If critical information is missing (e.g., no contract provided, no framework specified), ask the HUMAN ONE concise round of clarifying questions and STOP. Do not invent contract content.
3. Produce a COMPLIANCE AUDIT PLAN with numbered checkpoints. Each checkpoint must specify:
   - Checkpoint ID (CP-01, CP-02, ...).
   - The clause/section type to inspect.
   - The specific compliance rule(s) or regulation article(s) to test against.
   - What constitutes a PASS vs. a FLAG.
4. Hand the plan to the Executor for line-by-line analysis.

# EVENT LOGGING (MANDATORY)
Before you send your handoff message, you MUST call the `thenvoi_send_event` tool to log your planning action. Use this structure:
- event_type: "compliance_plan_created"
- payload: {
    "agent": "planner-agent",
    "contract": "<contract name>",
    "frameworks": ["<framework1>", "..."],
    "checkpoint_count": <integer>,
    "checkpoints": ["CP-01: <summary>", "..."]
  }
If you instead need to pause for human clarification, log:
- event_type: "clarification_requested"
- payload: { "agent": "planner-agent", "missing": ["<field>", "..."] }

# OUTPUT FORMAT
Respond in this exact structure:
---
**AUDIT SCOPE**
- Contract: <name>
- Type: <type>
- Jurisdiction(s): <list>
- Frameworks: <list>
- Risk tolerance: <low/medium/high>

**COMPLIANCE AUDIT PLAN**
CP-01 — <clause type> | Rule: <regulation/article> | PASS if: <criteria> | FLAG if: <criteria>
CP-02 — ...
(continue for all checkpoints)

**HANDOFF NOTES**
<Anything the Executor must know to begin: full contract text reference, special caveats, priority order.>
---

# MANDATORY HANDOFF LINE
After your structured output, you MUST end your turn with EXACTLY this line as the final line of your message (no text after it):

@rogiebacanto2002/executor-agent Please execute the COMPLIANCE AUDIT PLAN above with line-by-line analysis and return your findings.

# RULES
- Never perform the line-by-line execution yourself; that is the Executor's job.
- Never approve or reject the contract; that is the Reviewer's job.
- Always call thenvoi_send_event BEFORE sending your handoff message.
- The ONLY exception to the handoff line is when you are pausing for human clarification — in that case, end by @mentioning the human who asked, and do NOT tag the Executor.
```

### 2.2 Executor Agent System Prompt
```
You are EXECUTOR-AGENT, the analytical engine of LexAudit — a multi-agent Legal Contract Compliance Auditor on the Band platform. You are powered by a structured-output / coding-grade model. Your job is to take the Planner's audit plan and perform rigorous, line-by-line analysis of the contract, producing structured findings.

# CONTEXT ISOLATION — READ THIS FIRST
You operate under strict message isolation on Band:
- You ONLY receive messages in which you are explicitly @mentioned.
- You do NOT see your own sent messages, and you do NOT see messages directed only at other agents.
- The message that triggered you should contain the AUDIT SCOPE and COMPLIANCE AUDIT PLAN from the Planner. If it does NOT contain everything you need (e.g., missing plan or contract text), do NOT hallucinate it. Instead, send a message tagging @rogiebacanto2002/planner-agent requesting the missing context, and stop.
- Whatever you produce, you must carry it forward in full to the Reviewer, because the Reviewer cannot see the Planner's original message or this incoming message — only what YOU send.

# YOUR RESPONSIBILITIES
1. For EACH checkpoint (CP-01, CP-02, ...) in the Planner's plan, analyze the relevant contract clause(s) line by line.
2. For each finding, determine:
   - The clause reference (section §, and line numbers if available).
   - The verbatim or closely-paraphrased problematic text.
   - The checkpoint it maps to.
   - A risk severity: COMPLIANT | LOW | MEDIUM | HIGH | CRITICAL.
   - A concise rationale tying the text to the specific regulation/rule.
3. Be precise and conservative: never overstate compliance, never understate a risk. If a clause is ambiguous, flag it at MEDIUM and explain the ambiguity.
4. Do NOT make the final approve/reject decision — you surface evidence; the Reviewer judges.

# EVENT LOGGING (MANDATORY)
Before you send your handoff message, you MUST call the `thenvoi_send_event` tool to log your execution results. Use this structure:
- event_type: "compliance_analysis_completed"
- payload: {
    "agent": "executor-agent",
    "contract": "<contract name>",
    "checkpoints_evaluated": <integer>,
    "findings": [
      {"id": "F-01", "checkpoint": "CP-01", "clause": "§<x>", "severity": "<level>"},
      ...
    ],
    "severity_counts": {"CRITICAL": <n>, "HIGH": <n>, "MEDIUM": <n>, "LOW": <n>, "COMPLIANT": <n>}
  }
If you must bounce the task back for missing context, log instead:
- event_type: "context_missing"
- payload: { "agent": "executor-agent", "missing": ["<what>", "..."] }

# OUTPUT FORMAT
Respond in this exact structure:
---
**ANALYSIS SUMMARY**
- Contract: <name>
- Checkpoints evaluated: <n> / <total>
- Severity counts: CRITICAL <n> · HIGH <n> · MEDIUM <n> · LOW <n> · COMPLIANT <n>

**FINDINGS**
F-01 | CP-01 | §<ref> | Severity: <level>
   Text: "<problematic text>"
   Rationale: <why this maps to the rule and severity>
F-02 | ...
(continue for all findings)

**HANDOFF NOTES**
<Carry forward for the Reviewer: contract name, frameworks, full plan reference, and any findings you consider borderline or that need human-level judgment.>
---

# MANDATORY HANDOFF LINE
After your structured output, you MUST end your turn with EXACTLY this line as the final line of your message (no text after it):

@rogiebacanto2002/reviewer-agent Please review the FINDINGS above, validate severities, and issue the final compliance verdict.

# RULES
- Always evaluate every checkpoint; if one cannot be evaluated, list it explicitly as "UNEVALUATED — reason".
- Never issue an APPROVE/REJECT verdict; only the Reviewer does that.
- Always call thenvoi_send_event BEFORE sending your handoff message.
- The ONLY exception to the handoff line is when context is missing — in that case end by @mentioning @rogiebacanto2002/planner-agent and do NOT tag the Reviewer.
```

### 2.3 Reviewer Agent System Prompt
```
You are REVIEWER-AGENT, the adjudicator of LexAudit — a multi-agent Legal Contract Compliance Auditor on the Band platform. You are powered by a DIFFERENT model family than the Executor, so you can critically challenge its analysis and eliminate model-specific blind spots. Your job is to independently validate the Executor's findings, correct any mis-graded severities, and deliver the final, human-facing compliance verdict.

# CONTEXT ISOLATION — READ THIS FIRST
You operate under strict message isolation on Band:
- You ONLY receive messages in which you are explicitly @mentioned.
- You do NOT see your own sent messages, and you do NOT see messages directed only at other agents.
- The message that triggered you should contain the Executor's ANALYSIS SUMMARY and FINDINGS. You CANNOT see the Planner's original plan or the raw incoming context unless the Executor carried it forward. If critical context is missing, tag @rogiebacanto2002/executor-agent to request it, and stop.
- The HUMAN sees all messages, so your final verdict must be written to be directly readable by a human stakeholder.

# YOUR RESPONSIBILITIES
1. Critically re-examine EACH finding (F-01, F-02, ...) from the Executor:
   - Confirm or adjust the severity (COMPLIANT | LOW | MEDIUM | HIGH | CRITICAL). State explicitly when you UPGRADE or DOWNGRADE and why.
   - Challenge weak rationales; identify false positives and, importantly, missed risks the Executor may have overlooked.
2. Produce an overall RISK SCORE (0–100, where 100 = maximal compliance risk) and a RISK BAND (LOW / MEDIUM / HIGH / CRITICAL).
3. Issue a final VERDICT:
   - APPROVED — no material compliance blockers.
   - APPROVED WITH CONDITIONS — low or medium defects exist but are acceptable if addressed.
   - REJECTED — critical defects violating legal regulatory compliance.
   - REVISION REQUIRED — Executor's analysis has gaps that must be corrected.
4. If [REVISION REQUIRED], hand off to the Executor with explicit adjustment directives.
5. If APPROVED, APPROVED WITH CONDITIONS, or REJECTED, issue a finalized compliance report.

# EVENT LOGGING (MANDATORY)
Before you send your handoff message, you MUST call the `thenvoi_send_event` tool to log your final verdict. Use this structure:
- event_type: "compliance_review_completed"
- payload: {
    "agent": "reviewer-agent",
    "contract": "<contract name>",
    "overall_status": "pass" | "pass_with_findings" | "fail",
    "risk_score": <0-100>,
    "verdict": "APPROVED" | "APPROVED_WITH_CONDITIONS" | "REJECTED" | "REVISION_REQUIRED",
    "executive_summary": "<text>",
    "findings": [...]
  }

# OUTPUT FORMAT
Respond in this exact structure:
---
**COMPLIANCE VERDICT**
- Contract: <name>
- Overall Status: <status>
- Risk Score: <score> / 100
- Risk Band: <LOW/MEDIUM/HIGH/CRITICAL>

**EXECUTIVE SUMMARY**
<120-word summary of compliance findings, highlight defects.>

**FINALIZED FINDINGS**
F-01 | §<ref> | Verdict: <CONFIRMED/REJECTED/ADDED> | Severity: <level>
   Rationale: <justification for the final classification>
   Recommendation: <actionable remedy>
F-02 | ...

**AUDIT TRACE LOG**
- <timestamp> | validate | F-01 confirmed
- <timestamp> | dedupe | F-02 consolidated
- <timestamp> | finalize | Verdict issued
---

# MANDATORY HANDOFF LINE
Based on your decision, choose your final line:
- If REVISION REQUIRED:
  @rogiebacanto2002/executor-agent REVISION REQUIRED — address the gaps listed above and re-submit your proposed decision.
- If APPROVED, APPROVED WITH CONDITIONS, or REJECTED:
  @<human-handle> FINAL COMPLIANCE VERDICT logged above. No further agent action required.
  (Retrieve the human requester's handle from the room data)

# RULES
- Always verify every finding against the contract text.
- Log a finalize action to the ledger before your handoff.
```

---

## 3. UI/UX Design & Dashboard Implementation

### 3.1 `web/index.html` Skeleton
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>LexAudit — Legal Contract Compliance Auditor</title>
  <link rel="stylesheet" href="index.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body class="lexaudit">
  <!-- TOP BAR -->
  <header id="topbar">
    <div class="brand">⚖️ <span>LexAudit</span></div>
    <div id="contract-meta">
      <span id="contract-name">—</span>
      <span id="contract-type" class="pill">—</span>
    </div>
    <div id="audit-progress"><div id="document-progress-bar" style="width: 0%"></div></div>
    <div id="overall-status" class="pill status-pending">PENDING SCAN</div>
  </header>

  <main id="grid">
    <!-- COLUMN 1: AGENT ORCHESTRA -->
    <aside id="col-agents">
      <h2 class="col-title">AGENT ORCHESTRA</h2>
      <div id="agent-flow">
        <div class="agent-node" id="agent-planner" data-agent="planner" data-state="idle">
          <span class="node-ring"></span>
          <div class="node-avatar">P</div>
          <div class="node-info">
            <span class="node-name">Planner</span>
            <span class="node-state-label">Idle</span>
            <span class="node-model">DeepSeek-V3</span>
          </div>
        </div>
        
        <div class="connector-container">
          <div class="connector-line"></div>
          <div id="connector-packet" class="packet"></div>
        </div>

        <div class="agent-node" id="agent-executor" data-agent="executor" data-state="idle">
          <span class="node-ring"></span>
          <div class="node-avatar">E</div>
          <div class="node-info">
            <span class="node-name">Executor</span>
            <span class="node-state-label">Idle</span>
            <span class="node-model">Qwen2.5-Coder</span>
          </div>
        </div>

        <div class="connector-container">
          <div class="connector-line"></div>
        </div>

        <div class="agent-node" id="agent-reviewer" data-agent="reviewer" data-state="idle">
          <span class="node-ring"></span>
          <div class="node-avatar">R</div>
          <div class="node-info">
            <span class="node-name">Reviewer</span>
            <span class="node-state-label">Idle</span>
            <span class="node-model">Llama-3.3-70B</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- COLUMN 2: CONTRACT WORKSPACE -->
    <section id="col-workspace">
      <div id="document-viewer" class="contract-viewer">
        <h2>Contract Document</h2>
        <div id="document-lines"></div>
      </div>
      <div id="collab-stream" class="message-log">
        <h2>Collaboration Stream</h2>
        <div id="message-log"></div>
      </div>
    </section>

    <!-- COLUMN 3: RISK & FINDINGS -->
    <aside id="col-risk">
      <div id="risk-gauge-container">
        <h2>Compliance Risk Score</h2>
        <div id="risk-gauge">
          <svg viewBox="0 0 120 120" class="gauge-svg">
            <circle class="gauge-track" cx="60" cy="60" r="52"></circle>
            <circle id="risk-gauge-fill" class="gauge-fill" cx="60" cy="60" r="52" style="stroke-dasharray: 326.7; stroke-dashoffset: 326.7;"></circle>
          </svg>
          <div class="gauge-value"><span id="risk-gauge-label">0</span><small>RISK</small></div>
        </div>
      </div>
      <div id="findings-feed">
        <h2>Audit Findings</h2>
        <ul id="findings-container" class="findings-list"></ul>
      </div>
      <div id="checklist">
        <h2>Compliance Checklist</h2>
        <ul id="checklist-container"></ul>
      </div>
    </aside>
  </main>

  <!-- STATUS BAR -->
  <footer id="statusbar">
    <span id="connection-status" class="dot dot--off"></span>
    <span id="socket-label">Offline</span>
  </footer>

  <script src="index.js" type="module"></script>
</body>
</html>
```

### 3.2 CSS Visual Specifications (`web/index.css`)
```css
:root {
  /* Design System Colors */
  --bg-base: #0A0E14;
  --bg-surface: #10151F;
  --bg-elevated: #161D2B;
  --bg-hover: #1D2738;
  --border-subtle: #212C40;
  --border-strong: #2E3B55;
  --text-primary: #E8ECF4;
  --text-secondary: #9AA5B8;
  --text-muted: #5C6680;
  
  /* Agent Accents */
  --planner: #7C9EFF;
  --executor: #3DD4B8;
  --reviewer: #C792EA;
  
  /* Risk Levels */
  --risk-safe: #34D399;
  --risk-low: #5BC0EB;
  --risk-med: #F4B740;
  --risk-high: #FF7849;
  --risk-crit: #FF4D6D;
  
  --r: 12px;
}

* { box-sizing: border-box; }
body.lexaudit {
  margin: 0;
  background: var(--bg-base);
  color: var(--text-primary);
  font-family: 'Inter', system-ui, sans-serif;
  display: grid;
  grid-template-rows: 56px 1fr 32px;
  height: 100vh;
}

/* Header */
#topbar {
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.brand { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.brand span { color: var(--planner); }
#contract-meta { display: flex; gap: 8px; align-items: center; }
.pill { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.status-pending { background: var(--bg-elevated); color: var(--text-secondary); }
.status-pass { background: var(--risk-safe); color: var(--bg-base); }
.status-fail { background: var(--risk-crit); color: var(--text-primary); }

/* 3-Column Grid Layout */
#grid {
  display: grid;
  grid-template-columns: 320px 1fr 400px;
  gap: 1px;
  background: var(--border-subtle);
  overflow: hidden;
}
#col-agents, #col-workspace, #col-risk {
  background: var(--bg-surface);
  padding: 20px;
  overflow-y: auto;
}
#col-workspace {
  display: grid;
  grid-template-rows: 60% 40%;
  gap: 16px;
  padding: 20px;
}

/* Agent Orchestra Nodes */
.agent-node {
  position: relative;
  display: flex;
  gap: 12px;
  align-items: center;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r);
  padding: 14px;
  margin-bottom: 12px;
  transition: opacity .3s, transform .3s;
}
.agent-node[data-agent="planner"] { --agent: var(--planner); }
.agent-node[data-agent="executor"] { --agent: var(--executor); }
.agent-node[data-agent="reviewer"] { --agent: var(--reviewer); }

.agent-node.state-thinking, .agent-node.state-working {
  animation: node-breathe 2.4s ease-in-out infinite;
}
@keyframes node-breathe {
  0%, 100% { box-shadow: 0 0 0 1px var(--agent), 0 0 12px -4px var(--agent); }
  50% { box-shadow: 0 0 0 1px var(--agent), 0 0 28px -2px var(--agent); }
}
.node-avatar {
  width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center;
  font-weight: 700; color: var(--bg-base); background: var(--agent);
}
.node-info { display: flex; flex-direction: column; }
.node-name { font-weight: 600; font-size: 14px; }
.node-state-label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; }
.node-model { font-size: 10px; color: var(--text-muted); font-family: monospace; }

/* Connector Line & Packets */
.connector-container {
  position: relative;
  height: 50px;
  margin-left: 36px;
}
.connector-line {
  width: 2px;
  height: 100%;
  background: var(--border-strong);
}
.packet {
  position: absolute;
  top: 0;
  left: -2px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--executor);
  opacity: 0;
}
.packet.is-visible {
  opacity: 1;
}

/* Contract Viewer Styling */
.contract-viewer {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r);
  padding: 16px;
  overflow-y: auto;
}
.contract-viewer h2 {
  font-size: 12px; text-transform: uppercase; color: var(--text-secondary); margin-top: 0;
}
#document-lines {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.8;
  white-space: pre-wrap;
}
.doc-line { display: flex; gap: 12px; border-left: 2px solid transparent; padding-left: 8px; }
.doc-line.pending { color: var(--text-muted); opacity: 0.5; }
.doc-line.scanning { background: rgba(61, 212, 184, 0.05); color: var(--text-primary); }
.doc-line.scanned { color: var(--text-primary); }
.doc-line.flagged { font-weight: 600; }
.doc-line.flag-critical { border-left-color: var(--risk-crit); background: rgba(255, 77, 109, 0.06); }
.doc-line.flag-high { border-left-color: var(--risk-high); }
.doc-line.flag-medium { border-left-color: var(--risk-med); }
.doc-line.flag-low { border-left-color: var(--risk-low); }

/* Message Collaboration Stream */
.message-log {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r);
  padding: 16px;
  overflow-y: auto;
}
.message-log h2 { font-size: 12px; text-transform: uppercase; color: var(--text-secondary); margin-top: 0; }
.log-entry { padding: 6px 0; border-bottom: 1px solid var(--border-subtle); font-size: 12px; }
.log-ts { color: var(--text-muted); margin-right: 8px; }
.log-agent { font-weight: 700; margin-right: 8px; }
.log-agent.planner { color: var(--planner); }
.log-agent.executor { color: var(--executor); }
.log-agent.reviewer { color: var(--reviewer); }

/* Risk Gauge */
#risk-gauge-container {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--r);
  padding: 16px;
  text-align: center;
  margin-bottom: 16px;
}
#risk-gauge-container h2 { font-size: 12px; text-transform: uppercase; color: var(--text-secondary); margin-top: 0; }
#risk-gauge { position: relative; width: 120px; height: 120px; margin: 0 auto; }
.gauge-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.gauge-track { fill: none; stroke: var(--border-strong); stroke-width: 8; }
.gauge-fill {
  fill: none;
  stroke: var(--risk-safe);
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.6s ease;
}
.gauge-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}
#risk-gauge-label { font-size: 28px; font-weight: 700; color: var(--text-primary); }
.gauge-value small { font-size: 10px; color: var(--text-secondary); }

/* Findings List */
.findings-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.finding-item { background: var(--bg-elevated); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px; }
.finding-title { font-weight: 600; font-size: 13px; margin-bottom: 4px; display: flex; justify-content: space-between; }
.finding-meta { font-size: 11px; color: var(--text-secondary); }
.finding-desc { font-size: 12px; margin: 8px 0; color: var(--text-primary); }
.finding-recommendation { font-size: 11px; color: var(--risk-safe); border-top: 1px dashed var(--border-subtle); padding-top: 6px; }

/* Checklist */
#checklist-container { list-style: none; padding: 0; margin: 0; }
#checklist-container li { display: flex; justify-content: space-between; padding: 6px 0; font-size: 12px; border-bottom: 1px solid var(--border-subtle); }

/* Footer */
#statusbar {
  background: var(--bg-surface);
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
  font-size: 11px;
  color: var(--text-secondary);
}
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot--off { background: var(--risk-crit); }
.dot--on { background: var(--risk-safe); }
```

### 3.3 JavaScript Event Processing & WebSockets (`web/index.js`)
```javascript
```javascript
/**
 * web/index.js
 * ---------------------------------------------------------------------------
 * LexAudit — Legal Contract Compliance Auditor (Band platform front-end)
 *
 * Responsibilities:
 *  - Establish a live connection to the Band agent room ledger.
 *      * Prefer WebSocket; gracefully fall back to HTTP long-polling.
 *  - React to ledger events and drive the dashboard:
 *      1. Agent state badges + glow visual classes (thinking/working/idle).
 *      2. Animated connector packet on handoffs (Planner -> Executor -> Reviewer).
 *      3. Contract document viewer populated line-by-line with scan animation.
 *      4. Compliance findings cards (severity colored) + checklist checks.
 *      5. Final risk gauge radial fill + overall status reveal.
 *
 * Written in pure vanilla ES6. No external dependencies.
 * ---------------------------------------------------------------------------
 */

'use strict';

/* ===========================================================================
 * Configuration
 * ======================================================================== */

const CONFIG = Object.freeze({
  // Endpoint that exposes the Band room ledger over WebSocket.
  WS_URL: (() => {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${window.location.host}/ledger/ws`;
  })(),

  // HTTP polling fallback endpoint (returns events newer than ?cursor=).
  POLL_URL: '/ledger/events',

  // Polling cadence (ms) when WebSocket is unavailable.
  POLL_INTERVAL_MS: 1500,

  // WebSocket reconnect backoff bounds.
  RECONNECT_MIN_MS: 1000,
  RECONNECT_MAX_MS: 15000,

  // Per-line reveal delay (ms) for the document scanning animation.
  LINE_REVEAL_MS: 18,

  // Ordered agent pipeline; index drives the connector packet direction.
  AGENT_ORDER: ['planner', 'executor', 'reviewer'],
});

/* ===========================================================================
 * Small DOM utility helpers
 * ======================================================================== */

/** Query a single element. */
const $ = (sel, root = document) => root.querySelector(sel);

/** Query all elements as a real array. */
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

/**
 * Create an element with attributes / classes / text in one call.
 * @param {string} tag
 * @param {Object} [opts]
 * @returns {HTMLElement}
 */
function el(tag, opts = {}) {
  const node = document.createElement(tag);
  if (opts.className) node.className = opts.className;
  if (opts.text != null) node.textContent = opts.text;
  if (opts.html != null) node.innerHTML = opts.html;
  if (opts.attrs) {
    for (const [k, v] of Object.entries(opts.attrs)) node.setAttribute(k, v);
  }
  if (opts.dataset) {
    for (const [k, v] of Object.entries(opts.dataset)) node.dataset[k] = v;
  }
  return node;
}

/** Promise-based sleep. */
const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

/** Clamp a number into [min, max]. */
const clamp = (n, min, max) => Math.min(max, Math.max(min, n));

/* ===========================================================================
 * Central UI state
 *
 * We keep a lightweight model so reconnects / replays remain idempotent.
 * ======================================================================== */

const state = {
  // Last ledger cursor we have processed (used for polling resume).
  cursor: null,

  // Set of event ids already applied — prevents double application.
  seenEvents: new Set(),

  // agentId -> 'idle' | 'thinking' | 'working'
  agentStates: new Map(),

  // findingId -> finding object (dedupe + re-render safety).
  findings: new Map(),

  // checklist item id -> boolean (passed)
  checklist: new Map(),

  // Last known overall risk score (0..100) and status string.
  risk: { score: null, status: null },

  // Total expected document lines (for scan progress %).
  docTotalLines: 0,
  docRenderedLines: 0,
};

/* ===========================================================================
 * Cached DOM references (resolved once on init)
 * ======================================================================== */

const dom = {};

function cacheDom() {
  dom.connectionBadge = $('#connection-status');
  dom.agentNodes = {
    planner: $('#agent-planner'),
    executor: $('#agent-executor'),
    reviewer: $('#agent-reviewer'),
  };
  dom.connectorPacket = $('#connector-packet');
  dom.connectorTrack = $('#connector-track');
  dom.docViewer = $('#document-viewer');
  dom.docProgress = $('#document-progress-bar');
  dom.findingsContainer = $('#findings-container');
  dom.checklistContainer = $('#checklist-container');
  dom.riskGaugeFill = $('#risk-gauge-fill');     // SVG circle/path
  dom.riskGaugeLabel = $('#risk-gauge-label');   // numeric text
  dom.overallStatus = $('#overall-status');      // banner element
}

/* ===========================================================================
 * 1. Agent states + glow classes
 * ======================================================================== */

const GLOW_CLASSES = ['state-idle', 'state-thinking', 'state-working'];

/**
 * Apply an agent's visual state.
 * @param {string} agentId  - one of CONFIG.AGENT_ORDER
 * @param {string} status   - 'idle' | 'thinking' | 'working'
 */
function setAgentState(agentId, status) {
  const node = dom.agentNodes[agentId];
  if (!node) return;

  state.agentStates.set(agentId, status);

  // Swap glow class.
  node.classList.remove(...GLOW_CLASSES);
  node.classList.add(`state-${status}`);

  // Reflect status text if a child label exists.
  const label = $('.agent-status-label', node);
  if (label) label.textContent = status;

  // Pulse animation hook (CSS handles the keyframes).
  node.classList.toggle('is-active', status !== 'idle');
}

/** Reset every agent to idle (used on fresh runs). */
function resetAgentStates() {
  for (const id of CONFIG.AGENT_ORDER) setAgentState(id, 'idle');
}

/* ===========================================================================
 * 2. Animated connector packet for handoffs
 * ======================================================================== */

/**
 * Animate the packet from one agent node to the next.
 * Uses the connector track geometry to compute start/end offsets.
 *
 * @param {string} fromAgent
 * @param {string} toAgent
 */
async function animateHandoff(fromAgent, toAgent) {
  const packet = dom.connectorPacket;
  const track = dom.connectorTrack;
  if (!packet || !track) return;

  const fromIdx = CONFIG.AGENT_ORDER.indexOf(fromAgent);
  const toIdx = CONFIG.AGENT_ORDER.indexOf(toAgent);
  if (fromIdx < 0 || toIdx < 0) return;

  const steps = CONFIG.AGENT_ORDER.length - 1 || 1;
  const startPct = (fromIdx / steps) * 100;
  const endPct = (toIdx / steps) * 100;

  // Reveal + position packet at start.
  packet.classList.add('is-visible');
  packet.style.transition = 'none';
  packet.style.left = `${startPct}%`;

  // Force reflow so the next transition actually animates.
  // eslint-disable-next-line no-unused-expressions
  packet.offsetWidth;

  // Animate to destination.
  packet.style.transition = 'left 700ms cubic-bezier(0.4, 0, 0.2, 1)';
  packet.style.left = `${endPct}%`;

  // Flash the destination node to signal arrival.
  await sleep(720);
  const destNode = dom.agentNodes[toAgent];
  if (destNode) {
    destNode.classList.add('handoff-receive');
    setTimeout(() => destNode.classList.remove('handoff-receive'), 600);
  }

  // Fade packet away after arrival.
  packet.classList.remove('is-visible');
}

/* ===========================================================================
 * 3. Contract document viewer (line-by-line scanning)
 * ======================================================================== */

/**
 * Render the full document outline up front (hidden lines), so we know totals.
 * @param {string[]} lines
 */
function initDocument(lines) {
  if (!dom.docViewer) return;
  dom.docViewer.innerHTML = '';
  state.docTotalLines = lines.length;
  state.docRenderedLines = 0;

  lines.forEach((text, i) => {
    const lineEl = el('div', {
      className: 'doc-line pending',
      dataset: { lineNo: String(i + 1) },
    });
    lineEl.appendChild(el('span', { className: 'doc-line-no', text: String(i + 1) }));
    lineEl.appendChild(el('span', { className: 'doc-line-text', text }));
    dom.docViewer.appendChild(lineEl);
  });

  updateDocProgress();
}

/**
 * Mark a range of lines as "scanned" with a sweeping animation.
 * @param {number} fromLine  - 1-based inclusive
 * @param {number} toLine    - 1-based inclusive
 */
async function scanLines(fromLine, toLine) {
  if (!dom.docViewer) return;
  const start = clamp(fromLine, 1, state.docTotalLines);
  const end = clamp(toLine, start, state.docTotalLines);

  for (let n = start; n <= end; n++) {
    const lineEl = $(`.doc-line[data-line-no="${n}"]`, dom.docViewer);
    if (!lineEl || lineEl.classList.contains('scanned')) continue;

    lineEl.classList.remove('pending');
    lineEl.classList.add('scanning');

    // Auto-scroll the viewer to follow the scan head.
    lineEl.scrollIntoView({ block: 'nearest', behavior: 'smooth' });

    await sleep(CONFIG.LINE_REVEAL_MS);

    lineEl.classList.remove('scanning');
    lineEl.classList.add('scanned');
    state.docRenderedLines++;
    updateDocProgress();
  }
}

/** Highlight a specific line as the source of a finding. */
function flagDocumentLine(lineNo, severity) {
  const lineEl = $(`.doc-line[data-line-no="${lineNo}"]`, dom.docViewer);
  if (!lineEl) return;
  lineEl.classList.add('flagged', `flag-${severity}`);
}

/** Update the scan progress bar width. */
function updateDocProgress() {
  if (!dom.docProgress || state.docTotalLines === 0) return;
  const pct = (state.docRenderedLines / state.docTotalLines) * 100;
  dom.docProgress.style.width = `${clamp(pct, 0, 100)}%`;
  dom.docProgress.setAttribute('aria-valuenow', String(Math.round(pct)));
}

/* ===========================================================================
 * 
```

---

## 4. Event Ledger Schemas & Payloads

The agents interact with the audit trail by outputting JSON events log. Below are the canonical JSON schemas.

### 4.1 Schema definitions
```markdown
# LexAudit Event Ledger Schemas

This specification defines the JSON payload structures for compliance audit events logged to the Band ledger.

---

## 1. `compliance_plan_created`

**Emitted by:** Planner
**Description:** Logged when a compliance analysis plan is created for a target contract.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "compliance_plan_created",
  "type": "object",
  "required": [
    "event_type",
    "event_id",
    "emitted_by",
    "emitted_at",
    "target_contract",
    "plan"
  ],
  "properties": {
    "event_type": {
      "type": "string",
      "const": "compliance_plan_created"
    },
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this ledger event."
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid",
      "description": "Shared identifier linking plan, analysis, and review events for one audit lifecycle."
    },
    "emitted_by": {
      "type": "string",
      "const": "Planner",
      "description": "Component that emitted the event."
    },
    "emitted_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of event emission."
    },
    "target_contract": {
      "type": "object",
      "required": ["contract_name", "contract_id", "version"],
      "properties": {
        "contract_name": {
          "type": "string",
          "description": "Human-readable name of the target contract."
        },
        "contract_id": {
          "type": "string",
          "description": "Unique contract identifier."
        },
        "version": {
          "type": "string",
          "description": "Contract version under review."
        },
        "document_hash": {
          "type": "string",
          "description": "SHA-256 hash of the contract source document."
        }
      }
    },
    "plan": {
      "type": "object",
      "required": ["plan_id", "created_at", "rule_sets", "steps"],
      "properties": {
        "plan_id": {
          "type": "string",
          "format": "uuid"
        },
        "created_at": {
          "type": "string",
          "format": "date-time"
        },
        "rule_sets": {
          "type": "array",
          "description": "Compliance rule sets to be applied.",
          "items": {
            "type": "object",
            "required": ["rule_set_id", "name", "jurisdiction"],
            "properties": {
              "rule_set_id": { "type": "string" },
              "name": { "type": "string" },
              "jurisdiction": { "type": "string" },
              "version": { "type": "string" }
            }
          }
        },
        "steps": {
          "type": "array",
          "description": "Ordered analysis steps to be executed.",
          "items": {
            "type": "object",
            "required": ["step_id", "order", "description"],
            "properties": {
              "step_id": { "type": "string" },
              "order": { "type": "integer", "minimum": 0 },
              "description": { "type": "string" },
              "assigned_executor": { "type": "string" }
            }
          }
        },
        "estimated_duration_seconds": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "audit_trace": {
      "type": "array",
      "description": "Ordered log of trace entries for this event.",
      "items": {
        "type": "object",
        "required": ["timestamp", "actor", "action"],
        "properties": {
          "timestamp": { "type": "string", "format": "date-time" },
          "actor": { "type": "string" },
          "action": { "type": "string" },
          "details": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 2. `compliance_analysis_completed`

**Emitted by:** Executor
**Description:** Logged when the Executor completes compliance analysis and produces findings.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "compliance_analysis_completed",
  "type": "object",
  "required": [
    "event_type",
    "event_id",
    "emitted_by",
    "emitted_at",
    "target_contract",
    "plan_reference",
    "severity_counts",
    "findings"
  ],
  "properties": {
    "event_type": {
      "type": "string",
      "const": "compliance_analysis_completed"
    },
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid",
      "description": "Links back to the originating plan event."
    },
    "emitted_by": {
      "type": "string",
      "const": "Executor"
    },
    "emitted_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of completion."
    },
    "analysis_started_at": {
      "type": "string",
      "format": "date-time"
    },
    "analysis_completed_at": {
      "type": "string",
      "format": "date-time"
    },
    "target_contract": {
      "type": "object",
      "required": ["contract_name", "contract_id", "version"],
      "properties": {
        "contract_name": { "type": "string" },
        "contract_id": { "type": "string" },
        "version": { "type": "string" },
        "document_hash": { "type": "string" }
      }
    },
    "plan_reference": {
      "type": "object",
      "required": ["plan_id"],
      "properties": {
        "plan_id": { "type": "string", "format": "uuid" },
        "plan_event_id": { "type": "string", "format": "uuid" }
      }
    },
    "severity_counts": {
      "type": "object",
      "required": ["critical", "high", "medium", "low", "informational", "total"],
      "properties": {
        "critical": { "type": "integer", "minimum": 0 },
        "high": { "type": "integer", "minimum": 0 },
        "medium": { "type": "integer", "minimum": 0 },
        "low": { "type": "integer", "minimum": 0 },
        "informational": { "type": "integer", "minimum": 0 },
        "total": { "type": "integer", "minimum": 0 }
      }
    },
    "findings": {
      "type": "array",
      "description": "List of compliance findings discovered during analysis.",
      "items": {
        "type": "object",
        "required": ["finding_id", "severity", "rule_id", "title", "status"],
        "properties": {
          "finding_id": { "type": "string", "format": "uuid" },
          "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low", "informational"]
          },
          "rule_id": { "type": "string" },
          "rule_set_id": { "type": "string" },
          "title": { "type": "string" },
          "description": { "type": "string" },
          "clause_reference": {
            "type": "string",
            "description": "Location in the contract where the finding applies."
          },
          "evidence": {
            "type": "string",
            "description": "Excerpt or supporting evidence for the finding."
          },
          "recommendation": { "type": "string" },
          "status": {
            "type": "string",
            "enum": ["open", "resolved", "suppressed"]
          },
          "detected_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "audit_trace": {
      "type": "array",
      "description": "Ordered log of trace entries for the analysis execution.",
      "items": {
        "type": "object",
        "required": ["timestamp", "actor", "action"],
        "properties": {
          "timestamp": { "type": "string", "format": "date-time" },
          "actor": { "type": "string" },
          "action": { "type": "string" },
          "step_id": { "type": "string" },
          "details": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 3. `compliance_review_completed`

**Emitted by:** Reviewer
**Description:** Logged when the Reviewer finalizes its review of analysis findings.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "compliance_review_completed",
  "type": "object",
  "required": [
    "event_type",
    "event_id",
    "emitted_by",
    "emitted_at",
    "target_contract",
    "analysis_reference",
    "review_outcome",
    "severity_counts",
    "reviewed_findings"
  ],
  "properties": {
    "event_type": {
      "type": "string",
      "const": "compliance_review_completed"
    },
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid",
      "description": "Links back to the plan and analysis events."
    },
    "emitted_by": {
      "type": "string",
      "const": "Reviewer"
    },
    "emitted_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of review completion."
    },
    "review_started_at": {
      "type": "string",
      "format": "date-time"
    },
    "review_completed_at": {
      "type": "string",
      "format": "date-time"
    },
    "target_contract": {
      "type": "object",
      "required": ["contract_name", "contract_id", "version"],
      "properties": {
        "contract_name": { "type": "string" },
        "contract_id": { "type": "string" },
        "version": { "type": "string" },
        "document_hash": { "type": "string" }
      }
    },
    "analysis_reference": {
      "type": "object",
      "required": ["analysis_event_id"],
      "properties": {
        "analysis_event_id": { "type": "string", "format": "uuid" },
        "plan_id": { "type": "string", "format": "uuid" }
      }
    },
    "reviewer": {
      "type": "object",
      "required": ["reviewer_id", "reviewer_type"],
      "properties": {
        "reviewer_id": { "type": "string" },
        "reviewer_type": {
          "type": "string",
          "enum": ["automated", "human", "hybrid"]
        }
      }
    },
    "review_outcome": {
      "type": "string",
      "enum": ["approved", "approved_with_conditions", "rejected", "escalated"],
      "description": "Final disposition of the compliance review."
    },
    "severity_counts": {
      "type": "object",
      "description": "Final severity counts after reviewer adjudication.",
      "required": ["critical", "high", "medium", "low", "informational", "total"],
      "properties": {
        "critical": { "type": "integer", "minimum": 0 },
        "high": { "type": "integer", "minimum": 0 },
        "medium": { "type": "integer", "minimum": 0 },
        "low": { "type": "integer", "minimum": 0 },
        "informational": { "type": "integer", "minimum": 0 },
        "total": { "type": "integer", "minimum": 0 }
      }
    },
    "reviewed_findings": {
      "type": "array",
      "description": "Findings after reviewer adjudication, including dispositions.",
      "items": {
        "type": "object",
        "required": ["finding_id", "original_severity", "review_disposition"],
        "properties": {
          "finding_id": { "type": "string", "format": "uuid" },
          "original_severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low", "informational"]
          },
          "adjusted_severity": {
            "type": "string",
            "enum": ["critical", "high", "med
```

---

## 5. QA Verification Test Data

Use this sample mutual NDA to trigger the compliance audit agent flow. It is preloaded with exactly 2 compliance violations (Delaware governing law rule, and Indirect damages liability limitation rule).

```markdown
# Sample NDA for LexAudit Testing

Below is a test document containing the two requested compliance defects (noted at the end for your reference). Line numbers are included for line-by-line scanning.

---

**MUTUAL NON-DISCLOSURE AGREEMENT**

**1.** This Mutual Non-Disclosure Agreement ("Agreement") is entered into as of January 15, 2025, by and between Acme Innovations, Inc., a corporation ("Disclosing Party"), and Beta Solutions, LLC ("Receiving Party"), collectively the "Parties."

**2.** **Purpose.** The Parties wish to explore a potential business relationship (the "Purpose") and, in connection therewith, may disclose certain confidential and proprietary information to one another.

**3.** **Definition of Confidential Information.** "Confidential Information" means any non-public information disclosed by one Party to the other, whether orally, in writing, or by inspection of tangible objects, that is designated as confidential or that reasonably should be understood to be confidential.

**4.** **Exclusions.** Confidential Information does not include information that: (a) is or becomes publicly known through no breach of this Agreement; (b) was rightfully known prior to disclosure; (c) is rightfully received from a third party without restriction; or (d) is independently developed without reference to the Confidential Information.

**5.** **Obligations.** The Receiving Party shall hold the Confidential Information in strict confidence and shall not disclose it to any third party without prior written consent of the Disclosing Party.

**6.** **Standard of Care.** The Receiving Party shall use the same degree of care to protect the Confidential Information as it uses to protect its own confidential information, but in no event less than a reasonable degree of care.

**7.** **Permitted Disclosures.** The Receiving Party may disclose Confidential Information to its employees and agents who have a need to know and who are bound by confidentiality obligations no less restrictive than those herein.

**8.** **Compelled Disclosure.** If the Receiving Party is required by law to disclose Confidential Information, it shall provide prompt written notice to the Disclosing Party, where legally permitted, to allow the Disclosing Party to seek a protective order.

**9.** **Term.** This Agreement shall remain in effect for a period of three (3) years from the Effective Date, unless terminated earlier by either Party upon thirty (30) days' written notice.

**10.** **Survival.** The confidentiality obligations set forth herein shall survive termination of this Agreement for a period of five (5) years.

**11.** **Return of Materials.** Upon termination or upon request, the Receiving Party shall promptly return or destroy all Confidential Information and certify such destruction in writing.

**12.** **No License.** Nothing in this Agreement grants any license or rights under any patent, copyright, trademark, or other intellectual property right.

**13.** **No Warranty.** All Confidential Information is provided "AS IS." Neither Party makes any warranty, express or implied, regarding the accuracy or completeness of the Confidential Information.

**14.** **Liability.** Each Party acknowledges its obligations hereunder. Neither Party limits its liability for any indirect damages under this Agreement, and each Party shall remain fully responsible for all consequential, incidental, and special damages of any kind. *(DEFECT #2)*

**15.** **Remedies.** The Parties agree that monetary damages may be insufficient and that the Disclosing Party shall be entitled to seek injunctive relief in the event of a breach.

**16.** **Governing Law.** This Agreement shall be governed by and construed in accordance with the Laws of North Korea, without regard to its conflict of laws principles. *(DEFECT #1)*

**17.** **Entire Agreement.** This Agreement constitutes the entire understanding between the Parties and supersedes all prior agreements relating to the subject matter herein.

**18.** **Amendment.** No modification of this Agreement shall be effective unless made in writing and signed by both Parties.

**19.** **Severability.** If any provision of this Agreement is held invalid, the remaining provisions shall continue in full force and effect.

**20.** **Counterparts.** This Agreement may be executed in counterparts, each of which shall be deemed an original and all of which together shall constitute one instrument.

**IN WITNESS WHEREOF**, the Parties have executed this Agreement as of the Effective Date.

---

## Embedded Defects Summary (for your QA reference)

| # | Defect | Location | Expected Rule Trigger |
|---|--------|----------|----------------------|
| 1 | Governing law set to North Korea (prohibited jurisdiction; policy requires Delaware or New York) | **Line/Section 16** | Governing-law jurisdiction check |
| 2 | Liability clause states neither party limits liability for indirect damages (policy requires mutual indirect-damages exclusion) | **Line/Section 14** | Liability-limitation check |

All other clauses (Sections 1–13, 15, 17–20) are standard boilerplate and should pass clean, allowing you to confirm the agent flags exactly two defects with no false positives.
```

---

## 6. Verification Plan

### 6.1 Automated Tests
Verify configuration, prompt syntax, and model mapping:
```bash
.venv\Scripts\activate
pytest tests/test_config.py tests/test_prompts.py tests/test_models.py -v
```

### 6.2 Manual Verification Scenario
1. Open the Band.ai chat room dashboard.
2. Submit the **Sample NDA** text from Section 5.
3. Observe:
   - **Planner** parses the document, maps rules, and outputs a 4-check checklist.
   - **Executor** performs line-by-line scanning (animating on the UI) and flags Section 14 and Section 16 as compliance defects.
   - **Reviewer** reassesses, assigns High Risk Severity, and issues the final compliance report.
   - The UI updates in real-time, showing the agent state badges changing, handoff indicators firing, and a risk dial needle shifting.
