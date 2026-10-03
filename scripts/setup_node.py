import os
import sys
import urllib.request
import zipfile
import shutil

tools_dir = os.path.join(os.path.expanduser("~"), "tools")
node_dir = os.path.join(tools_dir, "nodejs")
node_exe = os.path.join(node_dir, "node.exe")

if os.path.exists(node_exe):
    print(f"Node already exists at {node_exe}")
    sys.exit(0)

os.makedirs(tools_dir, exist_ok=True)
url = "https://nodejs.org/dist/v20.18.0/node-v20.18.0-win-x64.zip"
zip_path = os.path.join(tools_dir, "node.zip")

print(f"Downloading Node from {url}...")
urllib.request.urlretrieve(url, zip_path)
print("Extracting zip...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(tools_dir)

extracted_folder = os.path.join(tools_dir, "node-v20.18.0-win-x64")
if os.path.exists(extracted_folder):
    if os.path.exists(node_dir):
        shutil.rmtree(node_dir)
    shutil.move(extracted_folder, node_dir)

if os.path.exists(zip_path):
    os.remove(zip_path)

print(f"Node successfully installed to {node_dir}")
