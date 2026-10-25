"""
Export embedded JS data file to guarantee 100% offline functionality without CORS issues.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
json_file = os.path.join(DASHBOARD_DIR, "dashboard_data.json")
js_file = os.path.join(DASHBOARD_DIR, "data.js")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(js_file, "w", encoding="utf-8") as f:
    f.write("window.EMBEDDED_DASHBOARD_DATA = ")
    json.dump(data, f)
    f.write(";\n")

print(f" -> Successfully exported embedded data to {js_file}")
