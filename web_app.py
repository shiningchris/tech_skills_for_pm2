import io
import json
import os
import queue
import sys
import threading
import uuid
from datetime import datetime

import anthropic
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, send_file

from agents import DesignAgent, MarketerAgent, PMAgent, TechAgent
from config import Config
from models.brief import ProductBrief
from models.scorecard import LeanCanvas, Scorecard
from orchestrator.debate_loop import DebateOrchestrator
from orchestrator.message_bus import MessageBus
from output.exporter import Exporter

load_dotenv()

app = Flask(__name__)

# sprint_id → queue.Queue of SSE event dicts
sprints: dict[str, queue.Queue] = {}


# ── Routes ────────────────────────────────────────────────────── #

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/history")
def history():
    """Return metadata for the 3 most recent completed sprints."""
    output_dir = Config().OUTPUT_DIR
    if not os.path.isdir(output_dir):
        return jsonify([])

    files = sorted(
        [f for f in os.listdir(output_dir) if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(output_dir, f)),
        reverse=True,
    )[:3]

    results = []
    for fname in files:
        try:
            with open(os.path.join(output_dir, fname)) as f:
                data = json.load(f)
            sc = data.get("scorecard", {})
            results.append({
                "filename": fname,
                "idea_title": data.get("idea_title", "Untitled"),
                "go_no_go": sc.get("go_no_go", "—"),
                "overall_score": sc.get("overall_score", 0),
                "exported_at": data.get("exported_at", ""),
                "scorecard": sc,
            })
        except Exception:
            continue

    return jsonify(results)


@app.get("/api/sprint/<filename>")
def get_sprint(filename: str):
    """Return full sprint data including debate transcript and lean canvas."""
    if ".." in filename or "/" in filename or not filename.endswith(".json"):
        return jsonify({"error": "Invalid filename"}), 400

    path = os.path.join(Config().OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Sprint not found"}), 404

    with open(path) as f:
        data = json.load(f)
    return jsonify(data)


@app.get("/api/pdf/<filename>")
def download_pdf(filename: str):
    """Generate and stream a PDF report for the given sprint."""
    import traceback
    if ".." in filename or "/" in filename or not filename.endswith(".json"):
        return jsonify({"error": "Invalid filename"}), 400

    path = os.path.join(Config().OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Sprint not found"}), 404

    try:
        with open(path) as f:
            data = json.load(f)
        pdf_bytes = _generate_pdf(data)
    except Exception as exc:
        return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500

    pdf_name = filename.replace(".json", ".pdf")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"validation-{pdf_name}",
    )


@app.post("/api/start")
def start():
    data = request.get_json(force=True)

    required = ["idea_title", "problem_statement", "proposed_solution",
                "target_user", "revenue_model", "stage"]
    missing = [f for f in required if not data.get(f, "").strip()]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "ANTHROPIC_API_KEY is not set on the server"}), 500

    brief = ProductBrief(
        idea_title=data["idea_title"].strip(),
        problem_statement=data["problem_statement"].strip(),
        proposed_solution=data["proposed_solution"].strip(),
        target_user=data["target_user"].strip(),
        revenue_model=data["revenue_model"].strip(),
        known_competitors=data.get("known_competitors", "").strip(),
        stage=data.get("stage", "idea").strip(),
    )

    sprint_id = str(uuid.uuid4())
    q: queue.Queue = queue.Queue()
    sprints[sprint_id] = q

    t = threading.Thread(target=_run_debate, args=(sprint_id, brief, api_key, q), daemon=True)
    t.start()

    return jsonify({"sprint_id": sprint_id})


@app.get("/api/stream/<sprint_id>")
def stream(sprint_id: str):
    q = sprints.get(sprint_id)
    if q is None:
        return jsonify({"error": "Unknown sprint_id"}), 404

    def generate():
        total_waited = 0
        max_wait = 360  # 6 min hard cap
        while total_waited < max_wait:
            try:
                event = q.get(timeout=15)
            except queue.Empty:
                total_waited += 15
                yield ": keepalive\n\n"
                continue

            total_waited = 0
            yield _sse(event)

            if event.get("type") in ("done", "error"):
                sprints.pop(sprint_id, None)
                break
        else:
            yield _sse({"type": "error", "message": "Sprint timed out after 6 minutes"})

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── Debate runner (background thread) ────────────────────────── #

