# Step-by-Step Implementation Plan: Ansible-Driven Jenkins & Service Architecture

> **Target Infrastructure**: AWS EC2 `lumora-ecommerce-prod-jenkins-server` (`i-03e7a9837cadbced6`)  
> **Public IP**: `100.25.98.10`  
> **SSH User**: `ubuntu`  
> **Private Key Target**: `ansible/jenkins_key.pem`  
> **Objective**: Clean, multi-service Ansible configuration structure to install and configure Jenkins inside EC2 without causing conflicts with other services (Docker, kubectl, AWS CLI, K8s).

---

## 1. Multi-Service Ansible Directory Architecture

To ensure Jenkins configuration does not cause confusion with other services (planned in Sprint 3 like Docker, kubectl, and AWS CLI), we adopt the standard **Ansible Role-Based Modular Architecture**.

```
hv-ecommerce-devops/
├── ansible/
│   ├── ansible.cfg                      # Global settings (roles_path, host_key_checking = False)
│   │
│   ├── inventory/
│   │   ├── hosts.ini                    # Grouped hosts (separate [jenkins] from future services)
│   │   └── group_vars/
│   │       ├── all.yml                  # Global variables (e.g., AWS region, environment)
│   │       └── jenkins.yml              # Isolated variables strictly for Jenkins
│   │
│   ├── playbooks/
│   │   ├── site.yml                     # Master playbook orchestrating all services
│   │   └── setup_jenkins.yml            # Dedicated playbook for Jenkins controller
│   │
│   └── roles/
│       ├── common/                      # Base system updates, Java 17, basic utilities
│       │   └── tasks/main.yml
│       ├── jenkins/                     # Isolated: Jenkins installation, plugins (#5), job (#6 & #15)
│       │   ├── tasks/main.yml
│       │   ├── templates/job.xml.j2     # Jinja2 template for pipeline job
│       │   └── vars/main.yml
│       ├── docker/                      # Future Sprint 3 #18: Docker Engine & user permissions
│       │   └── tasks/main.yml
│       ├── kubectl/                     # Future Sprint 3 #19: Kubectl CLI
│       │   └── tasks/main.yml
│       ├── aws_cli/                     # Sprint 3 #20: AWS CLI v2
│       │   └── tasks/main.yml
│       └── terraform/                   # Terraform CLI for CI/CD runners
│           └── tasks/main.yml
```

---

## 2. Why This Architecture Prevents Confusion Across Services

1. **Host Group Isolation in Inventory (`inventory/hosts.ini`)**:
   - The Jenkins server belongs to the `[jenkins]` group.
   - Other nodes (e.g., EKS worker nodes or DB servers) belong to distinct groups (`[k8s]`, `[db]`).
   - Playbooks target only the specific group, preventing accidental changes to unrelated servers.

2. **Isolated Variables per Service (`inventory/group_vars/`)**:
   - Variables for Jenkins (port `8080`, plugins list, Jenkins version) live solely in `group_vars/jenkins.yml`.
   - Variables for Kubernetes or Docker live in their respective variable files.

3. **Single Responsibility Roles (`roles/`)**:
   - `roles/jenkins` only manages Jenkins service, plugins, and job registration.
   - `roles/common` manages shared baseline packages (Java 17, git, curl).
   - Reusable across different environments without code duplication.

4. **Service-Specific Playbooks (`playbooks/`)**:
   - `playbooks/setup_jenkins.yml` only runs `common`, `aws_cli`, `terraform`, and `jenkins`.
   - A team member managing another service will run their own playbook (e.g., `setup_k8s.yml`) without touching Jenkins.

---

## 3. Step-by-Step Instructions to Set Up the Ansible Structure

### Step 1: Create Ansible Configuration (`ansible/ansible.cfg`)
```ini
[defaults]
inventory = inventory/hosts.ini
roles_path = roles
remote_user = ubuntu
private_key_file = jenkins_key.pem
host_key_checking = False
retry_files_enabled = False

[privilege_escalation]
become = False
become_method = sudo
become_user = root
become_ask_pass = False
```

