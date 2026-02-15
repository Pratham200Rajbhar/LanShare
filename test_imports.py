import sys
import os
sys.path.append(os.path.abspath("lan_share"))

try:
    from lan_share.utils.ip_utils import get_local_ip
    print("utils.ip_utils imported successfully")
    print(f"Local IP: {get_local_ip()}")
except ImportError as e:
    print(f"Error importing utils: {e}")

try:
    from lan_share.network.server import HTTPServerManager
    print("network.server imported successfully")
except ImportError as e:
    print(f"Error importing network.server: {e}")

try:
    from lan_share.network.client import HTTPClient
    print("network.client imported successfully")
except ImportError as e:
    print(f"Error importing network.client: {e}")