def _run_debate(sprint_id: str, brief: ProductBrief, api_key: str, q: queue.Queue) -> None:
    try:
        config = Config()
        client = anthropic.Anthropic(api_key=api_key)

        pm = PMAgent(client, config)
        marketer = MarketerAgent(client, config)
        tech = TechAgent(client, config)
        design = DesignAgent(client, config)

        bus = MessageBus()
        current_round = [0]

        def on_message(agent_name: str, content: str, round_num: int) -> None:
            if agent_name == "__status__":
                q.put({"type": "status", "message": content})
                return
            if round_num != current_round[0]:
                current_round[0] = round_num
                q.put({"type": "round_start", "round": round_num})
            q.put({"type": "message", "agent": agent_name, "content": content, "round": round_num})

        orchestrator = DebateOrchestrator(
            pm=pm, marketer=marketer, tech=tech, design=design,
            bus=bus, config=config, on_message=on_message,
        )

        scorecard = orchestrator.run(brief)

        saved_filename = None
        try:
            exporter = Exporter(output_dir=config.OUTPUT_DIR)
            saved_path = exporter.save_json(
                scorecard, brief,
                bus=bus,
                lean_canvas=scorecard.lean_canvas,
            )
            exporter.save_markdown(scorecard, brief, bus)
            saved_filename = os.path.basename(saved_path)
        except Exception:
            pass

        q.put({"type": "scorecard", "data": _scorecard_to_dict(scorecard)})
        if scorecard.lean_canvas:
            q.put({"type": "lean_canvas", "data": _lean_canvas_to_dict(scorecard.lean_canvas)})
        q.put({"type": "done", "filename": saved_filename})

    except Exception as exc:
        q.put({"type": "error", "message": str(exc)})
        q.put({"type": "done", "filename": None})


# ── PDF generation ────────────────────────────────────────────── #

