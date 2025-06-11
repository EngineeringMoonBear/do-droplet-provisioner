# DigitalOcean Droplet Provisioner

A set of Python scripts to easily provision and destroy DigitalOcean droplets with container runtimes (Docker, Kubernetes, or Podman) pre-installed.

## Prerequisites

1. Python 3.6 or higher
2. [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/) - DigitalOcean Command Line Interface
3. A DigitalOcean account and API token
4. SSH key added to your DigitalOcean account

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

3. Create a `.env` file in the project root:
```bash
echo "DO_API_TOKEN=your_digitalocean_api_token" > .env
```

Replace `your_digitalocean_api_token` with your actual DigitalOcean API token. You can generate one at: https://cloud.digitalocean.com/account/api/tokens

## Usage

### Creating a Droplet

Use `deploy-droplet.py` to create a new droplet with your chosen container runtime:

```bash
python deploy-droplet.py
```

The script will:
1. Prompt you for a droplet name (defaults to "test-droplet")
2. Show available regions for you to choose from
3. Show available droplet sizes
4. Let you choose the OS image (defaults to Ubuntu 22.04)
5. Let you choose a container runtime:
   - Podman
   - Kubernetes (K3s)
   - Docker
6. Create the droplet and install the selected container runtime
7. Log the droplet details to `droplets.log`

### Destroying Droplets

Use `destroy-droplet.py` to remove droplets created by the deploy script:

```bash
python destroy-droplet.py
```

The script will:
1. Read the `droplets.log` file to show available droplets
2. Give you options to:
   - Destroy a specific droplet
   - Destroy all droplets
   - Quit without destroying anything
3. Ask for confirmation before destroying any droplets
4. Update the `droplets.log` file after successful destruction

## File Structure

- `deploy-droplet.py` - Script for creating and provisioning droplets
- `destroy-droplet.py` - Script for destroying droplets
- `droplets.log` - Log file containing information about created droplets
- `.env` - Configuration file for your DigitalOcean API token

## Logging

The scripts maintain a `droplets.log` file in CSV format:
```
droplet_name,ip_address
```

This file is:
- Created/updated when deploying new droplets
- Updated when destroying droplets
- Used to track and manage created droplets

## Error Handling

Both scripts include error handling for common scenarios:
- Missing API token
- Missing doctl CLI
- SSH connection issues
- Invalid user input
- Failed deployments or destructions

## Security Notes

1. Never commit your `.env` file to version control
2. The scripts use SSH key authentication for secure access to droplets
3. API tokens are handled securely through environment variables

## Troubleshooting

### SSH Connection Issues
If the deployment script fails with SSH connection errors:
1. Ensure your SSH key is properly added to DigitalOcean
2. Wait a few minutes and try again (sometimes droplets need extra time to initialize)
3. Check if you can manually SSH into the droplet: `ssh root@droplet_ip`

### Container Runtime Installation
If container runtime installation fails:
1. SSH into the droplet manually
2. Check system logs: `journalctl -xe`
3. Try installing the container runtime manually to see detailed error messages

## Contributing

Feel free to submit issues and enhancement requests!
