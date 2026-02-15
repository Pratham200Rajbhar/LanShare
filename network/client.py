import requests
import os
import urllib.parse
import json
import gzip
import concurrent.futures
import threading
from pathlib import Path


class HTTPClient:
    def __init__(self, max_connections=10):
        self.session = requests.Session()
        # Optimize session for performance
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=max_connections,
            pool_maxsize=max_connections,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Set optimized headers
        self.session.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'User-Agent': 'LANShare/2.0 (Optimized)'
        })

    def list_files(self, ip, port):
        """Fetch structured file list from server JSON API with compression support."""
        url = f"http://{ip}:{port}/api/files"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Handle compressed responses
            if response.headers.get('content-encoding') == 'gzip':
                content = gzip.decompress(response.content)
                file_list = json.loads(content.decode('utf-8'))
            else:
                file_list = response.json()
                
            return True, file_list
        except requests.exceptions.Timeout:
            return False, "Connection timed out. Check IP and Port."
        except requests.exceptions.ConnectionError:
            return False, "Failed to connect. Is the server running?"
        except json.JSONDecodeError:
            return False, "Invalid response format from server."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def download_file(self, ip, port, file_path, save_path, progress_callback=None, resume=True):
        """Download a file with resume support and optimized performance."""
        url = f"http://{ip}:{port}/download?file={urllib.parse.quote(file_path)}"
        
        try:
            # Create parent directories if needed
            parent_dir = Path(save_path).parent
            parent_dir.mkdir(parents=True, exist_ok=True)

            # Check if partial file exists for resume
            resume_pos = 0
            if resume and os.path.exists(save_path):
                resume_pos = os.path.getsize(save_path)
                headers = {'Range': f'bytes={resume_pos}-'}
            else:
                headers = {}

            response = self.session.get(url, stream=True, timeout=30, headers=headers)
            
            # Handle range requests
            if response.status_code == 206:  # Partial content
                mode = 'ab'
            elif response.status_code == 200:
                mode = 'wb'
                resume_pos = 0
            else:
                response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0)) + resume_pos
            chunk_size = 1024 * 1024  # 1MB chunks for better performance
            downloaded = resume_pos

            with open(save_path, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            return True, "Download complete!"
            
        except Exception as e:
            # Only remove file if we were starting fresh (not resuming)
            if not resume and os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except:
                    pass
            return False, f"Download failed: {str(e)}"

    def download_all(self, ip, port, save_path, progress_callback=None):
        """Download all files as a zip archive with optimized streaming."""
        url = f"http://{ip}:{port}/download_all"
        try:
            response = self.session.get(url, stream=True, timeout=120)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 2 * 1024 * 1024  # 2MB chunks for large zip files
            downloaded = 0

            # Ensure parent directory exists
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            return True, "Bulk download complete!"
        except Exception as e:
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except:
                    pass
            return False, f"Bulk download failed: {str(e)}"

    def download_files_parallel(self, ip, port, file_list, base_save_path, progress_callback=None, max_workers=4):
        """Download multiple files in parallel for better performance."""
        def download_single(file_info):
            file_path = file_info['path']
            save_path = os.path.join(base_save_path, file_path)
            return self.download_file(ip, port, file_path, save_path, resume=True)

        successful = 0
        failed = 0
        total_files = len(file_list)
        
        # Filter only files (not folders)
        files_to_download = [f for f in file_list if f.get('type') == 'file']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(download_single, file_info): file_info 
                             for file_info in files_to_download}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    success, message = future.result()
                    if success:
                        successful += 1
                    else:
                        failed += 1
                        print(f"Failed to download {file_info['path']}: {message}")
                except Exception as e:
                    failed += 1
                    print(f"Exception downloading {file_info['path']}: {e}")
                
                if progress_callback:
                    progress_callback(successful + failed, len(files_to_download))

        return successful > 0, f"Downloaded {successful} files, {failed} failed"

    def close(self):
        """Clean up session and connections."""
        if self.session:
            self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
