"""
app.py

Flask application serving the current hardcoded automata visualizer pages.

GET /       -> serves index.html
GET /regex  -> serves regex.html
GET /cfg    -> serves cfg.html
"""

from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    """Serve the landing/selection page."""
    return render_template('index.html')


@app.route('/regex')
def regex_page():
    """Serve the Regex -> DFA page."""
    return render_template('regex.html')


@app.route('/cfg')
def cfg_page():
    """Serve the CFG -> PDA page."""
    return render_template('cfg.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
