# TO RUN: flask --app ./flask_app/app.py run --debug
from flask import Flask, render_template, request, jsonify
from logic.main import run
from cancel_event import cancel_event
from logic.autocomplete import wikipedia_autocomplete

app = Flask(__name__)

@app.route("/cancel", methods=["POST"])
def cancel():
    """
    Set the global cancel flag to abort an in-progress search.

    @return tuple: Empty response with HTTP 204.
    """
    cancel_event.set()
    return "", 204
    

@app.route("/autocomplete")
def autocomplete():
    """
    Return Wikipedia autocomplete suggestions for a query.

    @param q (query param): partial query string.
    @return JSON: list of suggested page titles (possibly empty on error).
    """
    query = request.args.get("q", "")

    if not query:
        return jsonify([])

    try:
        return jsonify(wikipedia_autocomplete(query, k=5))
    except Exception:
        return jsonify([])

@app.route("/run", methods=["POST"])
def run_search():
    """
    Run a configured search.

    @param k (form): beam width.
    @param time_limit (form): max time in seconds.
    @param max_depth (form): maximum depth allowed.
    @param start (form): start page title.
    @param end (form): end page title.
    @return JSON: status and results or error message.
    """
    cancel_event.clear()

    k = int(request.form["k"])
    time_limit = int(request.form["time_limit"])
    max_depth = int(request.form["max_depth"])
    start = request.form["start"]
    end = request.form["end"]

    result = run(start, end, k, time_limit, max_depth)

    error_map = {
        "START_NOT_FOUND": "Start Wikipedia page does not exist.",
        "END_NOT_FOUND": "End Wikipedia page does not exist.",
        "NO_PATH_FOUND": "No path found within the given limits."
    }

    if result["status"] != "OK":
        return jsonify({
            "status": "ERROR",
            "message": error_map[result["status"]]
        })

    return jsonify({
        "status": "OK",
        "links": result["links"],
        "elapsed_time": result["elapsed_time"]
    })

@app.route("/", methods=["GET"])
def home():
    """
    Render the home UI.

    @return Rendered template home.html.
    """
    return render_template("home.html")

@app.route("/blog")
def blog():
    """
    Render the blog/notes page.

    @return Rendered template blog.html.
    """
    return render_template('blog.html')