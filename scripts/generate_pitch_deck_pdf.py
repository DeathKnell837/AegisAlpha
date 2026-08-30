# scripts/generate_pitch_deck_pdf.py
import os
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

PDF_PATH = "c:/Users/USER/Desktop/HACKATHON/AegisAlpha_Pitch_Deck.pdf"
AVATAR_PATH = "c:/Users/USER/Desktop/HACKATHON/team_avatar.jpg"
BANNER_PATH = "c:/Users/USER/Desktop/HACKATHON/team_banner.jpg"

doc = SimpleDocTemplate(
    PDF_PATH,
    pagesize=landscape(letter),
    leftMargin=36,
    rightMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'DeckTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=26,
    leading=32,
    textColor=colors.HexColor('#0B0E11')
)

subtitle_style = ParagraphStyle(
    'DeckSubtitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=18,
    textColor=colors.HexColor('#00A884')
)

header_style = ParagraphStyle(
    'DeckHeader',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=24,
    textColor=colors.HexColor('#0B0E11')
)

body_style = ParagraphStyle(
    'DeckBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=11,
    leading=16,
    textColor=colors.HexColor('#2D3748')
)

bullet_style = ParagraphStyle(
    'DeckBullet',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10.5,
    leading=15,
    textColor=colors.HexColor('#1A202C')
)

tag_style = ParagraphStyle(
    'DeckTag',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9,
    leading=12,
    textColor=colors.HexColor('#4A5568')
)

story = []

def add_slide_header(title_text, subtitle_text):
    story.append(Paragraph(title_text, header_style))
    story.append(Paragraph(subtitle_text, subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#00D4AA'), spaceBefore=2, spaceAfter=14))

# ─── SLIDE 1: COVER ───
story.append(Spacer(1, 20))
if os.path.exists(BANNER_PATH):
    story.append(Image(BANNER_PATH, width=540, height=210))
story.append(Spacer(1, 15))
story.append(Paragraph("AegisAlpha: Autonomous Multi-Agent Options Trading Desk", title_style))
story.append(Paragraph("LabLab.ai × Alpaca AI Trading Agents Hackathon Submission | Team Returnee", subtitle_style))
story.append(Spacer(1, 10))
story.append(Paragraph("<b>Live URL:</b> https://aegis-alpha-desk.vercel.app  |  <b>GitHub:</b> DeathKnell837/band-of-agents-hackathon", tag_style))
story.append(Spacer(1, 50))

# ─── SLIDE 2: THE PROBLEM ───
add_slide_header("1. The Core Problem in AI Trading", "Why 99% of LLM trading algorithms fail in production")
p2_data = [
    [Paragraph("<b>Conventional Retail Bots</b>", subtitle_style), Paragraph("<b>The AegisAlpha Paradigm</b>", subtitle_style)],
    [
        Paragraph("• <b>Unhedged Risk:</b> Place raw directional stock or naked options with unlimited loss potential.<br/><br/>• <b>Hallucinated Sizing:</b> LLMs allocate arbitrary position sizes without mathematical risk bounding.<br/><br/>• <b>No Greeks Awareness:</b> Blind to Delta convexity, Theta decay, and Implied Volatility crush.", bullet_style),
        Paragraph("• <b>Defined-Risk Spreads Only:</b> Executes Bull Call Spreads, Bear Put Spreads, and Iron Condors with fixed maximum loss.<br/><br/>• <b>Zero-LLM Risk Authority:</b> 7 hardcoded Python gates enforce strict 2% equity risk caps ($2,000 max).<br/><br/>• <b>Quantitative Greeks Optimizer:</b> Real-time Alpaca chain filtering targeting optimal 0.40/0.20 Delta ratios.", bullet_style)
    ]
]
t2 = Table(p2_data, colWidths=[340, 360])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
    ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor('#EDF2F7')),
    ('TOPPADDING', (0,0), (-1,-1), 12),
    ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ('LEFTPADDING', (0,0), (-1,-1), 14),
    ('RIGHTPADDING', (0,0), (-1,-1), 14),
]))
story.append(t2)
story.append(Spacer(1, 60))

