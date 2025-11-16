from flask import Blueprint, redirect, current_app, request
from urllib.parse import urlparse

visor_bp = Blueprint("visor", __name__)

# Example mapping: dashboard ID → Power BI URL test


@visor_bp.route("/visor/<int:dashboard_id>/", methods=["GET"])
def visor_index(dashboard_id):
    """
    Serve a page that loads Power BI in a hidden way
    """
    DASHBOARDS = {
        1: current_app.config.get("TEST_BI_DASHBOARD"),
    }
    
    dashboard_url = DASHBOARDS.get(dashboard_id)
    if not dashboard_url:
        return f"Dashboard {dashboard_id} not found in {DASHBOARDS}", 404

    # Create a double iframe structure
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard</title>
        <style>
            body, html {{
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
            }}
            #outerFrame {{
                width: 100%;
                height: 100vh;
                border: none;
            }}
            #hiddenLoader {{
                display: none;
            }}
        </style>
    </head>
    <body>
        <!-- This iframe shows your content -->
        <iframe id="outerFrame" src="about:blank"></iframe>
        
        <!-- Hidden iframe that actually loads Power BI -->
        <iframe id="hiddenLoader" src="{dashboard_url}"></iframe>
        
        <script>
            // When the hidden iframe loads, copy its content to the visible iframe
            document.getElementById('hiddenLoader').onload = function() {{
                const hiddenFrame = document.getElementById('hiddenLoader');
                const visibleFrame = document.getElementById('outerFrame');
                
                try {{
                    visibleFrame.srcdoc = hiddenFrame.contentDocument.documentElement.outerHTML;
                }} catch (e) {{
                    // Fallback: redirect the visible frame
                    visibleFrame.src = "{dashboard_url}";
                }}
            }};
        </script>
    </body>
    </html>
    """
    
    return html