> [!TIP]
> **Security Best Practice (Principle of Least Privilege)**:
> `become = False` is set globally in `ansible.cfg` to prevent all tasks from running as root by default. Privilege escalation is explicitly declared via `become: true` only in the playbooks or roles that install packages or manage system services.


---

### Step 2: Create Inventory File (`ansible/inventory/hosts.ini`)
```ini
[jenkins]
jenkins-server ansible_host=100.25.98.10

[all:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=jenkins_key.pem
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

---

### Step 3: Create Jenkins Variables (`ansible/inventory/group_vars/jenkins.yml`)
```yaml
---
jenkins_http_port: 8080
jenkins_plugins:
  - git
  - github
  - workflow-aggregator
  - credentials-binding
  - aws-credentials
  - terraform

jenkins_pipeline_repo: "https://github.com/Saranyaharish93/hv-ecommerce-devops.git"
jenkins_pipeline_branch: "*/main"
jenkins_job_name: "hv-ecommerce-devops-pipeline"
```

### Step 4: Create Modular Roles

#### **A. Role: Common (`ansible/roles/common/tasks/main.yml`)**
```yaml
---
- name: Update apt cache
  apt:
    update_cache: yes
    cache_valid_time: 3600

- name: Remove outdated OpenJDK 17
  apt:
    name:
      - openjdk-17-jre
      - openjdk-17-jre-headless
    state: absent

- name: Install baseline utilities, fontconfig, and OpenJDK 21
  apt:
    name:
      - fontconfig
      - openjdk-21-jre
      - curl
      - wget
      - git
      - unzip
      - gnupg
      - lsb-release
    state: present
```

#### **B. Role: AWS CLI (`ansible/roles/aws_cli/tasks/main.yml`)**
```yaml
---
- name: Check if AWS CLI is installed
  command: aws --version
  register: aws_cli_check
  ignore_errors: true
  changed_when: false

- name: Download and install AWS CLI v2
  when: aws_cli_check.rc != 0
  block:
    - name: Download AWS CLI v2 zip
      get_url:
        url: "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
        dest: "/tmp/awscliv2.zip"
    - name: Unarchive AWS CLI zip
      unarchive:
        src: "/tmp/awscliv2.zip"
        dest: "/tmp"
        remote_src: yes
    - name: Run AWS CLI installer
      command: /tmp/aws/install
    - name: Clean up temporary files
      file:
        path: "{{ item }}"
        state: absent
      loop:
        - "/tmp/awscliv2.zip"
        - "/tmp/aws"
```

#### **C. Role: Terraform (`ansible/roles/terraform/tasks/main.yml`)**
```yaml
---
- name: Download HashiCorp GPG key
  get_url:
    url: https://apt.releases.hashicorp.com/gpg
    dest: /usr/share/keyrings/hashicorp-archive-keyring.asc
    mode: '0644'

- name: Dearmor HashiCorp GPG key
  shell: |
    gpg --dearmor --yes -o /usr/share/keyrings/hashicorp-archive-keyring.gpg /usr/share/keyrings/hashicorp-archive-keyring.asc
    chmod 644 /usr/share/keyrings/hashicorp-archive-keyring.gpg
  changed_when: false

- name: Add HashiCorp repository
  apt_repository:
    repo: "deb [arch=amd64 signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com {{ ansible_distribution_release }} main"
    state: present
    filename: hashicorp

- name: Install Terraform CLI
  apt:
    name: terraform
    state: present
    update_cache: yes
```

#### **D. Role: Jenkins (`ansible/roles/jenkins/tasks/main.yml`)**
```yaml
---
# ==============================================================================
# 1. Clean Stale Repository Configurations
# ==============================================================================
- name: Clean up any stale Jenkins lines from main sources.list
  lineinfile:
    path: /etc/apt/sources.list
    regexp: '.*pkg\.jenkins\.io.*'
    state: absent
  ignore_errors: true

- name: Clean up old Jenkins keyrings and list files
  file:
    path: "{{ item }}"
    state: absent
  loop:
    - /etc/apt/sources.list.d/jenkins.list
    - /etc/apt/trusted.gpg.d/jenkins.gpg
    - /usr/share/keyrings/jenkins-keyring.asc
    - /usr/share/keyrings/jenkins-keyring.gpg

