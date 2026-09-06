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
│       ├── common/                      # Base system updates, Java 21, basic utilities
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
   - `roles/common` manages shared baseline packages (Java 21, git, curl).
   - Reusable across different environments without code duplication.

4. **Service-Specific Playbooks (`playbooks/`)**:
   - `playbooks/setup_jenkins.yml` only runs `common`, `aws_cli`, `terraform`, and `jenkins`.
   - A team member managing another service will run their own playbook (e.g., `setup_k8s.yml`) without touching Jenkins.

---