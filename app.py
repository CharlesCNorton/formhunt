"""
FormHunt: Geographic coordinate capture for formalizable content discovery.
"""

from flask import Flask, render_template, jsonify, request
from pathlib import Path
import subprocess
import json
import shutil

app = Flask(__name__, static_folder='static', template_folder='templates')

# Find wolframscript
WOLFRAM_PATHS = [
    r"C:\Program Files\Wolfram Research\WolframScript\wolframscript.exe",
    r"C:\Program Files\Wolfram Research\Mathematica\14.0\wolframscript.exe",
    "wolframscript",  # If in PATH
]

def find_wolframscript():
    """Find wolframscript executable, return None if not found."""
    for path in WOLFRAM_PATHS:
        if Path(path).exists() or shutil.which(path):
            return path
    return None

WOLFRAMSCRIPT = find_wolframscript()


def query_wolfram_metadata(lat: float, lon: float) -> dict:
    """Query Wolfram for rich geographic metadata. Returns empty dict on failure."""
    if not WOLFRAMSCRIPT:
        return {}

    code = f'''
pos = GeoPosition[{{{lat}, {lon}}}];
safeNames[list_] := Select[Map[CommonName, list], StringQ];
divisions = GeoNearest["AdministrativeDivision", pos, 6];
(* Filter to get county-level, not state/country level *)
counties = Select[divisions, StringCount[CommonName[#], ","] >= 2 &];
ExportString[<|
  "divisions" -> Take[safeNames[counties], UpTo[4]],
  "lakes" -> safeNames[GeoNearest["Lake", pos, 4]],
  "islands" -> safeNames[GeoNearest["Island", pos, 4]],
  "mountains" -> safeNames[GeoNearest["Mountain", pos, 3]],
  "cities" -> safeNames[GeoNearest["City", pos, 5]],
  "historicalSites" -> safeNames[GeoNearest["HistoricalSite", pos, 6]],
  "waterfalls" -> safeNames[GeoNearest["Waterfall", pos, 3]],
  "buildings" -> safeNames[GeoNearest["Building", pos, 4]]
|>, "JSON"]
'''

    try:
        result = subprocess.run(
            [WOLFRAMSCRIPT, "-code", code],
            capture_output=True,
            text=True,
            timeout=90
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout.strip())
            # Filter out empty lists
            return {k: v for k, v in data.items() if v}
    except Exception as e:
        print(f"Wolfram error: {e}")

    return {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/wolfram-metadata', methods=['POST'])
def wolfram_metadata():
    """Query Wolfram for geographic metadata."""
    data = request.json
    lat = data.get('lat', 0)
    lon = data.get('lon', 0)

    metadata = query_wolfram_metadata(lat, lon)
    return jsonify(metadata)


@app.route('/api/wolfram-status')
def wolfram_status():
    """Check if Wolfram is available."""
    return jsonify({"available": WOLFRAMSCRIPT is not None})


if __name__ == '__main__':
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    print(f"FormHunt running at http://localhost:5000")
    print(f"Wolfram: {'Available' if WOLFRAMSCRIPT else 'Not found (metadata disabled)'}")
    app.run(debug=True, port=5000)
