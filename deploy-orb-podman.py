#!/usr/bin/env python3
import subprocess
import time
import sys
from pathlib import Path

def run_command(cmd_list, capture_output=True):
    """Run a command using array style to avoid shell interpretation issues."""
    try:
        result = subprocess.run(cmd_list, capture_output=capture_output, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result.stdout.strip() if capture_output else None
    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def wait_for_machine(machine_name, max_retries=10):
    """Wait for the machine to be ready."""
    print("Waiting for machine to be ready...")
    for i in range(max_retries):
        try:
            cmd = ["orb", "run", "-m", machine_name, "echo", "ready"]
            result = run_command(cmd)
            if result and "ready" in result:
                print("Machine is ready!")
                return True
        except:
            pass
        print(f"Waiting... (attempt {i + 1}/{max_retries})")
        time.sleep(5)
    return False

def install_podman(machine_name):
    """Install Podman on the machine using Ubuntu's official repositories."""
    print("\nInstalling Podman...")

    install_script = """#!/bin/bash
set -e
sudo apt-get update -y
sudo apt-get install -y podman
"""

    # Create a temporary directory in the user's home
    script_dir = Path.home() / ".orbstack" / "tmp"
    script_dir.mkdir(parents=True, exist_ok=True)
    local_script_path = script_dir / "install_podman.sh"
    remote_script_path = "/tmp/install_podman.sh"

    # Write script locally
    print(f"Writing install script to {local_script_path}")
    local_script_path.write_text(install_script)

    # Copy to VM
    print("Copying script to VM...")
    # First ensure the remote directory exists
    run_command(["orb", "run", "-m", machine_name, "mkdir", "-p", "/tmp"])
    # Then copy the file using push instead of cp
    run_command(["orb", "push", "-m", machine_name, str(local_script_path), remote_script_path])

    # Make executable
    run_command(["orb", "run", "-m", machine_name, "chmod", "+x", remote_script_path])

    # Run it
    print("Running install script on VM...")
    run_command(["orb", "run", "-m", machine_name, "sudo", "bash", remote_script_path], capture_output=False)

    # Clean up
    local_script_path.unlink()  # Remove local script
    run_command(["orb", "run", "-m", machine_name, "rm", remote_script_path])

    # Verify
    print("\nVerifying Podman installation...")
    run_command(["orb", "run", "-m", machine_name, "podman", "--version"], capture_output=False)

def main():
    machine_name = input("Enter machine name (default: podman-test): ").strip() or "podman-test"

    print(f"\nCreating Ubuntu machine '{machine_name}'...")
    run_command(["orb", "create", "ubuntu", machine_name])

    if not wait_for_machine(machine_name):
        print("Error: Machine failed to become ready")
        sys.exit(1)

    install_podman(machine_name)

    print("\n✅ Setup complete!")
    print(f"\nUseful commands:")
    print(f"  Access machine:    orb shell -m {machine_name}")
    print(f"  Run container:     orb run -m {machine_name} podman run -d nginx")
    print(f"  List containers:   orb run -m {machine_name} podman ps")
    print(f"  Stop machine:      orb stop {machine_name}")

if __name__ == "__main__":
    main()
