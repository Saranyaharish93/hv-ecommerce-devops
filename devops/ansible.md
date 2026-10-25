# Configuration Management with Ansible

This document outlines the Configuration Management architecture implemented with Ansible for the Lumora E-Commerce platform, focusing on agentless automation, modular roles, and strict idempotency.

---

## Table of Contents

1. [Configuration Management Philosophy](#1-configuration-management-philosophy)
2. [Modular Role Architecture](#2-modular-role-architecture)
3. [Deep-Dive into the 7 Modular Roles with Tool Verification](#3-deep-dive-into-the-7-modular-roles-with-tool-verification)
4. [Inventory and SSH Credential Management](#4-inventory-and-ssh-credential-management)
5. [Idempotency Testing and Convergence Proofs](#5-idempotency-testing-and-convergence-proofs)

---

## 1. Configuration Management Philosophy

In the Lumora architecture, virtual machines are not configured manually. We employ Ansible following these core principles:

- **Agentless Simplicity**: Operates entirely over standard OpenSSH; no background daemon or agent software is required on target hosts.
- **Single Responsibility Roles**: System tasks are cleanly decoupled into standalone roles, preventing configuration conflicts between different developer tools.
- **Strict Idempotency**: Running a playbook against a target host repeatedly produces zero unexpected configuration changes (`changed=0`), zero task failures (`failed=0`), and zero state drift.

---

## 2. Modular Role Architecture

The `ansible/` directory adopts a modular, role-based structure:

```
ansible/
├── ansible.cfg                          # Global configurations (roles_path, host_key_checking = False)
├── inventory/
│   ├── hosts.ini                        # Target hosts grouped by role with dynamic key resolving
│   └── group_vars/
│       ├── all.yml                      # Global environment parameters (region, environment)
│       └── jenkins.yml                  # Jenkins-specific variables (ports, plugins, job parameters)
├── playbooks/
│   ├── setup_jenkins.yml                # Master configuration playbook orchestrating all 7 roles
│   └── site.yml                         # Future multi-host site orchestration entry point
└── roles/
    ├── common/                          # Base system packages, repository updates, Java 21 LTS
    ├── aws_cli/                         # AWS CLI v2 installation and PATH registration
    ├── docker/                          # Docker CE, containerd, buildx, and group membership
    ├── kubectl/                         # Kubectl CLI binary installation aligned to cluster version
    ├── terraform/                       # HashiCorp repository and Terraform CLI
    ├── infracost/                       # Infracost FinOps binary installation
    └── jenkins/                         # Jenkins LTS repository, plugins, CLI, and job creation
```

The master playbook [setup_jenkins.yml](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/ansible/playbooks/setup_jenkins.yml) sequentially applies these roles:

```yaml
---
- name: Configure Jenkins Controller and CI/CD Tools
  hosts: jenkins
  become: yes
  roles:
    - common
    - aws_cli
    - docker
    - kubectl
    - terraform
    - infracost
    - jenkins
```

---

## 3. Deep-Dive into the 7 Modular Roles with Tool Verification

### 3.1. Role: `common`
- Updates the APT package cache safely.
- Removes legacy OpenJDK packages (e.g., OpenJDK 17) to prevent runtime conflicts.
- Installs **OpenJDK 21 LTS (`openjdk-21-jdk-headless`)**, the official required runtime for modern Jenkins LTS releases.
- Installs foundational utilities: `curl`, `wget`, `git`, `unzip`, `software-properties-common`, `ca-certificates`.

### 3.2. Role: `aws_cli`
- Idempotently checks if `aws --version` is already present.
- Downloads the official AWS CLI v2 bundle for Linux x86_64 (`https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip`).
- Extracts and executes `./aws/install --update`, ensuring the latest CLI is symlinked to `/usr/local/bin/aws`.
- Confirms the binary responds to STS identity commands.

### 3.3. Role: `docker`
- Idempotently verifies whether `docker --version` is installed.
- Establishes the official Docker GPG keyring at `/etc/apt/keyrings/docker.asc`.
- Configures the official Docker CE Ubuntu repository for the active Ubuntu release (`Noble`).
- Installs `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, and `docker-compose-plugin`.
- Enables and starts the `docker` systemd service.
- Appends both `ubuntu` and `jenkins` users to the `docker` UNIX group, granting non-root container build capabilities inside pipeline workspaces.

### 3.4. Role: `kubectl`
- Checks client version via `kubectl version --client`.
- If missing, queries Kubernetes release servers for the matching stable release string, with a clean fallback to `v1.36.0` to match our EKS control plane version.
- Downloads the official release binary from `https://dl.k8s.io/release/{{ kubectl_version }}/bin/linux/amd64/kubectl`.
- Installs binary with permissions `0755` into `/usr/local/bin/kubectl`.

### 3.5. Role: `terraform`
- Adds the official HashiCorp GPG key to `/usr/share/keyrings/hashicorp-archive-keyring.gpg`.
- Configures the HashiCorp APT repository and updates package lists.
- Installs the official `terraform` binary and verifies version execution.

### 3.6. Role: `infracost`
- Idempotently inspects `infracost --version`.
- Downloads the latest Linux AMD64 tarball from `https://github.com/infracost/infracost/releases/latest/download/infracost-linux-amd64.tar.gz`.
- Extracts and links the binary directly to `/usr/local/bin/infracost` for pipeline cost analysis.

### 3.7. Role: `jenkins`
- Establishes the 2026 Jenkins repository key at `/usr/share/keyrings/jenkins-keyring.asc`.
- Installs `jenkins` package and enables `systemd` service on port 8080.
- Automates initial unlock by retrieving the administrative password out-of-band.
- Uses `jenkins-cli.jar` to bootstrap required plugins: `git`, `workflow-aggregator`, `docker-workflow`, `kubernetes-cli`, `github`, `credentials-binding`.
- Renders [job.xml.j2](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/ansible/roles/jenkins/templates/job.xml.j2) and registers the declarative pipeline job `hv-ecommerce-devops-pipeline` with push webhook triggers pre-configured.



---

## 4. Inventory and SSH Credential Management

Target hosts are declared in [ansible/inventory/hosts.ini](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/ansible/inventory/hosts.ini):

```ini
[jenkins]
jenkins-server ansible_host=32.195.28.191

[all:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file={{ inventory_dir }}/../jenkins_key.pem
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

### Key Management Rules:
1. Terraform automatically generates the private key pair and outputs `jenkins_key.pem` directly into `ansible/`.
2. The file is strictly ignored via [.gitignore](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/.gitignore) (`ansible/jenkins_key.pem` and `*.pem`) so it can never be committed.
3. Permissions are set to read-only for the owner (`chmod 400 ansible/jenkins_key.pem`).
4. Using `{{ inventory_dir }}/../jenkins_key.pem` ensures the playbook resolves the key correctly regardless of whether invoked from repo root or the `ansible/` directory.

---

## 5. Idempotency Testing and Convergence Proofs

To validate that the playbook is truly idempotent, we execute the standard two-pass test:

```bash
# First Run: Applies configuration changes and installs packages
ansible-playbook -i inventory/hosts.ini playbooks/setup_jenkins.yml

# Second Run: Verifies system state (must produce changed=0)
ansible-playbook -i inventory/hosts.ini playbooks/setup_jenkins.yml
```



### Expected Output on Second Run:
```text
PLAY RECAP *********************************************************************
jenkins-server             : ok=24   changed=0    unreachable=0    failed=0    skipped=6    rescued=0    ignored=0
```
A return value of `changed=0` guarantees that the system is fully converged and free of configuration drift.

---

## 6. How Idempotency is Codified in Our Playbooks & Roles

In Ansible, idempotency is not achieved by chance—it is strictly codified into each task using declarative modules, pre-flight checks, and conditional guards:

### 6.1. Pre-Flight Checks & Conditional Execution (`changed_when: false`)
When downloading external binary utilities (such as `kubectl` or `docker`), executing a shell command on every run would always trigger `changed=1`. To maintain true idempotency, we inspect the existing binary first and mark the check task with `changed_when: false`:

From [`ansible/roles/kubectl/tasks/main.yml`](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/ansible/roles/kubectl/tasks/main.yml):
```yaml
- name: Check if kubectl is installed
  command: kubectl version --client
  register: kubectl_check
  ignore_errors: true
  changed_when: false

- name: Install kubectl CLI binary
  when: kubectl_check.rc != 0
  block:
    - name: Download official kubectl binary
      get_url:
        url: "https://dl.k8s.io/release/{{ kubectl_version }}/bin/linux/amd64/kubectl"
        dest: /usr/local/bin/kubectl
        mode: '0755'
        owner: root
        group: root
```
> **Idempotency Mechanism**: On the second pass, `kubectl_check.rc == 0`, causing Ansible to skip the download block entirely. The pre-flight check returns `ok` and `changed=0`.

---

### 6.2. Declarative Desired State (`state: present` & `state: started`)
Instead of running imperative commands like `systemctl start docker` or `apt-get install`, tasks declare the **desired end state**. Ansible verifies whether the current state already matches before taking action:

From [`ansible/roles/docker/tasks/main.yml`](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/ansible/roles/docker/tasks/main.yml):
```yaml
# Ensure service is running without issuing restart commands on every pass
- name: Ensure Docker service is enabled and running
  systemd:
    name: docker
    state: started
    enabled: yes

# Ensure group exists and append users idempotently
- name: Add ubuntu and jenkins users to docker group
  user:
    name: "{{ item }}"
    groups: docker
    append: yes
  loop:
    - ubuntu
    - jenkins
```
> **Idempotency Mechanism**: `systemd` inspects the active unit; if Docker is already running and enabled, no signal is sent and `changed` remains `0`. Similarly, `append: yes` ensures user group memberships are validated without resetting other secondary groups or passwords.

---

### 6.3. Repository Keyrings & Clean Sources
In Ubuntu 24.04+, legacy `apt-key add` commands are deprecated. We use modern, idempotent GPG de-armoring and targeted `.sources` lists:

From [`ansible/roles/jenkins/tasks/main.yml`](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/ansible/roles/jenkins/tasks/main.yml):
```yaml
- name: Add Jenkins official APT repository
  apt_repository:
    repo: "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/"
    state: present
    filename: jenkins
    update_cache: yes
```
> **Idempotency Mechanism**: The `apt_repository` module checks `/etc/apt/sources.list.d/jenkins.list`. If the repository entry already matches the target definition, it leaves the file untouched and skips cache updating on subsequent runs.
