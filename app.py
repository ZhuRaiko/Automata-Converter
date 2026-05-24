"""
app.py

Flask application serving the Regex (Thompson -> NFA -> DFA) and CFG -> PDA
pipelines as JSON APIs and a small set of HTML pages. The Flask app exposes the
following endpoints (all JSON POSTs return JSON responses):

POST /api/regex/nfa        -> compiles regex to NFA (uses algorithms.thompson)
POST /api/regex/dfa        -> converts NFA dict to DFA (uses algorithms.subset_construction)
POST /api/regex/check      -> runs DFA checker on a test string
POST /api/regex/nfa/check  -> runs NFA simulator on a test string (per-step active set)
POST /api/cfg/pda          -> converts CFG text to PDA (uses algorithms.cfg_to_pda)
POST /api/cfg/check        -> runs PDA simulation on a test string

GET /       -> serves index.html
GET /regex   -> serves regex.html
GET /cfg     -> serves cfg.html

The file contains detailed docstrings for each route and basic error handling.
"""

from flask import Flask, request, jsonify, render_template

# Import algorithm modules from the algorithms package
import algorithms.thompson as thompson
import algorithms.subset_construction as subset
import algorithms.string_checker_dfa as checker_dfa
import algorithms.string_checker_nfa as checker_nfa
import algorithms.cfg_to_pda as cfg_to_pda
import algorithms.string_checker_pda as checker_pda

app = Flask(__name__)


# ------------------------- Regex endpoints ------------------------- #

@app.route('/api/regex/nfa', methods=['POST'])
def api_regex_nfa():
    """Compile a regular expression into an NFA and return the JSON dict.

    Expects JSON body: { "regex": "(a|b)*abb" }
    Returns: nfa dict produced by `thompson.nfa_to_dict`.
    """
    data = request.get_json(force=True)
    regex = data.get('regex', '') if data else ''
    try:
        nfa_obj = thompson.compile_regex(regex)
        return jsonify(thompson.nfa_to_dict(nfa_obj))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/regex/dfa', methods=['POST'])
def api_regex_dfa():
    """Convert an NFA (JSON) to a DFA JSON dict.

    Expects JSON body: { "nfa": <nfa-dict> }
    Returns: DFA dict as produced by `subset.convert_nfa_to_dfa`.
    """
    data = request.get_json(force=True)
    nfa = data.get('nfa') if data else None
    if not nfa:
        return jsonify({"error": "Missing 'nfa' in request body"}), 400
    try:
        dfa = subset.convert_nfa_to_dfa(nfa)
        return jsonify(dfa)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/regex/check', methods=['POST'])
def api_regex_check():
    """Check whether a given string is accepted by the provided DFA.

    Expects JSON body: { "dfa": <dfa-dict>, "string": "aabb" }
    Returns: { "valid": True/False, "path": [state ids] }
    """
    data = request.get_json(force=True)
    dfa = data.get('dfa') if data else None
    s = data.get('string', '') if data else ''
    if not dfa:
        return jsonify({"error": "Missing 'dfa' in request body"}), 400
    try:
        result = checker_dfa.run_dfa_checker(dfa, s)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/regex/nfa/check', methods=['POST'])
def api_regex_nfa_check():
    """Simulate the NFA on a test string and return per-step active-set traces.

    Expects JSON body: { "nfa": <nfa-dict>, "string": "aabb" }
    Returns: { "valid": True/False, "steps": [ {states, char, edges}, ... ] }
    """
    data = request.get_json(force=True)
    nfa = data.get('nfa') if data else None
    s = data.get('string', '') if data else ''
    if not nfa:
        return jsonify({"error": "Missing 'nfa' in request body"}), 400
    try:
        return jsonify(checker_nfa.run_nfa_checker(nfa, s))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ------------------------- CFG / PDA endpoints ------------------------- #

@app.route('/api/cfg/pda', methods=['POST'])
def api_cfg_pda():
    """Convert CFG text into a PDA dict used by the frontend.

    Expects JSON body: { "cfg": "S -> aSb | ε\n" }
    Returns: PDA dict from `cfg_to_pda.convert_cfg_to_pda`.
    """
    data = request.get_json(force=True)
    cfg_text = data.get('cfg', '') if data else ''
    if cfg_text is None:
        return jsonify({"error": "Missing 'cfg' in request body"}), 400
    try:
        pda = cfg_to_pda.convert_cfg_to_pda(cfg_text)
        return jsonify(pda)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/cfg/check', methods=['POST'])
def api_cfg_check():
    """Run the PDA simulation on the test string and return the step trace.

    Expects JSON body: { "pda": <pda-dict>, "string": "aabb" }
    Returns: { "valid": True/False, "steps": [ {state, remaining_input, stack}, ... ] }
    """
    data = request.get_json(force=True)
    pda = data.get('pda') if data else None
    s = data.get('string', '') if data else ''
    if not pda:
        return jsonify({"error": "Missing 'pda' in request body"}), 400
    try:
        result = checker_pda.run_pda_simulation(pda, s)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ------------------------- Page routes ------------------------- #

@app.route('/')
def index():
    """Serve the landing/selection page."""
    return render_template('index.html')


@app.route('/regex')
def regex_page():
    """Serve the Regex -> NFA/DFA page."""
    return render_template('regex.html')


@app.route('/cfg')
def cfg_page():
    """Serve the CFG -> PDA page."""
    return render_template('cfg.html')


if __name__ == '__main__':
    # Start the Flask development server. For the school project this is
    # sufficient; in production a WSGI server should be used instead.
    app.run(host='127.0.0.1', port=5000, debug=True)
