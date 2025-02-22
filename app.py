from flask import Flask, send_from_directory, render_template_string, url_for
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerShell Script Library</title>
    <link rel="icon" type="image/png" href="{{ url_for('favicon') }}">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background: #1a1a1a;
            color: #e0e0e0;
        }
        .script-item {
            background: #2d2d2d;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #404040;
        }
        code {
            background: #363636;
            padding: 2px 5px;
            border-radius: 3px;
            color: #00ff00;
            font-family: 'Consolas', monospace;
        }
        .description {
            color: #888;
            font-size: 0.9em;
            margin: 5px 0;
        }
        .admin-note {
            background: #3d2c2c;
            border-left: 4px solid #ff4444;
            padding: 10px;
            margin: 10px 0;
        }
        h1, h2, h3 {
            color: #ffffff;
        }
        a {
            color: #5c9eff;
        }
        footer {
            margin-top: 40px;
            border-top: 1px solid #404040;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <h1>PowerShell Script Library</h1>
    
    <h2>How to Use</h2>
    <p>To run scripts, use this command in PowerShell:</p>
    <code>irm http://{{ request.host }}/[script_name] | iex</code>
    <p class="description">This command downloads and executes the script directly in your PowerShell session.</p>

    <div class="admin-note">
        <strong>⚠️ Administrator Rights:</strong>
        <p>Some scripts require administrator privileges. To run as administrator:</p>
        <code>Start-Process powershell -Verb RunAs -ArgumentList "-Command irm http://{{ request.host }}/[script_name] | iex"</code>
    </div>

    <h2>Available Scripts</h2>
    {% for script in scripts %}
    <div class="script-item">
        <h3>{{ script.name.replace('.ps1', '') }}</h3>
        <p><strong>Execute Command:</strong></p>
        <code>irm http://{{ request.host }}/{{ script.name.replace('.ps1', '') }} | iex</code>
        {% if script.requires_admin %}
        <p class="admin-note">⚠️ This script requires administrator privileges</p>
        {% endif %}
    </div>
    {% endfor %}

    <footer>
        <p class="description">⚠️ Security Note: Always review scripts before execution for security purposes.</p>
        <p class="description">💡 Tip: Use <code>Get-Content</code> to view script contents before execution.</p>
    </footer>
</body>
</html>
"""

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.png', mimetype='image/png')

@app.route('/')
def index():
    scripts = []
    for file in os.listdir('scripts'):
        if file.endswith('.ps1'):
            # You can set requires_admin=True for scripts that need admin rights
            scripts.append({
                "name": file,
                "requires_admin": False  # Set to True for scripts requiring admin
            })
    return render_template_string(HTML_TEMPLATE, scripts=scripts)

@app.route('/<path:filename>')
def serve_script(filename):
    if not filename.endswith('.ps1'):
        filename = filename + '.ps1'
    return send_from_directory('scripts', filename), 200, {
        'Content-Type': 'text/plain; charset=utf-8'
    }

if __name__ == '__main__':
    if not os.path.exists('scripts'):
        os.makedirs('scripts')
    app.run(host='0.0.0.0', port=5001) 