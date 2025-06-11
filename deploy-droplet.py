import os
import subprocess
import time
import shutil
from pathlib import Path
from dotenv import load_dotenv

def wait_for_ssh(ip, max_retries=10):
    """Wait for SSH to be fully available with retries."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Try to run a simple command via SSH
            result = subprocess.run(
                f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@{ip} 'echo ready'",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and "ready" in result.stdout:
                print("SSH is fully available!")
                return True
        except Exception as e:
            pass
        
        print(f"Waiting for SSH... (attempt {retry_count + 1}/{max_retries})")
        retry_count += 1
        time.sleep(10)
    
    return False

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
        "1": """
source /etc/os-release && \
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list && \
curl -L "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/Release.key" | sudo apt-key add - && \
sudo apt-get update -y && \
sudo apt-get install -y podman""",
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

    # Wait for SSH to be fully available
    print("Waiting for SSH to be available...")
    if not wait_for_ssh(droplet_ip):
        print("Error: Could not establish a stable SSH connection.")
        exit(1)

    # Install container runtime
    print("Installing selected container runtime...")
    print(f"Running: {install_command}")
    run_command(f"ssh -o StrictHostKeyChecking=no root@{droplet_ip} '{install_command}'", capture_output=False)

    # Verify installation
    if choice == "1":  # Podman
        print("Verifying Podman installation...")
        run_command(f"ssh -o StrictHostKeyChecking=no root@{droplet_ip} 'podman --version'", capture_output=False)
    elif choice == "2":  # Kubernetes
        print("Verifying K3s installation...")
        run_command(f"ssh -o StrictHostKeyChecking=no root@{droplet_ip} 'k3s --version'", capture_output=False)
    elif choice == "3":  # Docker
        print("Verifying Docker installation...")
        run_command(f"ssh -o StrictHostKeyChecking=no root@{droplet_ip} 'docker --version'", capture_output=False)

    # Log droplet info
    with open("droplets.log", "a") as log_file:
        log_file.write(f"{droplet_name},{droplet_ip}\n")

    print("\n" + "="*50)
    print("🚀 Deployment Complete!")
    print("="*50)
    print("\nSSH Connection:")
    print(f"    ssh root@{droplet_ip}")
    print("\n📝 Details:")
    print(f"    Name: {droplet_name}")
    print(f"    IP:   {droplet_ip}")
    print(f"    Runtime: {options[choice]}")
    print("\n💾 Connection info saved to droplets.log")
    print("="*50)

if __name__ == "__main__":
    main()