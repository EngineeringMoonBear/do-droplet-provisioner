import os
import subprocess
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
    return None

def load_droplets():
    """Load droplet information from the log file."""
    droplets = []
    try:
        with open("droplets.log", "r") as f:
            for line in f:
                name, ip = line.strip().split(",")
                droplets.append({"name": name, "ip": ip})
    except FileNotFoundError:
        print("No droplets.log file found. No droplets to destroy.")
        exit(0)
    return droplets

def main():
    # Load environment variables
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)

    # Pull API token
    DO_API_TOKEN = os.getenv("DO_API_TOKEN")
    if not DO_API_TOKEN:
        print("Error: DigitalOcean API token not found. Please set it in the .env file.")
        exit(1)

    # Check for doctl
    if not shutil.which("doctl"):
        print("doctl (DigitalOcean CLI) is required but not installed.")
        print("Install: https://docs.digitalocean.com/reference/doctl/how-to/install/")
        exit(1)

    # Set env for doctl calls
    doctl_env = os.environ.copy()
    doctl_env["DIGITALOCEAN_ACCESS_TOKEN"] = DO_API_TOKEN

    # Load existing droplets
    droplets = load_droplets()
    if not droplets:
        print("No droplets found in the log file.")
        exit(0)

    # List droplets
    print("\nFound the following droplets:")
    for idx, droplet in enumerate(droplets, 1):
        print(f"[{idx}] {droplet['name']} (IP: {droplet['ip']})")

    # Get user selection
    print("\nOptions:")
    print("[number] - Destroy a specific droplet")
    print("[A] - Destroy all droplets")
    print("[Q] - Quit without destroying anything")
    
    choice = input("\nWhat would you like to do? ").strip().upper()
    
    if choice == 'Q':
        print("Exiting without destroying any droplets.")
        exit(0)
    
    droplets_to_destroy = []
    if choice == 'A':
        droplets_to_destroy = droplets
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(droplets):
                droplets_to_destroy = [droplets[idx]]
            else:
                print("Invalid selection.")
                exit(1)
        except ValueError:
            print("Invalid input. Please enter a number, 'A', or 'Q'.")
            exit(1)

    # Confirm destruction
    names = ", ".join(d['name'] for d in droplets_to_destroy)
    confirm = input(f"\n⚠️  Are you sure you want to destroy: {names}? (y/N) ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        exit(0)

    # Destroy droplets
    print("\nDestroying droplets...")
    for droplet in droplets_to_destroy:
        try:
            # Get droplet ID by name
            droplet_id = run_command(
                f"doctl compute droplet list --format ID,Name --no-header | grep {droplet['name']} | awk '{{print $1}}'",
                env=doctl_env
            )
            
            if droplet_id:
                print(f"Destroying {droplet['name']}...")
                run_command(f"doctl compute droplet delete {droplet_id} --force", env=doctl_env)
                print(f"✅ Destroyed {droplet['name']}")
            else:
                print(f"⚠️  Droplet {droplet['name']} not found on DigitalOcean (might have been already destroyed)")
        except Exception as e:
            print(f"Error destroying {droplet['name']}: {str(e)}")

    # Update droplets.log
    remaining_droplets = [d for d in droplets if d not in droplets_to_destroy]
    with open("droplets.log", "w") as f:
        for droplet in remaining_droplets:
            f.write(f"{droplet['name']},{droplet['ip']}\n")

    print("\n🧹 Cleanup complete!")
    if remaining_droplets:
        print(f"Remaining droplets in log: {len(remaining_droplets)}")
    else:
        print("No droplets remaining in log.")

if __name__ == "__main__":
    main() 