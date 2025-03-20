import os
import subprocess
import time
import shutil
from dotenv import load_dotenv

def run_command(command, capture_output=True):
    result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    return result.stdout.strip()

def main():
    # Load environment variables from .env file
    load_dotenv()
    DO_API_TOKEN = os.getenv("DO_API_TOKEN")
    
    if not DO_API_TOKEN:
        print("Error: DigitalOcean API token not found. Please set it in the .env file.")
        exit(1)
    
    # Check if doctl is installed
    if not shutil.which("doctl"):
        print("doctl (DigitalOcean CLI) is required but not installed.")
        print("Follow installation instructions at: https://docs.digitalocean.com/reference/doctl/how-to/install/")
        exit(1)

    # Authenticate with DigitalOcean
    print("Authenticating with DigitalOcean...")
    run_command(f"doctl auth init --access-token {DO_API_TOKEN}")

    # Get available regions
    print("Fetching available DigitalOcean regions...")
    regions = run_command("doctl compute region list --format Slug --no-header").split("\n")
    for idx, region in enumerate(regions):
        print(f"[{idx}] {region}")
    region = regions[int(input("Enter the number corresponding to your desired region: "))]

    # Get available droplet sizes
    print("Fetching available droplet sizes...")
    sizes = run_command("doctl compute size list --format Slug --no-header").split("\n")
    for idx, size in enumerate(sizes):
        print(f"[{idx}] {size}")
    size = sizes[int(input("Enter the number corresponding to your desired size: "))]

    # Choose OS image
    image = input("Enter the OS image slug (default: ubuntu-22-04-x64): ") or "ubuntu-22-04-x64"

    # Select container runtime
    options = {"1": "Podman", "2": "Kubernetes", "3": "Docker"}
    print("Choose a container runtime:")
    for key, value in options.items():
        print(f"[{key}] {value}")
    choice = input("Enter your choice (1/2/3): ")
    install_commands = {
        "1": "sudo apt update && sudo apt install -y podman",
        "2": "curl -sfL https://get.k3s.io | sh -",
        "3": "curl -fsSL https://get.docker.com | sh"
    }
    install_command = install_commands.get(choice, "")
    if not install_command:
        print("Invalid selection.")
        exit(1)

    # Deploy the droplet
    print("Creating the droplet...")
    droplet_id = run_command(f"doctl compute droplet create test-droplet --region {region} --size {size} --image {image} --ssh-keys $(doctl compute ssh-key list --format ID --no-header | tr '\n' ',') --wait --format ID --no-header")

    # Get Droplet IP Address
    droplet_ip = run_command(f"doctl compute droplet get {droplet_id} --format PublicIPv4 --no-header")
    print(f"Droplet created with IP: {droplet_ip}")

    # Wait for SSH
    print("Waiting for SSH to be available...")
    while os.system(f"nc -z {droplet_ip} 22") != 0:
        time.sleep(5)
    
    # Install selected container runtime
    print("Installing selected container runtime...")
    run_command(f"ssh -o StrictHostKeyChecking=no root@{droplet_ip} '{install_command}'", capture_output=False)
    
    print(f"Installation complete. You can now SSH into your droplet with: ssh root@{droplet_ip}")

if __name__ == "__main__":
    main()