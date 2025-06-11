import os
import subprocess
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

def load_machines():
    """Load machine information from the log file."""
    machines = []
    try:
        with open("orb_machines.log", "r") as f:
            for line in f:
                name, os_image = line.strip().split(",")
                machines.append({"name": name, "os": os_image})
    except FileNotFoundError:
        print("No orb_machines.log file found. No machines to destroy.")
        exit(0)
    return machines

def main():
    # Check for orb CLI
    if not shutil.which("orb"):
        print("OrbStack CLI is required but not installed.")
        print("Install OrbStack from: https://orbstack.dev/download")
        exit(1)

    # Load existing machines
    machines = load_machines()
    if not machines:
        print("No machines found in the log file.")
        exit(0)

    # Get list of actual running machines
    try:
        running_machines = run_command("orb machine ls --format json")
        # Note: Parse JSON if needed for more detailed information
    except:
        running_machines = ""

    # List machines
    print("\nFound the following machines in log:")
    for idx, machine in enumerate(machines, 1):
        status = "✅ Running" if machine["name"] in running_machines else "⚠️  Not found"
        print(f"[{idx}] {machine['name']} (OS: {machine['os']}) - {status}")

    # Get user selection
    print("\nOptions:")
    print("[number] - Destroy a specific machine")
    print("[A] - Destroy all machines")
    print("[Q] - Quit without destroying anything")
    
    choice = input("\nWhat would you like to do? ").strip().upper()
    
    if choice == 'Q':
        print("Exiting without destroying any machines.")
        exit(0)
    
    machines_to_destroy = []
    if choice == 'A':
        machines_to_destroy = machines
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(machines):
                machines_to_destroy = [machines[idx]]
            else:
                print("Invalid selection.")
                exit(1)
        except ValueError:
            print("Invalid input. Please enter a number, 'A', or 'Q'.")
            exit(1)

    # Confirm destruction
    names = ", ".join(m['name'] for m in machines_to_destroy)
    confirm = input(f"\n⚠️  Are you sure you want to destroy: {names}? (y/N) ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        exit(0)

    # Destroy machines
    print("\nDestroying machines...")
    for machine in machines_to_destroy:
        try:
            print(f"Stopping {machine['name']}...")
            run_command(f"orb machine stop {machine['name']}")
            print(f"Destroying {machine['name']}...")
            run_command(f"orb machine rm {machine['name']}")
            print(f"✅ Destroyed {machine['name']}")
        except Exception as e:
            print(f"⚠️  Error destroying {machine['name']}: {str(e)}")

    # Update machines.log
    remaining_machines = [m for m in machines if m not in machines_to_destroy]
    with open("orb_machines.log", "w") as f:
        for machine in remaining_machines:
            f.write(f"{machine['name']},{machine['os']}\n")

    print("\n🧹 Cleanup complete!")
    if remaining_machines:
        print(f"Remaining machines in log: {len(remaining_machines)}")
    else:
        print("No machines remaining in log.")

if __name__ == "__main__":
    main() 