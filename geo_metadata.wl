(* FormHunt Geographic Metadata Query *)
(* Usage: wolframscript -file geo_metadata.wl -- lat lon *)

lat = ToExpression[$ScriptCommandLine[[2]]];
lon = ToExpression[$ScriptCommandLine[[3]]];
pos = GeoPosition[{lat, lon}];

(* Safe extraction helpers *)
safeFirst[list_, default_:None] := If[Length[list] > 0, First[list], default];
safeName[entity_] := If[Head[entity] === Entity, CommonName[entity], Null];
safeNameList[list_] := If[MatchQ[list, {__Entity}], DeleteCases[Map[CommonName, list], $Failed], {}];

(* Quiet all messages and wrap in TimeConstrained *)
result = Quiet[TimeConstrained[
  Module[{country, region, historical},
    country = safeFirst[GeoNearest["Country", pos, 1]];
    region = safeFirst[GeoNearest["AdministrativeDivision", pos, 1]];
    historical = GeoNearest["HistoricalCountry", pos, 5];
    <|
      "country" -> safeName[country],
      "region" -> safeName[region],
      "historicalCountries" -> safeNameList[historical],
      "coordinates" -> {lat, lon}
    |>
  ],
  30, (* 30 second timeout *)
  <|"error" -> "timeout", "coordinates" -> {lat, lon}|>
], All];

(* Handle any remaining failures *)
If[Head[result] =!= Association,
  result = <|"error" -> "query_failed", "coordinates" -> {lat, lon}|>
];

Print[ExportString[result, "JSON"]]
