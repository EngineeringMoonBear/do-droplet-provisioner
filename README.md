# OrbStack Machine Provisioner

A collection of scripts to manage OrbStack machines and DigitalOcean droplets with different container runtimes.

## Requirements

### For OrbStack
- macOS 13.0 or newer
- [OrbStack](https://orbstack.dev/download) installed
- Python 3.7 or newer

### For DigitalOcean
- Python 3.7 or newer
- [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/) installed
- DigitalOcean API token
- SSH key added to your DigitalOcean account

## Scripts

### 1. `deploy-orb-podman.py`

Creates an Ubuntu machine in OrbStack and installs Podman container runtime.

**Features:**
- Creates a new Ubuntu machine
- Installs Podman from Ubuntu's official repositories
- Verifies the installation
- Provides helpful commands for using Podman

**Usage:**
```bash
python deploy-orb-podman.py
```

### 2. `deploy-droplet.py`

Creates and provisions DigitalOcean droplets with your choice of container runtime.

**Features:**
- Interactive region and size selection
- Support for multiple container runtimes:
  - Podman
  - Docker
  - Kubernetes (K3s)
- Automatic SSH key configuration
- Machine readiness checks
- Logs droplet information for future reference

**Usage:**
```bash
python deploy-droplet.py
```

### 3. `destroy-droplet.py`

Safely destroys DigitalOcean droplets and cleans up resources.

**Features:**
- Lists available droplets
- Gracefully terminates instances
- Cleans up associated resources
- Maintains a log of deletions
- Interactive confirmation to prevent accidental deletions

**Usage:**
```bash
python destroy-droplet.py
```

## Common Commands

### OrbStack Commands
```bash
# Create a machine
orb create ubuntu machine-name

# Run commands on a machine
orb run -m machine-name command

# Copy files to a machine
orb push -m machine-name local_file remote_path

# Access machine shell
orb shell -m machine-name

# Stop a machine
orb stop machine-name

# Delete a machine
orb delete machine-name
```

### DigitalOcean Commands
```bash
# List droplets
doctl compute droplet list

# SSH into a droplet
ssh root@droplet-ip

# Delete a droplet
doctl compute droplet delete droplet-id
```

## File Structure

```
.
├── README.md
├── deploy-orb-podman.py  # OrbStack Podman installation script
├── deploy-droplet.py     # DigitalOcean deployment script
├── destroy-droplet.py    # DigitalOcean cleanup script
├── droplets.log         # DigitalOcean droplet tracking log
└── .gitignore
```

## Error Handling

The scripts include error handling for common scenarios:
- Machine/droplet creation failures
- Connection timeouts
- Installation errors
- Resource cleanup issues
- SSH key configuration problems

## Contributing

Feel free to submit issues and enhancement requests!
