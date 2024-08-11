import os
import subprocess
import click
import httpx
import base64

# Paths
version_file_path = os.path.join(os.path.dirname(__file__), "./src/data/version.py")
exe_file_path = os.path.join(os.path.dirname(__file__), "./dist/Privatools.exe")

# URL for version info
req_url = "https://raw.githubusercontent.com/Its3rr0rsWRLD/RAMPAGE/main/version.txt"

# Fetch current version
response = httpx.get(req_url)
click.secho("Current version: " + response.text, fg='green')

# Update version
new_version = input("Version to update: ")
with open(version_file_path, 'w') as file:
    file.write(f'version = "{new_version}"')

# Build and obfuscate
process1 = subprocess.Popen(
    "pyinstaller --onefile --add-data .venv/Lib/site-packages/tls_client/dependencies/tls-client-64.dll;tls_client/dependencies --icon=icon.ico --name=Privatools src/main.py",
    shell=True
)
process1.wait()

process2 = subprocess.Popen(
    "pyarmor gen --enable-jit --enable-themida --pack dist/privatools.exe -r src/main.py",
    shell=True
)
process2.wait()

click.secho("Packaging and Obfuscation done.", fg='green')
is_good = input("\n\nPlease verify that nothing bad happened while compiling. Is it good? (y/n): ")

if is_good.lower() != "y":
    print("\nOk try again...")
    exit()