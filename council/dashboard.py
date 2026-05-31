"""Live dashboard for Research Council - web UI for monitoring queries."""

import json
import logging
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict

from council.config import DASHBOARD_HOST, DASHBOARD_PORT, REFRESH_INTERVAL_MS
from council.state import get_state

logger = logging.getLogger(__name__)


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for dashboard endpoints."""

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/":
            self._serve_html()
        elif self.path == "/api/state":
            self._serve_state_json()
        elif self.path == "/api/stats":
            self._serve_stats_json()
        else:
            self._send_404()

    def _serve_html(self) -> None:
        """Serve main dashboard HTML page."""
        html = self._generate_dashboard_html()
        self._send_response(200, html, "text/html")

    def _serve_state_json(self) -> None:
        """Serve current state as JSON."""
        state = get_state()
        recent = state.get_recent(10)

        data = {
            "active_count": state.get_active_count(),
            "recent": [
                {
                    "id": item.id,
                    "query": item.query,
                    "timestamp": item.timestamp.isoformat(),
                    "status": item.status,
                    "models_used": item.models_used,
                    "has_results": bool(item.results),
                    "error": item.error,
                }
                for item in recent
            ],
        }

        self._send_response(200, json.dumps(data), "application/json")

    def _serve_stats_json(self) -> None:
        """Serve statistics as JSON."""
        state = get_state()
        stats = state.get_stats()
        self._send_response(200, json.dumps(stats), "application/json")

    def _send_response(self, status: int, content: str, content_type: str) -> None:
        """Send HTTP response."""
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def _send_404(self) -> None:
        """Send 404 response."""
        self._send_response(404, "Not Found", "text/plain")

    def log_message(self, format: str, *args) -> None:
        """Override to use proper logging instead of stderr."""
        logger.debug(f"Dashboard request: {format % args}")

    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML with embedded JavaScript."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Council Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f1419;
            color: #e6e6e6;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
            color: #fff;
        }}
        .subtitle {{
            color: #8b949e;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
        }}
        .stat-label {{
            color: #8b949e;
            font-size: 0.875rem;
            margin-bottom: 8px;
        }}
        .stat-value {{
            color: #fff;
            font-size: 2rem;
            font-weight: 600;
        }}
        .section {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .section-title {{
            font-size: 1.25rem;
            margin-bottom: 15px;
            color: #fff;
        }}
        .query-item {{
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 10px;
        }}
        .query-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .query-text {{
            color: #58a6ff;
            font-weight: 500;
        }}
        .status {{
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status-pending {{ background: #58a6ff; color: #000; }}
        .status-in_progress {{ background: #f0883e; color: #000; }}
        .status-completed {{ background: #3fb950; color: #000; }}
        .status-failed {{ background: #f85149; color: #fff; }}
        .query-meta {{
            color: #8b949e;
            font-size: 0.875rem;
        }}
        .models {{
            display: flex;
            gap: 5px;
            margin-top: 8px;
        }}
        .model-badge {{
            background: #30363d;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.75rem;
            color: #c9d1d9;
        }}
        .error {{
            color: #f85149;
            margin-top: 8px;
            font-size: 0.875rem;
        }}
        .refresh-indicator {{
            color: #8b949e;
            font-size: 0.875rem;
        }}
        .empty-state {{
            color: #8b949e;
            text-align: center;
            padding: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Research Council Dashboard</h1>
        <p class="subtitle">
            Live monitoring of multi-model research queries
            <span class="refresh-indicator" id="refresh-time">Loading...</span>
        </p>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Active Queries</div>
                <div class="stat-value" id="active-count">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Queries</div>
                <div class="stat-value" id="total-queries">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Successful</div>
                <div class="stat-value" id="successful-queries">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Failed</div>
                <div class="stat-value" id="failed-queries">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Model Calls</div>
                <div class="stat-value" id="total-model-calls">-</div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Recent Queries</h2>
            <div id="recent-queries">
                <div class="empty-state">Loading queries...</div>
            </div>
        </div>
    </div>

    <script>
        const REFRESH_INTERVAL = {REFRESH_INTERVAL_MS};

        async function fetchData(endpoint) {{
            const response = await fetch(endpoint);
            return response.json();
        }}

        function formatTimestamp(isoString) {{
            const date = new Date(isoString);
            const now = new Date();
            const diff = Math.floor((now - date) / 1000);

            if (diff < 60) return `${{diff}}s ago`;
            if (diff < 3600) return `${{Math.floor(diff / 60)}}m ago`;
            if (diff < 86400) return `${{Math.floor(diff / 3600)}}h ago`;
            return date.toLocaleDateString();
        }}

        function renderQueries(data) {{
            const container = document.getElementById('recent-queries');

            if (!data.recent || data.recent.length === 0) {{
                container.innerHTML = '<div class="empty-state">No queries yet</div>';
                return;
            }}

            container.innerHTML = data.recent.map(item => `
                <div class="query-item">
                    <div class="query-header">
                        <div class="query-text">${{escapeHtml(item.query)}}</div>
                        <span class="status status-${{item.status}}">${{item.status}}</span>
                    </div>
                    <div class="query-meta">
                        ${{formatTimestamp(item.timestamp)}} · ID: ${{item.id.slice(0, 8)}}
                    </div>
                    <div class="models">
                        ${{item.models_used.map(m => `<span class="model-badge">${{m}}</span>`).join('')}}
                    </div>
                    ${{item.error ? `<div class="error">Error: ${{escapeHtml(item.error)}}</div>` : ''}}
                </div>
            `).join('');
        }}

        function renderStats(stats) {{
            document.getElementById('total-queries').textContent = stats.total_queries;
            document.getElementById('successful-queries').textContent = stats.successful_queries;
            document.getElementById('failed-queries').textContent = stats.failed_queries;
            document.getElementById('total-model-calls').textContent = stats.total_model_calls;
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        async function refresh() {{
            try {{
                const [state, stats] = await Promise.all([
                    fetchData('/api/state'),
                    fetchData('/api/stats')
                ]);

                document.getElementById('active-count').textContent = state.active_count;
                renderQueries(state);
                renderStats(stats);

                const now = new Date().toLocaleTimeString();
                document.getElementById('refresh-time').textContent = `Last updated: ${{now}}`;
            }} catch (error) {{
                console.error('Refresh failed:', error);
            }}
        }}

        // Initial load and periodic refresh
        refresh();
        setInterval(refresh, REFRESH_INTERVAL);
    </script>
</body>
</html>"""


class Dashboard:
    """Research Council live dashboard server."""

    def __init__(self, host: str = DASHBOARD_HOST, port: int = DASHBOARD_PORT):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None

    def start(self, blocking: bool = True) -> None:
        """
        Start dashboard server.

        Args:
            blocking: If True, blocks until server stops. If False, returns immediately.
        """
        self.server = HTTPServer((self.host, self.port), DashboardHandler)
        logger.info(f"Dashboard server starting on http://{self.host}:{self.port}")

        try:
            if blocking:
                self.server.serve_forever()
            else:
                # In production, would use threading or asyncio for non-blocking
                import threading

                thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                thread.start()
                logger.info("Dashboard server running in background thread")
        except KeyboardInterrupt:
            logger.info("Dashboard server stopping...")
            self.stop()

    def stop(self) -> None:
        """Stop dashboard server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Dashboard server stopped")


def create_dashboard() -> Dashboard:
    """Factory function to create configured dashboard."""
    return Dashboard()


def main() -> None:
    """Run dashboard as standalone application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    dashboard = create_dashboard()
    print(f"Starting Research Council Dashboard on http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    print("Press Ctrl+C to stop")
    dashboard.start()


if __name__ == "__main__":
    main()