def _generate_pdf(data: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        Table, TableStyle, HRFlowable,
    )
    from reportlab.lib.units import cm

    W, _H = A4
    MARGIN = 2.0 * cm
    CW = W - 2 * MARGIN  # usable content width

    # ── Palette ──────────────────────────────────────────────────
    INDIGO     = HexColor('#6366F1')
    INDIGO_BG  = HexColor('#EEF2FF')
    GREY       = HexColor('#6B7280')
    BORDER     = HexColor('#E5E7EB')
    ROW_ALT    = HexColor('#F9FAFB')
    TEXT       = HexColor('#111111')
    BODY_C     = HexColor('#374151')

    # ── Style factory ────────────────────────────────────────────
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    sTitle   = S('title',  fontSize=20, fontName='Helvetica-Bold',   spaceAfter=4,  textColor=TEXT)
    sMeta    = S('meta',   fontSize=9,  fontName='Helvetica',         spaceAfter=2,  textColor=GREY)
    sSection = S('sec',    fontSize=12, fontName='Helvetica-Bold',    spaceBefore=16, spaceAfter=8, textColor=INDIGO)
    sLabel   = S('lbl',    fontSize=8,  fontName='Helvetica-Bold',    spaceAfter=2,  textColor=GREY)
    sILabel  = S('ilbl',   fontSize=8,  fontName='Helvetica-Bold',    spaceAfter=2,  textColor=INDIGO)
    sValue   = S('val',    fontSize=9,  fontName='Helvetica',         leading=13,    textColor=BODY_C)
    sIValue  = S('ival',   fontSize=9,  fontName='Helvetica',         leading=13,    textColor=TEXT)
    sBody    = S('body',   fontSize=10, fontName='Helvetica',         leading=14,    spaceAfter=5,  textColor=BODY_C)
    sSmall   = S('small',  fontSize=8,  fontName='Helvetica',         textColor=GREY)
    sHdr     = S('hdr',    fontSize=9,  fontName='Helvetica-Bold',    textColor=GREY)
    sDim     = S('dim',    fontSize=10, fontName='Helvetica',         textColor=BODY_C)
    sScore   = S('sc',     fontSize=10, fontName='Helvetica-Bold',    textColor=INDIGO)

    idea_title  = data.get('idea_title', 'Untitled')
    exported_at = (data.get('exported_at') or '')[:10]
    sc          = data.get('scorecard', {})
    lc          = data.get('lean_canvas') or {}

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN,  bottomMargin=MARGIN)
    story = []

    # ── Header ───────────────────────────────────────────────────
    story.append(Paragraph('Validation Sprint', sMeta))
    story.append(Paragraph(idea_title, sTitle))
    story.append(Paragraph(f'Generated {exported_at} · AI Founding Team', sMeta))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER, spaceBefore=8, spaceAfter=16))

    # ── Lean Canvas (first) ───────────────────────────────────────
    if lc:
        story.append(Paragraph('Lean Canvas', sSection))

        CANVAS_CELLS = [
            ('early_adopter',     'Early Adopter (ICP)',       True),
            ('problem',           'Problem',                   False),
            ('unique_value_prop', 'Unique Value Proposition',  False),
            ('solution',          'Solution',                  False),
            ('channels',          'Channels',                  False),
            ('customer_segments', 'Customer Segments',         False),
            ('revenue_streams',   'Revenue Streams',           False),
            ('cost_structure',    'Cost Structure',            False),
            ('key_metrics',       'Key Metrics',               False),
            ('unfair_advantage',  'Unfair Advantage',          False),
        ]

        col_w = CW / 2
        rows = []
        bg_cmds = []

        for i in range(0, len(CANVAS_CELLS), 2):
            row = []
            for j in range(2):
                if i + j < len(CANVAS_CELLS):
                    key, label, highlight = CANVAS_CELLS[i + j]
                    val = lc.get(key) or '—'
                    cell = [
                        Paragraph(label.upper(), sILabel if highlight else sLabel),
                        Paragraph(val, sIValue if highlight else sValue),
                    ]
                    if highlight:
                        bg_cmds.append(('BACKGROUND', (j, i // 2), (j, i // 2), INDIGO_BG))
                else:
                    cell = [Paragraph('', sLabel)]
                row.append(cell)
            rows.append(row)

        t = Table(rows, colWidths=[col_w, col_w])
        t.setStyle(TableStyle([
            ('BOX',         (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID',   (0, 0), (-1, -1), 0.5, BORDER),
            ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING',  (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING',(0,0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',(0, 0), (-1, -1), 10),
        ] + bg_cmds))
        story.append(t)
        story.append(Spacer(1, 12))

    # ── Scorecard ─────────────────────────────────────────────────
    story.append(Paragraph('Scorecard', sSection))

    verdict   = sc.get('go_no_go', '—')
    overall   = sc.get('overall_score', 0)
    go_cond   = sc.get('go_condition')

    VC = {
        'GO':             ('#DCFCE7', '#15803D'),
        'NO-GO':          ('#FEE2E2', '#B91C1C'),
        'CONDITIONAL GO': ('#FEF9C3', '#78350F'),
    }
    vc_bg, vc_txt = VC.get(verdict, ('#F3F4F6', '#6B7280'))

    sVerdict = S('vv', fontSize=16, fontName='Helvetica-Bold', textColor=HexColor(vc_txt))
    sVScore  = S('vs', fontSize=10, fontName='Helvetica',      textColor=HexColor(vc_txt))
    sVCond   = S('vc', fontSize=9,  fontName='Helvetica-Oblique', textColor=HexColor(vc_txt))

    vrows = [[Paragraph(verdict, sVerdict)], [Paragraph(f'Overall Score: {overall}/10', sVScore)]]
    if go_cond:
        vrows.append([Paragraph(f'Condition: {go_cond}', sVCond)])

    vt = Table(vrows, colWidths=[CW])
    vt.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), HexColor(vc_bg)),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(vt)
    story.append(Spacer(1, 10))

    # Dimension table
    dims = sc.get('dimensions', {})
    # Map stored keys (snake_case) → display names
    DIM_LABELS = {
        'market_size': 'Market Size', 'icp_clarity': 'ICP Clarity',
        'gtm_viability': 'GTM Viability', 'technical_feasibility': 'Technical Feasibility',
        'build_complexity': 'Build Complexity', 'ux_viability': 'UX Viability',
        'user_journey_clarity': 'User Journey Clarity', 'competitive_moat': 'Competitive Moat',
        'revenue_model_strength': 'Revenue Model Strength',
        # also accept title-case keys from scorecard dict
        'Market Size': 'Market Size', 'ICP Clarity': 'ICP Clarity',
        'GTM Viability': 'GTM Viability', 'Technical Feasibility': 'Technical Feasibility',
        'Build Complexity': 'Build Complexity', 'UX Viability': 'UX Viability',
        'User Journey Clarity': 'User Journey Clarity', 'Competitive Moat': 'Competitive Moat',
        'Revenue Model Strength': 'Revenue Model Strength',
    }

    dim_rows = [[Paragraph('DIMENSION', sHdr), Paragraph('SCORE', sHdr)]]
    for key, d in dims.items():
        if d and 'score' in d:
            label = DIM_LABELS.get(key, key)
            dim_rows.append([Paragraph(label, sDim), Paragraph(f"{d['score']}/10", sScore)])

    if len(dim_rows) > 1:
        row_bgs = [
            ('BACKGROUND', (0, r), (-1, r), ROW_ALT if r % 2 == 0 else white)
            for r in range(1, len(dim_rows))
        ]
        dt = Table(dim_rows, colWidths=[CW * 0.78, CW * 0.22])
        dt.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0),  ROW_ALT),
            ('LINEBELOW',     (0, 0), (-1, -2), 0.5, BORDER),
            ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING',    (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN',         (1, 0), (1, -1),  'CENTER'),
        ] + row_bgs))
        story.append(dt)

    # Next actions
    next_actions = sc.get('next_actions', [])
    if next_actions:
        story.append(Paragraph('Next Actions', sSection))
        for i, item in enumerate(next_actions, 1):
            action = item.get('action', '') if isinstance(item, dict) else str(item)
            owner  = item.get('owner', 'PM') if isinstance(item, dict) else 'PM'
            story.append(Paragraph(f'{i}. <b>[{owner}]</b> {action}', sBody))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width='100%', thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f'Validation Sprint · AI Founding Team · {idea_title}', sSmall))

    doc.build(story)
    return buf.getvalue()


