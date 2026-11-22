# Infrastructure Operations Runbook

## 1. Purpose

This runbook documents the operational procedures for the secure enterprise
network and private cloud infrastructure.

It provides a reference for infrastructure startup, administrative access,
application deployment, monitoring, troubleshooting, recovery and controlled
shutdown.

All operations are restricted to the locally managed laboratory environment.

## 2. Administrative Environment

| Component | Configuration |
|---|---|
| Windows host | Windows 10 Pro |
| Virtualization platform | Hyper-V |
| Firewall | LAB-FW-01 |
| Management server | LAB-MGMT-01 |
| Application server | LAB-APP-01 |
| Linux administrative account | labadmin |
| Infrastructure automation | Ansible |
| Container runtime | Rootless Podman |
| Administrative orchestration | PowerShell |

### Repository Locations

Authoritative Windows repository:

```text
D:\engineering-lab\projects\secure-enterprise-network-private-cloud
```

Ubuntu automation workspace:

```text
/home/labadmin/infrastructure-automation
```

Source code and automation changes originate in the Windows repository.
Relevant files are transferred to the Ubuntu management server using SCP.

## 3. Infrastructure Startup Procedure

Start the virtual machines in the following order using Hyper-V Manager:

1. LAB-FW-01.
2. LAB-MGMT-01.
3. LAB-APP-01.

Allow each system to complete its startup sequence before depending on
its services.

Starting the firewall first establishes the network segmentation layer
before the management and application servers become operational.

Verify virtual machine status from an authorized PowerShell session:

```powershell
.\scripts\manage_infrastructure.ps1 -Action Status
```

Expected result:

- All three virtual machines are running.
- Assigned memory and uptime are available.
- Infrastructure status inspection completes successfully.

Hyper-V inspection requires appropriate Windows permissions.

## 4. Establish Management Access

From Windows PowerShell, connect to the Ubuntu management server:

```powershell
ssh -o StrictHostKeyChecking=yes labadmin@10.20.40.10
```

Enter the authorized Ubuntu account password when prompted.

Navigate to the infrastructure automation workspace:

```bash
cd ~/infrastructure-automation
```

All subsequent Linux administration commands must be executed from
the appropriate Ubuntu management session.

## 5. Initialize SSH Authentication

The Ubuntu management server uses a dedicated ED25519 automation identity
to administer the Rocky Linux application server.

After a management server restart, initialize an authentication agent:

```bash
eval "$(ssh-agent -s)"
```

Load the passphrase-protected automation identity:

```bash
ssh-add ~/.ssh/lab_automation_ed25519
```

Enter the private key passphrase when requested.

Verify that the identity is loaded:

```bash
ssh-add -l
```

Refresh the protected authentication socket reference:

```bash
chmod 700 "$HOME/.ssh"
ln -sfn "$SSH_AUTH_SOCK" "$HOME/.ssh/lab-agent.sock"
```

Validate the stable authentication reference:

```bash
SSH_AUTH_SOCK="$HOME/.ssh/lab-agent.sock" ssh-add -l
```

The stable reference allows separately established SSH sessions to use
the existing local authentication agent.

The reference must be refreshed whenever the underlying agent changes.

Private keys and passphrases must not be copied into the repository or
stored directly in administrative scripts.

## 6. Verify Rocky Administration

From the Ubuntu management server:

```bash
ssh -o BatchMode=yes \
-o StrictHostKeyChecking=yes \
-o IdentitiesOnly=yes \
-i ~/.ssh/lab_automation_ed25519 \
labadmin@10.20.20.10 hostname
```

Expected hostname:

```text
labapp01
```

Verify Ansible connectivity:

```bash
.venv/bin/ansible application_servers -m ping
```

Expected result:

```text
ping: pong
```

Authentication or host key verification failures must be investigated
before proceeding with deployment.

## 7. Application Deployment

The infrastructure hosts two operational applications.

| Application | Deployment playbook |
|---|---|
| Enterprise health service | playbooks/deploy_application.yml |
| Enterprise API | playbooks/deploy_enterprise_api.yml |

### Deploy the Health Service

```bash
.venv/bin/ansible-playbook \
playbooks/deploy_application.yml
```

### Deploy the Enterprise API

```bash
.venv/bin/ansible-playbook \
playbooks/deploy_enterprise_api.yml
```

The enterprise API deployment requires the locally imported application
image and previously initialized persistent database volume.

It does not automatically initialize missing enterprise data.

Unexpected existing configuration is rejected rather than silently
overwritten.

### Deployment Acceptance Criteria

- Deployment completes without failed or unreachable hosts.
- Required container images are available locally.
- Application security assertions pass.
- Application health endpoints respond successfully.
- Existing compliant containers are not unnecessarily recreated.
- Persistent application data is preserved.

