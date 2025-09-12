import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from optimizer import run_optimization

# Build a reliable, absolute path to the 'Dashboard' folder.
# This correctly matches the case-sensitive folder name.
DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Dashboard')

# Initialize Flask, telling it where to find the static files (HTML, CSS, JS)
app = Flask(__name__, static_folder=DASHBOARD_DIR)
CORS(app)

# This route serves your index.html file as the homepage
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# This route serves other files (like CSS and JS) from the dashboard folder
@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# API endpoint for the optimizer
@app.route('/api/optimize', methods=['GET'])
def optimize_schedule():
    print("Received API request to optimize schedule...")
    optimized_df = run_optimization()
    if optimized_df is not None:
        result_json = optimized_df.to_json(orient='records')
        return result_json
    else:
        return jsonify({"error": "Could not find an optimal solution."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)