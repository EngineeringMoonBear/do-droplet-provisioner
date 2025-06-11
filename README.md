# Container Management Scripts

A set of Python scripts to easily provision and manage containers in both DigitalOcean and OrbStack environments.

## Prerequisites

### For DigitalOcean Deployment
1. Python 3.6 or higher
2. [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/) - DigitalOcean Command Line Interface
3. A DigitalOcean account and API token
4. SSH key added to your DigitalOcean account

### For Local OrbStack Deployment
1. Python 3.6 or higher
2. [OrbStack](https://orbstack.dev/download) installed and configured
3. OrbStack CLI available in your path

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd do-droplet-provisioner
```

2. Install required Python packages:
```bash
pip install python-dotenv
```

3. For DigitalOcean deployment only, create a `.env` file:
```bash
echo "DO_API_TOKEN=your_digitalocean_api_token" > .env
```

## Usage

### DigitalOcean Deployment

#### Creating a Droplet
Use `deploy-droplet.py` to create a new droplet with your chosen container runtime:
```bash
python deploy-droplet.py
```

#### Destroying Droplets
Use `destroy-droplet.py` to remove droplets:
```bash
python destroy-droplet.py
```

### Local OrbStack Deployment

#### Creating a Local Machine
Use `deploy-orb.py` to create a new local machine with your chosen container runtime:
```bash
python deploy-orb.py
```

Features:
- Choice of OS (Ubuntu, Debian, Fedora, or Alpine)
- Choice of container runtime (Podman, Kubernetes, or Docker)
- Automatic installation and configuration
- Local machine logging

#### Destroying Local Machines
Use `destroy-orb.py` to remove local machines:
```bash
python destroy-orb.py
```

## File Structure

### DigitalOcean Scripts
- `deploy-droplet.py` - Script for creating and provisioning droplets
- `destroy-droplet.py` - Script for destroying droplets
- `droplets.log` - Log file containing information about created droplets
- `.env` - Configuration file for your DigitalOcean API token

### OrbStack Scripts
- `deploy-orb.py` - Script for creating and provisioning local machines
- `destroy-orb.py` - Script for destroying local machines
- `orb_machines.log` - Log file containing information about created local machines

## Container Runtime Installation Methods

### Podman
- Uses distribution-specific installation methods
- Automatically selects correct repository based on OS
- Installs all required dependencies

### Kubernetes (K3s)
- Uses the official Rancher K3s installation script
- Installs a lightweight Kubernetes distribution
- Sets up a single-node cluster

### Docker
- Uses distribution-specific installation methods
- Sets up the Docker daemon automatically
- Configures necessary system settings

## Troubleshooting

### DigitalOcean SSH Issues
If the deployment script fails with SSH connection errors:
1. Ensure your SSH key is properly added to DigitalOcean
2. Wait a few minutes and try again
3. Check if you can manually SSH into the droplet

### OrbStack Issues
If the local deployment fails:
1. Ensure OrbStack is running (`orb doctor`)
2. Check machine status (`orb ps`)
3. Try connecting manually (`orb ssh machine-name`)

## Security Notes

1. Never commit your `.env` file to version control
2. The scripts use secure methods for authentication
3. Local machines are isolated from your host system

## Contributing

Feel free to submit issues and enhancement requests!
