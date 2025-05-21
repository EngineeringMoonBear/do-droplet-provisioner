# do-droplet-provisioner

**do-droplet-provisioner** is a Python-based automation tool designed to streamline the provisioning of DigitalOcean droplets with your choice of container runtime: Kubernetes, Podman, or Docker. This utility simplifies the setup process, making it ideal for developers, DevOps engineers, and system administrators who require quick and consistent environment deployments.

## Features

* **Automated Droplet Provisioning**: Leverages the DigitalOcean API to create new droplets effortlessly.
* **Container Runtime Selection**: Choose between Kubernetes, Podman, or Docker during the provisioning process.
* **Customizable Configurations**: Tailor droplet specifications such as size, region, and image to fit your needs.
* **Environment Variable Management**: Utilizes a `.env` file for secure and flexible configuration.

## Prerequisites

Before using this tool, ensure you have the following:

* **Python 3.6+**: The script is written in Python and requires version 3.6 or higher.

* **DigitalOcean Personal Access Token**: Generate one from your [DigitalOcean Control Panel](https://cloud.digitalocean.com/account/api/tokens).

* **DigitalOcean Python Client**: Install via pip:

```bash
  pip install python-digitalocean
```



## Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/EngineeringMoonBear/do-droplet-provisioner.git
   cd do-droplet-provisioner
   ```



2. **Configure Environment Variables**

   Create a `.env` file in the root directory with the following content:

   ```ini
   DIGITALOCEAN_TOKEN=your_personal_access_token
   DROPLET_NAME=your_droplet_name
   REGION=nyc3
   IMAGE=ubuntu-20-04-x64
   SIZE=s-1vcpu-1gb
   SSH_KEYS=your_ssh_key_id
   CONTAINER_RUNTIME=docker
   ```



* `DIGITALOCEAN_TOKEN`: Your DigitalOcean Personal Access Token.
* `DROPLET_NAME`: Desired name for your droplet.
* `REGION`: Data center region (e.g., `nyc3`, `sfo2`).
* `IMAGE`: Droplet image (e.g., `ubuntu-20-04-x64`).
* `SIZE`: Droplet size (e.g., `s-1vcpu-1gb`).
* `SSH_KEYS`: Comma-separated list of SSH key IDs already added to your DigitalOcean account.
* `CONTAINER_RUNTIME`: Choose between `docker`, `podman`, or `kubernetes`.([GitHub][1], [Medium][2])

3. **Run the Provisioning Script**

   ```bash
   python deploy-droplet.py
   ```



The script will read the `.env` file and initiate the droplet creation process with the specified configurations.

## Usage

Once the droplet is provisioned:

* **Access the Droplet**: Use SSH to connect.

```bash
  ssh root@your_droplet_ip
```



* **Verify Container Runtime Installation**: Check that your chosen container runtime is installed and running.

  * For Docker:([GitHub][1])

    ```bash
    docker --version
    ```

  * For Podman:([Medium][3])

    ```bash
    podman --version
    ```

  * For Kubernetes:

    ```bash
    kubectl version --client
    ```