# ── Helpers ──────────────────────────────────────────────────── #

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def _scorecard_to_dict(sc: Scorecard) -> dict:
    def dim(d):
        if d is None:
            return {}
        return {"score": d.score, "rationale": d.rationale, "risks": d.risks}

    return {
        "dimensions": {
            "Market Size": dim(sc.market_size),
            "ICP Clarity": dim(sc.icp_clarity),
            "GTM Viability": dim(sc.gtm_viability),
            "Technical Feasibility": dim(sc.technical_feasibility),
            "Build Complexity": dim(sc.build_complexity),
            "UX Viability": dim(sc.ux_viability),
            "User Journey Clarity": dim(sc.user_journey_clarity),
            "Competitive Moat": dim(sc.competitive_moat),
            "Revenue Model Strength": dim(sc.revenue_model_strength),
        },
        "overall_score": sc.overall_score,
        "go_no_go": sc.go_no_go,
        "go_condition": sc.go_condition,
        "next_actions": [
            {"action": a.action, "owner": a.owner} for a in sc.next_actions
        ],
        "debate_rounds_completed": sc.debate_rounds_completed,
        "consensus_reached": sc.consensus_reached,
    }


def _lean_canvas_to_dict(lc: LeanCanvas) -> dict:
    return {
        "problem": lc.problem,
        "customer_segments": lc.customer_segments,
        "early_adopter": lc.early_adopter,
        "unique_value_prop": lc.unique_value_prop,
        "solution": lc.solution,
        "channels": lc.channels,
        "revenue_streams": lc.revenue_streams,
        "cost_structure": lc.cost_structure,
        "key_metrics": lc.key_metrics,
        "unfair_advantage": lc.unfair_advantage,
    }


# ── Entry point ──────────────────────────────────────────────── #

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ERROR: ANTHROPIC_API_KEY is not set. Run: export ANTHROPIC_API_KEY=sk-ant-...")
    print("Starting Validation Sprint UI at http://localhost:5000")
    app.run(debug=False, threaded=True, port=5000)
