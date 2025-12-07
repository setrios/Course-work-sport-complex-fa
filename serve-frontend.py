#!/usr/bin/env python
"""
Простий веб-сервер для фронтенду
Запустіть: python serve-frontend.py
Відкрийте: http://127.0.0.1:8001
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
from pathlib import Path

class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP обробник з CORS підтримкою"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        print(f'[{self.log_date_time_string()}] {format % args}')

def main():
    # Переходимо в папку frontend
    frontend_path = Path(__file__).parent / 'frontend'
    os.chdir(frontend_path)
    
    PORT = 8001
    handler = CORSRequestHandler
    server = HTTPServer(('127.0.0.1', PORT), handler)
    
    print('✨ ФРОНТЕНД ВЕБ-СЕРВЕР')
    print('=' * 50)
    print(f'🌐 URL: http://127.0.0.1:{PORT}')
    print(f'📁 Папка: {frontend_path}')
    print('=' * 50)
    print('⌨️  Натисніть Ctrl+C для зупинки')
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n✅ Сервер зупинений')
        sys.exit(0)

if __name__ == '__main__':
    main()
