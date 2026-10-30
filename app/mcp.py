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
    """['Dinner', '-- Main Entree --', 'Posole', ...] -> header + stations.
    None when the hall posted no menu; scrapeHall's ['Error'] never gets here."""
    if not lines or lines[0] == "No Data Available":
        return None
    out = []
    # FoodPro double-escapes ("&amp;amp;"), so the scrape still holds "&amp;".
    for line in map(unescape, lines[1:]):
        if line.startswith("-- ") and line.endswith(" --"):
            out.append({"station": line[3:-3], "items": []})
        elif out:
            out[-1]["items"].append(line)
    return {"meal": lines[0], "stations": [s for s in out if s["items"]]}


def check_args(args):
    """The reason args are invalid, or None. Nothing is coerced or clamped."""
    if not isinstance(args, dict):
        return "arguments must be an object"
    unknown = set(args) - set(TOOL["inputSchema"]["properties"])
    if unknown:
        return f"unknown argument(s): {', '.join(sorted(unknown))}"
    day = args.get("day", 0)
    if type(day) is not int or not 0 <= day <= 6:
        return "day must be an integer from 0 (today) to 6"
    if "meal" in args and (not isinstance(args["meal"], str) or args["meal"] not in MEALS):
        return f"meal must be one of: {', '.join(MEALS)}"
    halls = args.get("halls", [])
    if not isinstance(halls, list) or any(h not in HALLS for h in halls):
        return f"halls must be a list drawn from: {', '.join(HALLS)}"
    return None


def get_menu(day=0, meal=None, halls=None):
    meals = [meal] if meal else list(MEALS)
    result = []
    for h in [h for h in HALLS if h in halls] if halls else HALLS:
        i = HALLS.index(h)
        lines = [getattr(views, MEALS[m])[day][i] for m in meals]
        if any(l == ["Error"] for l in lines):
            result.append({"hall": h, "error": "Couldn't fetch this hall's menu from Campus Dining."})
            continue
        served = [stations(l) for l in lines]
        result.append({"hall": h, "meals": [s for s in served if s]})
    date = (views.day + timedelta(days=day)).strftime("%Y-%m-%d")
    return {"date": date, "halls": result}


def tool_result(data, is_error=False):
    text = data if isinstance(data, str) else json.dumps(data)
    result = {"content": [{"type": "text", "text": text}], "isError": is_error}
    if not isinstance(data, str):
        result["structuredContent"] = data
    return result


def reply(msg_id, result=None, error=None):
    body = {"jsonrpc": "2.0", "id": msg_id}
    body.update({"error": error} if error else {"result": result})
    return jsonify(body)


@app.route("/api/mcp", methods=["POST"])
def mcp():
    msg = request.get_json(silent=True)
    if not isinstance(msg, dict):
        return reply(None, error={"code": -32600, "message": "Expected one JSON-RPC object"})
    method, msg_id = msg.get("method"), msg.get("id")
    if msg_id is None:
        return "", 202
    if method == "initialize":
        return reply(msg_id, {
            "protocolVersion": (msg.get("params") or {}).get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "tigermenus", "version": "1.0.0"},
        })
    if method == "ping":
        return reply(msg_id, {})
    if method == "tools/list":
        return reply(msg_id, {"tools": [TOOL]})
    if method == "tools/call":
        params = msg.get("params")
        params = params if isinstance(params, dict) else {}
        if params.get("name") != TOOL["name"]:
            return reply(msg_id, error={"code": -32602, "message": "Unknown tool"})
        args = params.get("arguments")
        args = {} if args is None else args
        problem = check_args(args)
        if problem:
            return reply(msg_id, tool_result(f"Invalid arguments: {problem}", True))
        data = get_menu(args.get("day", 0), args.get("meal"), args.get("halls"))
        failed = any("error" in h for h in data["halls"])
        return reply(msg_id, tool_result(data, failed))
    return reply(msg_id, error={"code": -32601, "message": "Method not found"})


@app.route("/api/mcp", methods=["GET", "DELETE"])
def mcp_no_stream():
    return "", 405
