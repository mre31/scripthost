from flask import Flask, render_template_string
import os
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerShell Script Library</title>
    <link rel="icon" type="image/png" href="favicon.png">
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
            display: block;
            margin: 10px 0;
            word-wrap: break-word;
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
        #loading {
            text-align: center;
            padding: 20px;
            font-style: italic;
            color: #888;
        }
        .error {
            background: #ff444433;
            padding: 10px;
            border-left: 4px solid #ff4444;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>PowerShell Script Library</h1>
    
    <h2>How to Use</h2>
    <p>To run scripts, use this command in PowerShell:</p>
    <code>irm https://your-site.pages.dev/scripts/[script_name].ps1 | iex</code>
    <p class="description">This command downloads and executes the script directly in your PowerShell session.</p>

    <div class="admin-note">
        <strong>⚠️ Administrator Rights:</strong>
        <p>Some scripts require administrator privileges. To run as administrator:</p>
        <code>Start-Process powershell -Verb RunAs -ArgumentList "-Command irm https://your-site.pages.dev/scripts/[script_name].ps1 | iex"</code>
    </div>

    <h2>Available Scripts</h2>
    <div id="loading">Loading scripts...</div>
    <div id="scripts-container"></div>

    <footer>
        <p class="description">⚠️ Security Note: Always review scripts before execution for security purposes.</p>
        <p class="description">💡 Tip: Use <code>Get-Content</code> to view script contents before execution.</p>
    </footer>

    <script>
        const loadingElement = document.getElementById('loading');
        const container = document.getElementById('scripts-container');
        
        // Statik olarak script listesini tanımlayalım
        const scripts = [
            {% for script in scripts %}
            {
                "name": "{{ script.name }}",
                "requires_admin": {{ 'true' if script.requires_admin else 'false' }}
            }{% if not loop.last %},{% endif %}
            {% endfor %}
        ];

        // Sayfa yüklendiğinde hemen scriptleri göster
        loadingElement.style.display = 'none';
        scripts.forEach(script => {
            const div = document.createElement('div');
            div.className = 'script-item';
            div.innerHTML = `
                <h3>${script.name.replace('.ps1', '')}</h3>
                <p><strong>Execute Command:</strong></p>
                <code>irm ${window.location.origin}/scripts/${script.name} | iex</code>
                ${script.requires_admin ? '<p class="admin-note">⚠️ This script requires administrator privileges</p>' : ''}
            `;
            container.appendChild(div);
        });
    </script>
</body>
</html>
"""

def build_static_site():
    # Create dist directory
    if not os.path.exists('dist'):
        os.makedirs('dist')
    if not os.path.exists('dist/scripts'):
        os.makedirs('dist/scripts')

    # Copy scripts and build scripts list
    scripts = []
    for file in os.listdir('scripts'):
        if file.endswith('.ps1'):
            scripts.append({
                "name": file,
                "requires_admin": False  # Set to True for scripts requiring admin
            })
            with open(f'scripts/{file}', 'r', encoding='utf-8') as src:
                with open(f'dist/scripts/{file}', 'w', encoding='utf-8') as dst:
                    dst.write(src.read())

    # Generate index.html with embedded script data
    from jinja2 import Template
    template = Template(HTML_TEMPLATE)
    html_content = template.render(scripts=scripts)
    
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Copy favicon
    if os.path.exists('favicon.png'):
        with open('favicon.png', 'rb') as src:
            with open('dist/favicon.png', 'wb') as dst:
                dst.write(src.read())

if __name__ == '__main__':
    build_static_site() 