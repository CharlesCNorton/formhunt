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
safeQuery[type_, n_] := Quiet[Check[GeoNearest[type, pos, n], {{}}]];
divisions = safeQuery["AdministrativeDivision", 6];
counties = Select[divisions, StringCount[CommonName[#], ","] >= 2 &];
ExportString[<|
  "divisions" -> Take[safeNames[counties], UpTo[4]],
  "cities" -> safeNames[safeQuery["City", 5]],
  "lakes" -> safeNames[safeQuery["Lake", 4]],
  "islands" -> safeNames[safeQuery["Island", 4]],
  "mountains" -> safeNames[safeQuery["Mountain", 3]],
  "forests" -> safeNames[safeQuery["Forest", 3]],
  "parks" -> safeNames[safeQuery["Park", 4]],
  "beaches" -> safeNames[safeQuery["Beach", 3]],
  "caves" -> safeNames[safeQuery["Cave", 3]],
  "glaciers" -> safeNames[safeQuery["Glacier", 3]],
  "volcanoes" -> safeNames[safeQuery["Volcano", 3]],
  "historicalSites" -> safeNames[safeQuery["HistoricalSite", 6]],
  "museums" -> safeNames[safeQuery["Museum", 4]],
  "universities" -> safeNames[safeQuery["University", 3]],
  "militaryBases" -> safeNames[safeQuery["MilitaryBase", 3]],
  "shipwrecks" -> safeNames[safeQuery["Shipwreck", 5]],
  "bridges" -> safeNames[safeQuery["Bridge", 4]],
  "dams" -> safeNames[safeQuery["Dam", 4]],
  "mines" -> safeNames[safeQuery["Mine", 3]],
  "tunnels" -> safeNames[safeQuery["Tunnel", 3]],
  "airports" -> safeNames[safeQuery["Airport", 3]],
  "waterfalls" -> safeNames[safeQuery["Waterfall", 3]],
  "buildings" -> safeNames[safeQuery["Building", 4]],
  "cemeteries" -> safeNames[safeQuery["Cemetery", 3]]
|>, "JSON"]
'''

    try:
        result = subprocess.run(
            [WOLFRAMSCRIPT, "-code", code],
            capture_output=True,
            text=True,
            timeout=120
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
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        lat = data.get('lat')
        lon = data.get('lon')

        if lat is None or lon is None:
            return jsonify({"error": "Missing lat/lon"}), 400

        # Validate coordinate ranges
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({"error": "Invalid coordinates"}), 400

        metadata = query_wolfram_metadata(float(lat), float(lon))
        return jsonify(metadata)

    except Exception as e:
        print(f"API error: {e}")
        return jsonify({"error": "Internal server error"}), 500


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
