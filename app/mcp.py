"""A read-only MCP endpoint, so PI (pi.tigerapps.org) and other MCP clients
can ask what the dining halls are serving.
"""

import json
from datetime import timedelta
from html import unescape
from flask import jsonify, request
from app import app, views
from app.scrape import hallToId

HALLS = list(hallToId.keys())
MEALS = {"breakfast": "breakfastLists", "lunch": "lunchLists", "dinner": "dinnerLists"}

TOOL = {
    "name": "get_menu",
    "description": (
        "Princeton dining hall menus for today or the next six days, by hall, "
        "meal and station. Weekend lunch is brunch. CJL is kosher."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "day": {
                "type": "integer", "minimum": 0, "maximum": 6, "default": 0,
                "description": "Days from today (America/New_York): 0 is today, 1 is tomorrow.",
            },
            "meal": {
                "type": "string", "enum": list(MEALS),
                "description": "One meal only. Leave out for all three.",
            },
            "halls": {
                "type": "array", "items": {"type": "string", "enum": HALLS},
                "description": "Limit to these halls. Leave out for all six.",
            },
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": False},
}


def stations(lines):
    """['Dinner', '-- Main Entree --', 'Posole', ...] -> header + stations."""
    if not lines or lines[0] in ("No Data Available", "Error"):
        return None
    out = []
    # FoodPro double-escapes ("&amp;amp;"), so the scrape still holds "&amp;".
    for line in map(unescape, lines[1:]):
        if line.startswith("-- ") and line.endswith(" --"):
            out.append({"station": line[3:-3], "items": []})
        elif out:
            out[-1]["items"].append(line)
    return {"meal": lines[0], "stations": [s for s in out if s["items"]]}


def get_menu(day=0, meal=None, halls=None):
    day = min(max(int(day), 0), 6)
    meals = [meal] if meal in MEALS else list(MEALS)
    wanted = [h for h in HALLS if not halls or h in halls] or HALLS
    result = []
    for h in wanted:
        i = HALLS.index(h)
        served = [stations(getattr(views, MEALS[m])[day][i]) for m in meals]
        result.append({"hall": h, "meals": [s for s in served if s]})
    date = (views.day + timedelta(days=day)).strftime("%Y-%m-%d")
    return {"date": date, "halls": result}


def reply(msg_id, result=None, error=None):
    body = {"jsonrpc": "2.0", "id": msg_id}
    body.update({"error": error} if error else {"result": result})
    return jsonify(body)


@app.route("/api/mcp", methods=["POST"])
def mcp():
    msg = request.get_json(silent=True) or {}
    method, msg_id = msg.get("method"), msg.get("id")
    if msg_id is None:
        return "", 202
    if method == "initialize":
        return reply(msg_id, {
            "protocolVersion": msg.get("params", {}).get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "tigermenus", "version": "1.0.0"},
        })
    if method == "ping":
        return reply(msg_id, {})
    if method == "tools/list":
        return reply(msg_id, {"tools": [TOOL]})
    if method == "tools/call":
        params = msg.get("params", {})
        if params.get("name") != TOOL["name"]:
            return reply(msg_id, error={"code": -32602, "message": "Unknown tool"})
        args = params.get("arguments") or {}
        data = get_menu(args.get("day", 0), args.get("meal"), args.get("halls"))
        return reply(msg_id, {
            "content": [{"type": "text", "text": json.dumps(data)}],
            "structuredContent": data,
        })
    return reply(msg_id, error={"code": -32601, "message": "Method not found"})


@app.route("/api/mcp", methods=["GET", "DELETE"])
def mcp_no_stream():
    return "", 405