# ─── SLIDE 3: MULTI-AGENT ARCHITECTURE ───
add_slide_header("2. Autonomous 4-Agent Dialectic Architecture", "Separating hypothesis generation from mathematical execution")
p3_data = [
    [Paragraph("<b>Agent</b>", tag_style), Paragraph("<b>Core Engine & Role</b>", tag_style), Paragraph("<b>Output / Mechanism</b>", tag_style)],
    [
        Paragraph("<b>1. Market Scanner</b>", bullet_style),
        Paragraph("Alpaca IEX Data Client", bullet_style),
        Paragraph("Ingests real-time 1m/5m/1d bars, calculates 30-day realized volatility & 5/20 MA momentum.", bullet_style)
    ],
    [
        Paragraph("<b>2. Alpha Strategist</b>", bullet_style),
        Paragraph("Qwen-2.5-72B (Featherless AI)", bullet_style),
        Paragraph("Evaluates regime, scores thesis confidence, and formulates multi-leg spread structures.", bullet_style)
    ],
    [
        Paragraph("<b>3. Greeks Optimizer</b>", bullet_style),
        Paragraph("Alpaca Options Historical Feed", bullet_style),
        Paragraph("Filters option contracts for strike expiration, liquidity, and 0.40/0.20 Delta ratios.", bullet_style)
    ],
    [
        Paragraph("<b>4. Risk Gatekeeper</b>", bullet_style),
        Paragraph("Deterministic Risk Engine", bullet_style),
        Paragraph("7 hardcoded mathematical safety gates. Pass/Veto verdict with zero LLM override.", bullet_style)
    ]
]
t3 = Table(p3_data, colWidths=[160, 210, 330])
t3.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 10),
    ('RIGHTPADDING', (0,0), (-1,-1), 10),
]))
story.append(t3)
story.append(Spacer(1, 60))

# ─── SLIDE 4: THE 7 RISK GATES ───
add_slide_header("3. The 7 Deterministic Risk Guardrails", "Mathematical boundaries protecting portfolio equity ($100k Account PA3PL5AZ85K6)")
p4_data = [
    [Paragraph("<b>Gate</b>", tag_style), Paragraph("<b>Name</b>", tag_style), Paragraph("<b>Constraint Rule</b>", tag_style), Paragraph("<b>Enforcement</b>", tag_style)],
    [Paragraph("Gate 1", bullet_style), Paragraph("Defined-Risk Only", bullet_style), Paragraph("No naked calls/puts. Spreads only.", bullet_style), Paragraph("HARD BLOCK", subtitle_style)],
    [Paragraph("Gate 2", bullet_style), Paragraph("Max Risk per Trade", bullet_style), Paragraph("Max $2,000 loss (2.0% equity cap)", bullet_style), Paragraph("VETO / RESIZE", subtitle_style)],
    [Paragraph("Gate 3", bullet_style), Paragraph("Portfolio Options Cap", bullet_style), Paragraph("Max $20,000 total active in options (20%)", bullet_style), Paragraph("HARD BLOCK", subtitle_style)],
    [Paragraph("Gate 4", bullet_style), Paragraph("Bid-Ask Liquidity", bullet_style), Paragraph("Spread must be <15% of contract mid-price", bullet_style), Paragraph("SLIPPAGE FILTER", subtitle_style)],
    [Paragraph("Gate 5", bullet_style), Paragraph("DTE Horizon", bullet_style), Paragraph("Target expiration window: 5 to 45 DTE", bullet_style), Paragraph("GAMMA PIN GUARD", subtitle_style)],
    [Paragraph("Gate 6", bullet_style), Paragraph("Drawdown Breaker", bullet_style), Paragraph("Immediate freeze if daily loss hits -3.0%", bullet_style), Paragraph("CIRCUIT BREAKER", subtitle_style)],
    [Paragraph("Gate 7", bullet_style), Paragraph("Dynamic Sizing", bullet_style), Paragraph("Auto-scales contracts to stay inside $2k cap", bullet_style), Paragraph("DYNAMIC SCALE", subtitle_style)],
]
t4 = Table(p4_data, colWidths=[65, 160, 310, 165])
t4.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
story.append(t4)
story.append(Spacer(1, 60))

# ─── SLIDE 5: FASTMCP & LIVE TELEMETRY ───
add_slide_header("4. FastMCP Tools & Quantum Observability", "Seamless agent tool integration and real-time execution telemetry")
story.append(Paragraph("<b>FastMCP Autonomous Agent Tools:</b> Exposes 5 standalone MCP tools for AI IDEs (Cursor, Claude Desktop, Antigravity) — <code>get_account_telemetry</code>, <code>scan_and_propose_spread</code>, <code>validate_risk_gate</code>, <code>execute_options_order</code>, and <code>emergency_kill_switch</code>.", body_style))
story.append(Spacer(1, 12))
story.append(Paragraph("<b>Quantum Dark Web Dashboard:</b> Real-time paper trading interface featuring dynamic payoff curves, Greeks matrix (Delta/Gamma/Theta/Vega/IV), live orders and active positions tracking, and 1-click autonomous cycle execution.", body_style))
story.append(Spacer(1, 16))
story.append(Paragraph("<b>Submission Links:</b><br/>• <b>Web Dashboard:</b> https://aegis-alpha-desk.vercel.app<br/>• <b>Interactive Slides:</b> https://aegis-alpha-desk.vercel.app/slides.html<br/>• <b>GitHub Repo:</b> https://github.com/DeathKnell837/band-of-agents-hackathon", bullet_style))

doc.build(story)
print(f"PDF Successfully generated at: {PDF_PATH} ({os.path.getsize(PDF_PATH)} bytes)")
