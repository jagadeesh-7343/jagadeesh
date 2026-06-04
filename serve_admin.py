"""
Simple HTTP server to serve admin panel files
This solves CORS issues with Ollama API calls
"""
import http.server
import socketserver
import os

# Change to the directory containing the HTML files
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

Handler = MyHTTPRequestHandler

print(f"""
╔════════════════════════════════════════════════════════╗
║          Citizen Bridge Admin Server                  ║
╚════════════════════════════════════════════════════════╝

✅ Server running at: http://localhost:{PORT}

📋 Access admin panels:
   • Education:   http://localhost:{PORT}/admin_education.html
   • Electrical:  http://localhost:{PORT}/admin_electrical.html
   • Health:      http://localhost:{PORT}/admin_health.html
   • Police:      http://localhost:{PORT}/admin_police.html
   • Transport:   http://localhost:{PORT}/admin_transport.html
   
   • Main Login:  http://localhost:{PORT}/register.html

🛑 Press Ctrl+C to stop the server
""")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped.")
