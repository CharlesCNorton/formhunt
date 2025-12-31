# FormHunt

A geographic selection tool for discovering formalizable content. Select a region on a map; receive coordinates formatted for LLM queries or Mathematica processing.

The premise: point at a place on Earth and ask "what originated here that could be machine-verified?" The selection geometry bounds the results. If evidence for something exists only within your selection, it counts. Regional associations without evidentiary basis do not.

The loss test: if this region were erased from history, would knowledge of the item be lost? If yes, return it.

Output formats:

LLM paste format includes bounding box, center, area, zoom level, and identified place name, followed by a structured prompt asking for formalizable systems, formulas, algorithms, legal codes, or procedures with primary evidence in the selection.

Mathematica format returns a FormHuntQuery expression with GeoRange, GeoPosition, area, and place name suitable for GeoGraphics visualization and distance calculations.

JSON format provides raw coordinates for programmatic use.

UI components: Leaflet or MapBox map with satellite and historical overlay options. Selection tools for rectangle, polygon, circle, or click-to-identify. Zoom classification from Site (<0.01 km²) through Local, Urban, Regional, to National/Continental (50,000+ km²). Copy buttons for each output format. Reverse geocoding for automatic place name population.

No LLM integration initially. The tool formats coordinates; the user pastes to their preferred model.

Future extensions: saved selections, overlay showing regions already formalized in the omnia corpus, difficulty estimates based on available sources.

Author: Charles C. Norton