- name: Remove any remaining repository files referencing pkg.jenkins.io
  shell: |
    grep -l "pkg.jenkins.io" /etc/apt/sources.list.d/* 2>/dev/null | xargs rm -f || true
  changed_when: false

# ==============================================================================
# 2. Download and Configure Official GPG Key & APT Repo (2026 Key ID 7198F4B714ABFC68)
# ==============================================================================
- name: Download official Jenkins 2026 GPG key and configure keyrings
  shell: |
    curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key | tee /usr/share/keyrings/jenkins-keyring.asc | gpg --dearmor --yes -o /usr/share/keyrings/jenkins-keyring.gpg
    chmod 644 /usr/share/keyrings/jenkins-keyring.asc /usr/share/keyrings/jenkins-keyring.gpg
  changed_when: false

- name: Add Jenkins official APT repository
  apt_repository:
    repo: "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/"
    state: present
    filename: jenkins
    update_cache: yes

# ==============================================================================
# 3. Install and Start Jenkins Service
# ==============================================================================
- name: Remove outdated Java 17 packages
  apt:
    name:
      - openjdk-17-jre
      - openjdk-17-jre-headless
    state: absent

- name: Ensure Java 21 and fontconfig are installed
  apt:
    name:
      - fontconfig
      - openjdk-21-jre
    state: present

- name: Install Jenkins LTS package
  apt:
    name: jenkins
    state: present
    update_cache: yes

- name: Create systemd override directory for Jenkins
  file:
    path: /etc/systemd/system/jenkins.service.d
    state: directory
    mode: '0755'

- name: Configure systemd override for Jenkins CLI and Java options
  copy:
    dest: /etc/systemd/system/jenkins.service.d/override.conf
    content: |
      [Service]
      Environment="JAVA_OPTS=-Djava.awt.headless=true -Dhudson.cli.CLIAction.ACCEPT_URL_FROM_REQUEST=true"
    mode: '0644'

- name: Create Jenkins init.groovy.d directory
  file:
    path: /var/lib/jenkins/init.groovy.d
    state: directory
    owner: jenkins
    group: jenkins
    mode: '0755'

- name: Set Jenkins root URL via init script to authorize CLI handshake
  copy:
    dest: /var/lib/jenkins/init.groovy.d/01-set-url.groovy
    content: |
      import jenkins.model.JenkinsLocationConfiguration
      def location = JenkinsLocationConfiguration.get()
      location.setUrl("http://localhost:{{ jenkins_http_port }}/")
      location.save()
    owner: jenkins
    group: jenkins
    mode: '0644'

- name: Preconfigure JenkinsLocationConfiguration XML
  copy:
    dest: /var/lib/jenkins/jenkins.model.JenkinsLocationConfiguration.xml
    content: |
      <?xml version='1.1' encoding='UTF-8'?>
      <jenkins.model.JenkinsLocationConfiguration>
        <jenkinsUrl>http://localhost:{{ jenkins_http_port }}/</jenkinsUrl>
      </jenkins.model.JenkinsLocationConfiguration>
    owner: jenkins
    group: jenkins
    mode: '0644'

- name: Reset failed systemd state for jenkins
  command: systemctl reset-failed jenkins
  ignore_errors: true
  changed_when: false

- name: Reload systemd daemon
  systemd:
    daemon_reload: yes

- name: Enable and restart Jenkins systemd service
  systemd:
    name: jenkins
    state: restarted
    enabled: yes

# ==============================================================================
# 4. Wait for Initialization & Extract Admin Token
# ==============================================================================
- name: Wait for Jenkins port {{ jenkins_http_port }} to be open
  wait_for:
    port: "{{ jenkins_http_port }}"
    delay: 5
    timeout: 180

- name: Wait for initialAdminPassword file to be generated
  wait_for:
    path: /var/lib/jenkins/secrets/initialAdminPassword
    timeout: 180

- name: Download Jenkins CLI jar from running controller
  get_url:
    url: "http://localhost:{{ jenkins_http_port }}/jnlpJars/jenkins-cli.jar"
    dest: /opt/jenkins-cli.jar
    mode: '0755'

- name: Read Initial Admin Password
  slurp:
    src: /var/lib/jenkins/secrets/initialAdminPassword
  register: admin_pass_raw

- name: Set admin password variable
  set_fact:
    admin_password: "{{ admin_pass_raw['content'] | b64decode | trim }}"

# ==============================================================================
# 5. Install Plugins & Restart (Task #5)
# ==============================================================================
- name: Install required Jenkins plugins in batch (Task #5)
  command: >
    java -jar /opt/jenkins-cli.jar -s http://localhost:{{ jenkins_http_port }}/
    -auth admin:{{ admin_password }}
    install-plugin {{ jenkins_plugins | join(' ') }}
  register: plugin_install
  changed_when: "'Installed' in plugin_install.stdout"

- name: Restart Jenkins to activate plugins
  systemd:
    name: jenkins
    state: restarted

- name: Wait for Jenkins port {{ jenkins_http_port }} to reopen after restart
  wait_for:
    port: "{{ jenkins_http_port }}"
    delay: 10
    timeout: 180

# ==============================================================================
# 6. Register Pipeline Job (Task #6 & #15)
# ==============================================================================
- name: Deploy Pipeline Job Definition XML template
  template:
    src: job.xml.j2
    dest: /tmp/job.xml

- name: Register Pipeline Job in Jenkins (Task #6 & #15)
  shell: >
    java -jar /opt/jenkins-cli.jar -s http://localhost:{{ jenkins_http_port }}/
    -auth admin:{{ admin_password }}
    create-job "{{ jenkins_job_name }}" < /tmp/job.xml ||
    java -jar /opt/jenkins-cli.jar -s http://localhost:{{ jenkins_http_port }}/
    -auth admin:{{ admin_password }}
    update-job "{{ jenkins_job_name }}" < /tmp/job.xml
```

#### **E. Job Template (`ansible/roles/jenkins/templates/job.xml.j2`)**
```xml
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>Automated Infrastructure Pipeline for Lumora E-Commerce DevOps (Sprint 2 #15)</description>
  <properties>
    <com.coravy.hudson.plugins.github.GithubProjectProperty plugin="github">
      <projectUrl>{{ jenkins_pipeline_repo }}/</projectUrl>
    </com.coravy.hudson.plugins.github.GithubProjectProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>{{ jenkins_pipeline_repo }}</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>{{ jenkins_pipeline_branch }}</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
</flow-definition>
```

---

### Step 5: Create the Orchestration Playbook (`ansible/playbooks/setup_jenkins.yml`)
```yaml
---
- name: Configure Jenkins Controller and CI/CD Tools
  hosts: jenkins
  become: yes
  roles:
    - common
    - aws_cli
    - terraform
    - jenkins
```

---

## 4. How to Execute the Ansible Playbook

### Option 1: Run Remotely from Workstation (WSL / Linux / Mac)
Ensure the private key `jenkins_key.pem` is placed in `ansible/` with `chmod 400`:
```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbooks/setup_jenkins.yml
```

### Option 2: Run Locally on the EC2 Server (`100.25.98.10`)
If you prefer running Ansible directly on the EC2 server without configuring remote SSH on your local workstation:
1. Connect via EC2 Instance Connect.
2. Install Ansible on EC2:
   ```bash
   sudo apt-get update && sudo apt-get install -y ansible
   ```
3. Run the playbook locally:
   ```bash
   ansible-playbook -i "localhost," -c local playbooks/setup_jenkins.yml
   ```

---

## 5. Verification Checklist

1. **Ansible Output**: All tasks show `ok` or `changed`, with `failed=0`.
2. **Jenkins Web Service**: Open `http://100.25.98.10:8080` in your browser.
3. **Task #5 (Plugins)**: Navigate to **Manage Jenkins $\rightarrow$ Plugins $\rightarrow$ Installed Plugins** to verify `git`, `github`, `workflow-aggregator`, `credentials-binding`, `aws-credentials`, and `terraform` are active.
4. **Task #5 (AWS Auth)**: Run `aws sts get-caller-identity` on the server to verify role `lumora-ecommerce-prod-jenkins-role` is active.
5. **Task #6 & #15 (Job)**: Open dashboard and verify the job `hv-ecommerce-devops-pipeline` is registered and ready to execute the root `Jenkinsfile`.
