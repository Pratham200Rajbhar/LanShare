import http.server
import socketserver
import threading
import functools
import os
import zipfile
import io
import urllib.parse
import json
import gzip
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import mmap


class LANShareRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with JSON API for recursive file listing and zip download."""

    # Class-level cache for directory structures
    _dir_cache = {}
    _cache_lock = threading.Lock()
    _cache_ttl = 60  # Cache for 60 seconds

    def log_message(self, format, *args):
        pass

    def _get_cached_file_list(self, base_dir):
        """Get cached file list or rebuild if expired."""
        with self._cache_lock:
            cache_key = base_dir
            current_time = time.time()
            
            if (cache_key in self._dir_cache and 
                current_time - self._dir_cache[cache_key]['timestamp'] < self._cache_ttl):
                return self._dir_cache[cache_key]['data']
            
            # Rebuild cache
            file_list = self._build_file_list(base_dir)
            self._dir_cache[cache_key] = {
                'data': file_list,
                'timestamp': current_time
            }
            return file_list

    def _build_file_list(self, base_dir):
        """Build optimized file list using pathlib for better performance."""
        file_list = []
        base_path = Path(base_dir)
        
        try:
            # Use pathlib for better performance and error handling
            for file_path in base_path.rglob('*'):
                try:
                    rel_path = file_path.relative_to(base_path)
                    
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        file_list.append({
                            "name": file_path.name,
                            "path": str(rel_path).replace("\\", "/"),
                            "type": "file",
                            "size": size,
                        })
                    elif file_path.is_dir():
                        file_list.append({
                            "name": file_path.name,
                            "path": str(rel_path).replace("\\", "/"),
                            "type": "folder",
                            "size": 0,
                        })
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
                    
        except Exception:
            # Fallback to old method if pathlib fails
            return self._build_file_list_fallback(base_dir)
            
        return file_list

    def _build_file_list_fallback(self, base_dir):
        """Fallback method using os.walk."""
        file_list = []
        
        for root, dirs, files in os.walk(base_dir):
            rel_dir = os.path.relpath(root, base_dir)
            if rel_dir != '.':
                file_list.append({
                    "name": os.path.basename(root),
                    "path": rel_dir.replace("\\", "/"),
                    "type": "folder",
                    "size": 0,
                })

            for fname in files:
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    size = 0

                file_list.append({
                    "name": fname,
                    "path": rel_path,
                    "type": "file",
                    "size": size,
                })
        
        return file_list

    def do_GET(self):
        path = urllib.parse.unquote(self.path)

        if path == '/api/files':
            self._handle_file_list()
        elif path == '/download_all':
            self._handle_download_all()
        elif path.startswith('/download?') or '?file=' in self.path:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            filepath = params.get('file', [''])[0]
            self._handle_download_file(filepath)
        else:
            super().do_GET()

    def _handle_file_list(self):
        """Return JSON list of all files recursively with relative paths and sizes."""
        base_dir = self.directory
        file_list = self._get_cached_file_list(base_dir)

        response_data = json.dumps(file_list, separators=(',', ':')).encode('utf-8')
        
        # Add gzip compression for large file lists with better error handling
        should_compress = len(response_data) > 1024
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        
        if should_compress:
            try:
                compressed_data = gzip.compress(response_data, compresslevel=6)
                # Only set gzip header if compression was successful and actually reduces size
                if len(compressed_data) < len(response_data):
                    response_data = compressed_data
                    self.send_header('Content-Encoding', 'gzip')
            except Exception:
                # If compression fails, send uncompressed data
                pass
            
        self.send_header('Content-Length', str(len(response_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'max-age=30')
        self.end_headers()
        self.wfile.write(response_data)

    def _handle_download_file(self, filepath):
        """Download a specific file by relative path with optimized streaming."""
        base_dir = self.directory
        safe_path = os.path.normpath(filepath)
        if safe_path.startswith('..') or os.path.isabs(safe_path):
            self.send_error(403, "Forbidden")
            return

        full_path = os.path.join(base_dir, safe_path)
        if not os.path.isfile(full_path):
            self.send_error(404, "File not found")
            return

        try:
            file_size = os.path.getsize(full_path)
            filename = os.path.basename(full_path)

            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(file_size))
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()

            # Use memory mapping for large files (>50MB) to reduce memory usage
            if file_size > 50 * 1024 * 1024:
                self._stream_large_file(full_path, file_size)
            else:
                self._stream_file(full_path)
                
        except Exception as e:
            self.send_error(500, str(e))

    def _stream_file(self, file_path):
        """Stream file with optimized chunk size."""
        chunk_size = 1024 * 1024  # 1MB chunks for better performance
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                self.wfile.write(chunk)

    def _stream_large_file(self, file_path, file_size):
        """Stream large files using memory mapping for better memory efficiency."""
        try:
            with open(file_path, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                    chunk_size = 2 * 1024 * 1024  # 2MB chunks for large files
                    offset = 0
                    while offset < file_size:
                        chunk = mmapped_file[offset:offset + chunk_size]
                        self.wfile.write(chunk)
                        offset += chunk_size
        except (ValueError, MemoryError):
            # Fallback to regular streaming if mmap fails
            self._stream_file(file_path)

    def _handle_download_all(self):
        """Download entire directory as zip with streaming for memory efficiency."""
        import tempfile
        import shutil
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/zip')
        self.send_header('Content-Disposition', 'attachment; filename="shared_files.zip"')
        
        # Create temporary file for streaming zip
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            
            try:
                # Create zip file on disk first for better memory usage
                base_dir = self.directory
                root_name = os.path.basename(base_dir.rstrip(os.sep))

                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                    base_path = Path(base_dir)
                    
                    # Use pathlib for better performance
                    for file_path in base_path.rglob('*'):
                        try:
                            if file_path.is_file():
                                rel_path = file_path.relative_to(base_path)
                                arcname = str(Path(root_name) / rel_path)
                                zf.write(str(file_path), arcname)
                            elif file_path.is_dir() and not any(file_path.iterdir()):
                                # Add empty directories
                                rel_path = file_path.relative_to(base_path)
                                arcname = str(Path(root_name) / rel_path) + '/'
                                zf.writestr(arcname, '')
                        except (OSError, PermissionError):
                            continue
                
                # Get file size and send header
                zip_size = os.path.getsize(temp_path)
                self.send_header('Content-Length', str(zip_size))
                self.end_headers()
                
                # Stream the zip file
                chunk_size = 1024 * 1024  # 1MB chunks
                with open(temp_path, 'rb') as zf:
                    while True:
                        chunk = zf.read(chunk_size)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass


class OptimizedThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Optimized threaded server with better performance characteristics."""
    allow_reuse_address = True
    daemon_threads = True
    # Optimize thread pool size based on CPU cores
    request_queue_size = 100
    
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        # Use thread pool executor for better thread management
        self.executor = ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) + 4))
    
    def process_request_thread(self, request, client_address):
        """Process request in thread pool."""
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        except Exception:
            self.handle_error(request, client_address)
            self.shutdown_request(request)
    
    def process_request(self, request, client_address):
        """Submit request to thread pool."""
        self.executor.submit(self.process_request_thread, request, client_address)


class HTTPServerManager:
    def __init__(self, directory, port=8000):
        self.directory = directory
        self.port = port
        self.httpd = None
        self.server_thread = None
        self.is_running = False

    def start_server(self, ip='0.0.0.0'):
        try:
            handler = functools.partial(LANShareRequestHandler, directory=self.directory)
            self.httpd = OptimizedThreadedHTTPServer((ip, self.port), handler)
            self.is_running = True

            self.server_thread = threading.Thread(target=self.httpd.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            return True, f"Server started at {ip}:{self.port}"
        except OSError as e:
            if e.errno == 98:
                return False, f"Port {self.port} is already in use."
            return False, f"Error starting server: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def stop_server(self):
        if self.httpd and self.is_running:
            self.httpd.shutdown()
            self.httpd.server_close()
            # Shutdown thread pool
            if hasattr(self.httpd, 'executor'):
                self.httpd.executor.shutdown(wait=True)
            self.is_running = False
            self.httpd = None
            if self.server_thread:
                self.server_thread.join(timeout=5)
                self.server_thread = None
            return True
        return False

    def clear_cache(self):
        """Clear directory cache to force refresh."""
        with LANShareRequestHandler._cache_lock:
            LANShareRequestHandler._dir_cache.clear()
