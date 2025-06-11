import os
import subprocess
import time
import shutil
from pathlib import Path
from dotenv import load_dotenv

def run_command(command, capture_output=True, env=None):
    result = subprocess.run(command, shell=True, capture_output=capture_output, text=True, env=env)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    if capture_output:
        return result.stdout.strip()
    return None  # Prevent crash if capture_output=False

def main():
    # Load .env file from the same directory as the script
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)

    # Pull API token
    DO_API_TOKEN = os.getenv("DO_API_TOKEN")
    if not DO_API_TOKEN:
        print("Error: DigitalOcean API token not found. Please set it in the .env file.")
        exit(1)
    
    print(f"Loaded DO_API_TOKEN: {DO_API_TOKEN[:10]}...")  # Debug

    # Check for doctl
    if not shutil.which("doctl"):
        print("doctl (DigitalOcean CLI) is required but not installed.")
        print("Install: https://docs.digitalocean.com/reference/doctl/how-to/install/")
        exit(1)

    # Set env for all doctl calls
    doctl_env = os.environ.copy()
    doctl_env["DIGITALOCEAN_ACCESS_TOKEN"] = DO_API_TOKEN

 # Choose droplet name
    droplet_name = input("Enter a name for your droplet (default: test-droplet): ") or "test-droplet"

    # Get regions
    print("Fetching available DigitalOcean regions...")
    regions = run_command("doctl compute region list --format Slug --no-header", env=doctl_env).split("\n")
    for idx, region in enumerate(regions):
        print(f"[{idx}] {region}")
    region = regions[int(input("Enter the number corresponding to your desired region: "))]

    # Get droplet sizes
    print("Fetching available droplet sizes...")
    sizes = run_command("doctl compute size list --format Slug --no-header", env=doctl_env).split("\n")
    for idx, size in enumerate(sizes):
        print(f"[{idx}] {size}")
    size = sizes[int(input("Enter the number corresponding to your desired size: "))]

    # OS image
    image = input("Enter the OS image slug (default: ubuntu-22-04-x64): ") or "ubuntu-22-04-x64"

    # Container runtime
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
    install_command = install_commands.get(choice)
    if not install_command:
        print("Invalid selection.")
        exit(1)

    # SSH key IDs
    ssh_keys = run_command("doctl compute ssh-key list --format ID --no-header", env=doctl_env).replace("\n", ",")

    # Create droplet
    print("Creating the droplet...")
    droplet_id = run_command(
        f"doctl compute droplet create {droplet_name} "
        f"--region {region} --size {size} --image {image} "
        f"--ssh-keys {ssh_keys} --wait --format ID --no-header",
        env=doctl_env
    )

    # Get droplet IP
    droplet_ip = run_command(f"doctl compute droplet get {droplet_id} --format PublicIPv4 --no-header", env=doctl_env)
    print(f"Droplet '{droplet_name}' created with IP: {droplet_ip}")

    # Wait for SSH to be available
    print("Waiting for SSH to be available...")
    while os.system(f"nc -z {droplet_ip} 22") != 0:
        time.sleep(5)

    # Install container runtime
    print("Installing selected container runtime...")
    run_command(f"ssh -o StrictHostKeyChecking=no root@{droplet_ip} '{install_command}'", capture_output=False)

    # Log droplet info
    with open("droplets.log", "a") as log_file:
        log_file.write(f"{droplet_name},{droplet_ip}\n")

    print("\n✅ All done!")
    print(f"🔗 SSH into your droplet: ssh root@{droplet_ip}")
    print(f"📓 Logged to droplets.log as: {droplet_name},{droplet_ip}")

if __name__ == "__main__":
    main()