Repeated execution against a compliant environment should report zero
configuration changes.

## 8. Establish Encrypted Enterprise API Access

The enterprise API is published exclusively on the Rocky host
loopback interface.

From Ubuntu, establish the management tunnel:

```bash
ssh -f -N \
-o BatchMode=yes \
-o StrictHostKeyChecking=yes \
-o IdentitiesOnly=yes \
-o ExitOnForwardFailure=yes \
-i ~/.ssh/lab_automation_ed25519 \
-L 127.0.0.1:18000:127.0.0.1:18000 \
labadmin@10.20.20.10
```

This creates an encrypted forwarding path between the Ubuntu management
server and the Rocky application server.

The tunnel should be established only once per active listening port.

Verify the tunnel and application health:

```bash
curl --noproxy "*" --fail --silent --show-error \
--max-time 5 http://127.0.0.1:18000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "enterprise-api-security-testing"
}
```

The enterprise API must not be directly exposed through an unrestricted
host network binding.

Application authentication is still required for protected endpoints.

## 9. Firewall Administration

The OPNsense administrative interface is accessed through an encrypted
management connection.

From a separate Windows PowerShell session:

```powershell
ssh -o ExitOnForwardFailure=yes `
-N `
-L 127.0.0.1:8443:10.20.10.1:443 `
labadmin@10.20.40.10
```

Open the local browser address:

```text
https://127.0.0.1:8443
```

Authenticate using the authorized laboratory firewall administration
credentials.

Firewall administration must preserve the established segmentation
and restricted application access rules.

Unexpected certificate warnings or host identity changes should be
investigated rather than automatically accepted.

Close the dedicated forwarding session when firewall administration
is complete.

## 10. Operational Monitoring

Execute the centralized Python monitoring utility from Ubuntu:

```bash
python3 scripts/monitor_infrastructure.py
```

The monitoring report contains:

- Application health status.
- HTTP response codes.
- Response latency.
- Operational container status.
- Storage capacity and utilization.
- Overall infrastructure health.

### Monitoring Exit Codes

| Exit code | Interpretation |
|---|---|
| 0 | All monitored infrastructure checks passed |
| 1 | One or more infrastructure checks failed |

The storage warning threshold is 90 percent utilization.

An unsuccessful remote administration check produces a degraded
monitoring result even when the HTTP endpoints remain healthy.

Monitoring results therefore need to be interpreted in conjunction
with SSH authentication and infrastructure availability.

## 11. Windows-Based Infrastructure Orchestration

The PowerShell orchestration utility provides a centralized administrative
entry point from the Windows project repository.

### Virtual Machine Status

```powershell
.\scripts\manage_infrastructure.ps1 -Action Status
```

Requires appropriate Hyper-V administrative permissions.

### Deployment Syntax Validation

```powershell
.\scripts\manage_infrastructure.ps1 -Action Validate
```

Validates the application deployment playbooks without deploying them.

### Infrastructure Monitoring

```powershell
.\scripts\manage_infrastructure.ps1 -Action Monitor
```

Requires an active Ubuntu authentication agent and an operational
enterprise API SSH tunnel.

### Application Deployment

```powershell
.\scripts\manage_infrastructure.ps1 -Action Deploy
```

Executes both application deployment playbooks using the existing
Ubuntu-to-Rocky authentication identity.

This action may change infrastructure configuration when required.

The default PowerShell action is read-only virtual machine status
inspection.

## 12. Application Container Administration

From Ubuntu, inspect the Rocky container inventory:

```bash
ssh -o BatchMode=yes \
-o StrictHostKeyChecking=yes \
-o IdentitiesOnly=yes \
-i ~/.ssh/lab_automation_ed25519 \
labadmin@10.20.20.10 'podman ps -a'
```

Expected operational containers:

| Container | Expected state |
|---|---|
| enterprise-health | Running |
| enterprise-api | Running |

Stopped recovery and rollback containers are retained separately.

They must not be started indiscriminately, particularly when they
reference the same persistent application data.

### Inspect Application Logs

```bash
ssh -o BatchMode=yes \
-o StrictHostKeyChecking=yes \
-o IdentitiesOnly=yes \
-i ~/.ssh/lab_automation_ed25519 \
labadmin@10.20.20.10 \
'podman logs --tail 30 enterprise-api'
```

Review startup errors and application failures before attempting
configuration changes.

## 13. Application Upgrade and Rollback

The health service supports controlled image version upgrades through:

```text
playbooks/upgrade_application.yml
```

The upgrade automation validates the target application version and
preserves the existing network exposure configuration.

A failed validation triggers the rollback mechanism.

Existing image availability, container identity, network configuration
and application health must be inspected before initiating an upgrade.

The rollback procedure has been exercised using an independent test
container and an intentionally incorrect expected application version.

The original operational application and protected recovery containers
were preserved during rollback testing.

The enterprise API has separate deployment and data recovery procedures.
The health service upgrade procedure must not be applied indiscriminately
to the enterprise API.

## 14. Backup and Disaster Recovery

The reusable backup and restoration utilities are:

```text
scripts/backup_enterprise_api.py
scripts/restore_enterprise_api.py
```

Backup creation requires a controlled enterprise API maintenance window
to preserve consistency across both databases and the security audit log.

Restoration must use independent recovery storage unless a separately
planned production-style recovery operation explicitly requires
replacement of operational data.

The detailed procedures are documented in:

[Backup and Recovery](backup-and-recovery.md)

## 15. Troubleshooting

### SSH Authentication Failure

Symptoms:

- Rocky administration fails.
- Ansible reports an unreachable host.
- Monitoring reports CalledProcessError.
- HTTP endpoints may remain healthy.

Required checks:

1. Verify the management server is running.
2. Verify the Rocky application server is running.
3. Verify the SSH agent contains the correct automation identity.
4. Verify the stable authentication socket reference.
5. Verify strict host key authentication succeeds.

Do not remove key passphrase protection or disable host key verification
to resolve authentication failures.

### Hyper-V Permission Failure

Symptoms:

- PowerShell reports insufficient permissions when executing Get-VM.

Required action:

Use an appropriately authorized Windows administrative session for the
Hyper-V status inspection.

Routine source editing and remote application monitoring do not require
an elevated Windows session.

### Enterprise API Health Failure

Required checks:

1. Verify the enterprise API container is running.
2. Inspect the container startup logs.
3. Verify the operational persistent volume exists.
4. Verify database ownership and permissions.
5. Verify the Rocky loopback port publication.
6. Verify the Ubuntu SSH tunnel.

A failed management-side request does not independently establish that
the application itself is unavailable.

### DNS Isolation Validation Failure

Inspect the application resolver configuration without performing external
DNS queries.

The enterprise API requires the explicitly empty, read-only resolver
configuration maintained by its deployment playbook.

Unexpected public DNS entries must be investigated and corrected.
Their presence alone does not establish that external communication
has occurred.

### Unexpected Deployment Configuration

The deployment playbooks may reject noncompliant existing containers.

Investigate the failed assertion before replacing any container.

Preserve persistent application data and recovery resources.

Do not use broad container or volume cleanup commands to resolve a
specific configuration discrepancy.

### Storage Capacity Warning

The monitoring utility reports degraded infrastructure when the monitored
filesystem reaches 90 percent utilization.

Review storage consumption, retained backups, image archives and
container resources.

Do not delete persistent databases, backup directories or retained
rollback resources without confirming their purpose and recovery
requirements.

### Incorrect Terminal Syntax

Windows PowerShell and Linux Bash use different command syntax.

PowerShell commands must execute from the Windows terminal.

Linux shell commands, Ansible commands and Bash heredocs must execute
from the appropriate Linux session.

A shell parser error does not independently indicate an infrastructure
failure.

## 16. Controlled Infrastructure Shutdown

Before shutting down the laboratory, complete active administrative
operations and confirm that no backup or restoration process is running.

Stop the two operational containers gracefully from the Rocky server:

```bash
podman stop --time 30 enterprise-api
podman stop --time 30 enterprise-health
```

The commands should be executed under the dedicated rootless Podman
administrative account.

Verify the containers have stopped before powering down the application
server.

Shut down the virtual machines in the following order:

1. Rocky Linux application server.
2. Ubuntu management server.
3. OPNsense firewall.

Use the guest operating system's normal shutdown mechanism.

Avoid abrupt virtual machine power-off operations during normal
maintenance.

The application and recovery volumes must be preserved.

## 17. Post-Startup Recovery

After restarting the laboratory:

1. Verify all required virtual machines are running.
2. Establish Ubuntu management access.
3. Initialize the SSH authentication agent.
4. Refresh the stable authentication socket reference.
5. Verify Rocky connectivity.
6. Execute both application deployment playbooks.
7. Re-establish the enterprise API SSH tunnel.
8. Execute centralized infrastructure monitoring.

The deployment automation can start existing compliant containers
when they are stopped.

The laboratory does not claim fully unattended recovery from every
possible physical host or virtual machine failure.

## 18. Operational Safety Requirements

All administrative operations must remain within the owned laboratory
environment.

The following restrictions apply:

- No testing against third-party infrastructure.
- No intentional external network scanning.
- No external container image pulling during deployment.
- No unapproved cloud infrastructure provisioning.
- No real enterprise or employer data.
- No publication of authentication material.
- No unreviewed destructive storage operations.
- No automatic removal of recovery resources.

Application health monitoring is intentionally lightweight and local.

The procedures documented here do not replace production change
management, enterprise access governance or formal incident response
requirements.