#!/usr/bin/env python3
"""
Simple HTTP server to serve the Zoid GPT frontend
"""
import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve static files
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
            return self.serve_static_file('text/html')
        elif self.path.endswith('.js'):
            return self.serve_static_file('text/javascript')
        elif self.path.endswith('.css'):
            return self.serve_static_file('text/css')
        elif self.path.endswith('.json'):
            return self.serve_static_file('application/json')
        elif self.path.endswith('.svg'):
            return self.serve_static_file('image/svg+xml')
        else:
            # Default to serving index.html for SPA routing
            self.path = '/index.html'
            return self.serve_static_file('text/html')

    def serve_static_file(self, content_type):
        try:
            # Map URL paths to actual file paths
            if self.path == '/':
                file_path = 'index.html'
            else:
                file_path = self.path.lstrip('/')
                
            # For build files that don't exist in development, serve index.html
            if not Path(file_path).exists() and '.' in file_path and not file_path.startswith('src/'):
                file_path = 'index.html'
                
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, f"File not found: {file_path}")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        # Handle API proxy requests to the backend
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            self.send_error(404, "API endpoint not found")

    def proxy_to_backend(self):
        # This would proxy requests to the actual backend
        # For now, we'll just return a placeholder
        self.send_error(501, "API proxy not implemented in this simple server")

def run_server(port=3000):
    with socketserver.TCPServer(("", port), FrontendHandler) as httpd:
        print(f"Frontend server running at http://localhost:{port}/")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the server...")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()