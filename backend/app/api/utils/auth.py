"""Authentication utility functions."""

import json
from html import escape


def build_auth_popup_html(title, subtitle, payload, auto_close=True, error_message=None):
    """Build an HTML response for OAuth authentication popup.
    
    Creates an HTML page that displays authentication status and communicates
    the result back to the opener window via postMessage.
    
    Args:
        title (str): The window title and main heading.
        subtitle (str): The subtitle/message text.
        payload (dict): The data to send to the opener window.
        auto_close (bool): Whether to automatically close the window (default: True).
        error_message (str): Optional error message to display.
    
    Returns:
        str: HTML content as a string.
    """
    payload_json = json.dumps(payload)
    safe_subtitle = escape(subtitle)
    safe_error_message = escape(error_message) if error_message else ""
    safe_status_text = (
        "Notificando a la aplicacion principal y cerrando esta ventana..."
        if auto_close
        else "Puede revisar el detalle del error y cerrar esta ventana manualmente."
    )
    actions_display = "none" if auto_close else "flex"
    error_detail_html = (
        f'<div class="error-box"><strong>Detalle:</strong> {safe_error_message}</div>'
        if safe_error_message
        else ""
    )

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{title}</title>
        <style>
            :root {{
                --bg: #f3f7ff;
                --card: #ffffff;
                --text: #0f172a;
                --muted: #475569;
                --ok: #0f766e;
                --error: #b91c1c;
                --btn: #1d4ed8;
                --btn-hover: #1e40af;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                min-height: 100vh;
                display: grid;
                place-items: center;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                background: radial-gradient(circle at 20% 20%, #dbeafe 0%, var(--bg) 60%);
                color: var(--text);
                padding: 20px;
            }}
            .card {{
                width: min(460px, 100%);
                background: var(--card);
                border: 1px solid #dbeafe;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
                padding: 24px;
                text-align: center;
            }}
            .title {{
                margin: 0;
                font-size: 1.25rem;
                font-weight: 700;
            }}
            .subtitle {{
                margin: 10px 0 0;
                color: var(--muted);
                line-height: 1.5;
            }}
            .ok {{ color: var(--ok); }}
            .error {{ color: var(--error); }}
            .hint {{
                margin-top: 14px;
                color: var(--muted);
                font-size: 0.92rem;
            }}
            .actions {{
                margin-top: 18px;
                display: {actions_display};
                justify-content: center;
            }}
            .error-box {{
                margin-top: 14px;
                border: 1px solid #fecaca;
                background: #fef2f2;
                color: #991b1b;
                border-radius: 10px;
                padding: 12px;
                text-align: left;
                font-size: 0.92rem;
            }}
            .close-btn {{
                border: 0;
                border-radius: 10px;
                background: var(--btn);
                color: #fff;
                padding: 10px 18px;
                font-weight: 600;
                cursor: pointer;
            }}
            .close-btn:hover {{ background: var(--btn-hover); }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1 class="title">{title}</h1>
            <p class="subtitle">{safe_subtitle}</p>
            {error_detail_html}
            <p id="status-text" class="hint">{safe_status_text}</p>
            <div id="actions" class="actions">
                <button class="close-btn" onclick="window.close()">Cerrar ventana</button>
            </div>
        </div>
        <script type="text/javascript">
            const messageData = {payload_json};
            try {{
                if (window.opener && !window.opener.closed) {{
                    window.opener.postMessage(messageData, "*");
                }}
            }} catch (error) {{
                console.error("Failed to notify opener window:", error);
            }}

            const autoClose = {str(auto_close).lower()};
            if (autoClose) {{
                window.close();
                setTimeout(() => {{
                    const statusText = document.getElementById("status-text");
                    const actions = document.getElementById("actions");
                    if (statusText) {{
                        statusText.textContent = "Si la ventana no se cierra automaticamente, use el boton de abajo.";
                    }}
                    if (actions) {{
                        actions.style.display = "flex";
                    }}
                }}, 1200);
            }}
        </script>
    </body>
    </html>
    """
