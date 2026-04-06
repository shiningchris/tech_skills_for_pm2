import json
import os
import queue
import sys
import threading
import uuid
from dataclasses import asdict

import anthropic
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request

from agents import DesignAgent, MarketerAgent, PMAgent, TechAgent
from config import Config
from models.brief import ProductBrief
from models.scorecard import Scorecard
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
                # Keepalive comment — prevents browser/proxy from closing idle SSE connection
                yield ": keepalive\n\n"
                continue

            total_waited = 0  # reset on activity
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

        # Save exports
        try:
            exporter = Exporter(output_dir=config.OUTPUT_DIR)
            exporter.save_json(scorecard, brief)
            exporter.save_markdown(scorecard, brief, bus)
        except Exception:
            pass  # Export failure shouldn't kill the stream

        q.put({"type": "scorecard", "data": _scorecard_to_dict(scorecard)})
        q.put({"type": "done"})

    except Exception as exc:
        q.put({"type": "error", "message": str(exc)})
        q.put({"type": "done"})


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
        "next_actions": sc.next_actions,
        "debate_rounds_completed": sc.debate_rounds_completed,
        "consensus_reached": sc.consensus_reached,
    }


# ── Entry point ──────────────────────────────────────────────── #

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ERROR: ANTHROPIC_API_KEY is not set. Run: export ANTHROPIC_API_KEY=sk-ant-...")
    print("Starting Validation Sprint UI at http://localhost:5000")
    app.run(debug=False, threaded=True, port=5000)
