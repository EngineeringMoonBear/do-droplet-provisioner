import os
import subprocess
import time
import shutil
from pathlib import Path

def run_command(command, capture_output=True):
    result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    if capture_output:
        return result.stdout.strip()
    return None

def main():
    # Check for orb CLI
    if not shutil.which("orb"):
        print("OrbStack CLI is required but not installed.")
        print("Install OrbStack from: https://orbstack.dev/download")
        exit(1)

    # Get machine name
    machine_name = input("Enter a name for your machine (default: test-machine): ") or "test-machine"

    # Choose OS
    print("\nAvailable OS options:")
    print("[1] Ubuntu 22.04 (default)")
    print("[2] Debian 12")
    print("[3] Fedora 39")
    print("[4] Alpine 3.19")
    
    os_choice = input("\nChoose OS (1-4) [1]: ") or "1"
    os_options = {
        "1": "ubuntu:22.04",
        "2": "debian:12",
        "3": "fedora:39",
        "4": "alpine:3.19"
    }
    
    os_image = os_options.get(os_choice)
    if not os_image:
        print("Invalid OS selection.")
        exit(1)

    # Container runtime selection
    print("\nChoose a container runtime:")
    print("[1] Podman")
    print("[2] Kubernetes (K3s)")
    print("[3] Docker")
    
    choice = input("Enter your choice (1/2/3): ")
    
    # Installation commands for different OSes and runtimes
    install_commands = {
        "ubuntu:22.04": {
            "1": """
source /etc/os-release && \
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" | tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list && \
curl -L "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/Release.key" | apt-key add - && \
apt-get update -y && \
apt-get install -y podman""",
            "2": "curl -sfL https://get.k3s.io | sh -",
            "3": "curl -fsSL https://get.docker.com | sh"
        },
        "debian:12": {
            "1": """
apt-get update && \
apt-get install -y curl && \
curl -fsSL https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/Debian_12/Release.key | gpg --dearmor > /etc/apt/trusted.gpg.d/libcontainers.gpg && \
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/Debian_12/ /" > /etc/apt/sources.list.d/libcontainers.list && \
apt-get update -y && \
apt-get install -y podman""",
            "2": "curl -sfL https://get.k3s.io | sh -",
            "3": "curl -fsSL https://get.docker.com | sh"
        },
        "fedora:39": {
            "1": "dnf install -y podman",
            "2": "curl -sfL https://get.k3s.io | sh -",
            "3": "dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo && dnf install -y docker-ce docker-ce-cli containerd.io"
        },
        "alpine:3.19": {
            "1": "apk add --no-cache podman",
            "2": "curl -sfL https://get.k3s.io | sh -",
            "3": "apk add --no-cache docker"
        }
    }

    install_command = install_commands.get(os_image, {}).get(choice)
    if not install_command:
        print("Invalid runtime selection.")
        exit(1)

    # Create the machine
    print(f"\nCreating OrbStack machine '{machine_name}'...")
    run_command(f"orb machine create {machine_name} --image {os_image}")

    # Wait for machine to be ready
    print("Waiting for machine to be ready...")
    time.sleep(5)

    # Install container runtime
    print(f"Installing {['Podman', 'Kubernetes', 'Docker'][int(choice)-1]}...")
    run_command(f"orb machine exec {machine_name} -- bash -c '{install_command}'", capture_output=False)

    # Get machine info
    machine_info = run_command(f"orb machine inspect {machine_name}")
    
    # Log machine info
    with open("orb_machines.log", "a") as log_file:
        log_file.write(f"{machine_name},{os_image}\n")

    print("\n" + "="*50)
    print("🚀 Local Machine Deployment Complete!")
    print("="*50)
    print("\nConnect to machine:")
    print(f"    orb connect {machine_name}")
    print("\n📝 Details:")
    print(f"    Name: {machine_name}")
    print(f"    OS: {os_image}")
    print(f"    Runtime: {['Podman', 'Kubernetes', 'Docker'][int(choice)-1]}")
    print("\n💾 Machine info saved to orb_machines.log")
    print("="*50)
    print("\n🔍 Additional commands:")
    print(f"    List files:    orb machine exec {machine_name} -- ls")
    print(f"    Check status:  orb machine status {machine_name}")
    print(f"    Stop machine:  orb machine stop {machine_name}")
    print("="*50)

if __name__ == "__main__":
    main() 