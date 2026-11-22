# Security Controls and Validation

## 1. Security Objectives

The infrastructure implements a defence-in-depth approach to enterprise
infrastructure security within a controlled local laboratory.

The primary security objectives are:

- Minimize unnecessary network exposure.
- Separate infrastructure administration from application hosting.
- Enforce least-privilege application execution.
- Protect persistent application data.
- Restrict access to confidential enterprise information.
- Maintain security audit records.
- Support controlled application recovery.
- Avoid unnecessary dependencies on external infrastructure.

All application data and demonstration identities are fictional.

## 2. Network Segmentation

OPNsense separates the management, application and reserved compute networks.

| Network | Security purpose |
|---|---|
| Management | Controlled infrastructure administration |
| Application | Restricted application hosting |
| Compute | Reserved isolated computing segment |
| Host management | Private Windows-to-Ubuntu administration |
| Isolated WAN | Firewall interface without an upstream gateway |

The application server does not have a configured default IPv4 or IPv6 route.

IPv4 forwarding is disabled on the Rocky Linux application server.

The laboratory uses private network addressing and does not require an
external cloud network for application operation.

## 3. Firewall Controls

Network-level filtering is implemented through OPNsense and host-level
filtering through Rocky Linux firewalld.

The application health service is exposed on TCP port 8080 through
restricted network access rules.

The Rocky host firewall restricts health service access to the authorized
management server source address.

| Control | Configuration |
|---|---|
| Authorized management source | 10.20.10.10 |
| Application destination | 10.20.20.10 |
| Health service port | TCP 8080 |
| Enterprise API host binding | 127.0.0.1:18000 |
| Host firewall | Active |
| Unnecessary application exposure | Restricted |

Network validation included successful authorized health requests and
unsuccessful connections to unauthorized application ports.

The enterprise API could not be accessed directly from the management
server through the application server address on TCP port 18000.

## 4. Administrative Access Security

Infrastructure administration uses SSH with strict host key verification.

The Ubuntu management server authenticates to Rocky Linux through a
dedicated passphrase-protected ED25519 identity.

Implemented controls include:

- Dedicated laboratory administration account.
- Explicit SSH identity selection.
- SSH host key verification.
- Non-interactive authentication for automated Rocky administration.
- Passphrase-protected private key material.
- Local SSH authentication agent.
- Restricted authentication socket directory.
- No stored passwords in automation scripts.
- No requirement for SSH agent forwarding.

The Windows orchestration utility references an existing authentication
agent through a protected symbolic link on Ubuntu.

This reference must be refreshed after the authentication agent is replaced
or the management server is restarted.

Access to the active agent socket permits authentication using its loaded
identity. The socket must therefore remain restricted to the authorized
management account.

## 5. Linux Host Security

The Rocky Linux application server implements the following baseline controls.

| Security control | Final verified state |
|---|---|
| SELinux | Enforcing |
| SSH service | Active |
| Host firewall | Active |
| IPv4 forwarding | Disabled |
| Default IPv4 route | Absent |
| Default IPv6 route | Absent |
| Podman runtime | Rootless |

SELinux remains enabled during application deployment, backup and recovery.

Container storage and dedicated configuration mounts use appropriate
SELinux volume labeling rather than disabling mandatory access controls.

## 6. Container Runtime Hardening

Both operational applications run using rootless Podman.

| Runtime control | Health service | Enterprise API |
|---|---|---|
| Application UID | 10001 | 10001 |
| Application GID | 10001 | 10001 |
| Root filesystem | Read-only | Read-only |
| Linux capabilities | Dropped | Dropped |
| Privilege escalation | Disabled | Disabled |
| Memory limit | 128 MiB | 256 MiB |
| Process limit | 32 | 32 |
| External image pulls | Prohibited | Prohibited |
| Container networking | Internal bridge | Internal bridge |

The enterprise API deployment additionally validates actual process
capabilities through the Linux process status interface.

### Verified Enterprise API Process Security

| Process attribute | Verified value |
|---|---|
| CapInh | 0000000000000000 |
| CapPrm | 0000000000000000 |
| CapEff | 0000000000000000 |
| CapBnd | 0000000000000000 |
| CapAmb | 0000000000000000 |
| NoNewPrivs | 1 |

Runtime verification provides stronger evidence than relying exclusively
on declared container configuration.

## 7. Container Network Isolation

The two operational applications use separate internal container networks.

| Application | Network | Subnet |
|---|---|---|
| Health service | enterprise-private | 10.89.50.0/24 |
| Enterprise API | enterprise-api-private | 10.89.60.0/24 |

The enterprise API network is configured with internal networking and
container network DNS disabled.

The enterprise API runtime was independently verified to have:

- No default IPv4 route.
- No active default IPv6 route.
- An empty resolver configuration.
- Restricted loopback port publishing.

Temporary backup, restoration and recovery validation containers use
network-disabled execution.

## 8. DNS Configuration Remediation

During enterprise API migration, runtime validation identified public
resolver addresses inside the imported application container despite
the internal network configuration and DNS restrictions.

The resolver configuration contained public DNS server addresses, while
the Rocky host resolver configuration was empty.

This discrepancy did not establish that external DNS communication had
occurred.

The issue was remediated by:

1. Creating a dedicated empty resolver configuration.
2. Restricting its filesystem permissions.
3. Mounting it read-only at /etc/resolv.conf.
4. Recreating the application container with the corrected configuration.
5. Revalidating network routes, resolver contents and application health.
6. Incorporating the configuration into Ansible deployment automation.

The corrected application passed all subsequent resolver and network
isolation validations.

No external DNS queries were deliberately performed during remediation.

## 9. Encrypted Enterprise API Access

The enterprise API is published exclusively on the Rocky host loopback
interface.

Access from the Ubuntu management server is provided through SSH
local port forwarding.

This design avoids opening an additional firewall port and encrypts
application requests between the management and application servers.

The following access paths were verified:

| Access path | Result |
|---|---|
| Rocky loopback health request | Successful |
| Ubuntu SSH tunnel health request | Successful |
| Authenticated requests through SSH tunnel | Successful |
| Direct access to Rocky TCP 18000 from Ubuntu | Unsuccessful |

Application-level authentication remains required for protected resources,
including requests originating through the encrypted tunnel.

The SSH tunnel is an administrative access mechanism, not a replacement
for application authorization.

## 10. Application Authentication and Authorization

The integrated enterprise API uses a centralized identity registry and
explicit role-based permissions.

Authentication is implemented using fictional demonstration credentials.

| Role | Public documents | Confidential documents | Finance reports | Ingestion monitoring |
|---|---|---|---|---|
| Finance | Allowed | Allowed | Allowed | Allowed |
| Strategy | Allowed | Denied | Denied | Denied |
| Employee | Allowed | Denied | Denied | Denied |
| AI service | Denied | Denied | Denied | Denied |
| Unauthenticated | Denied | Denied | Denied | Denied |

The API applies explicit permission checks and denies unknown roles or
permissions by default.

Confidential document access is restricted to Finance identities.

### Authentication and Authorization Test Results

| Test category | Successful validations |
|---|---:|
| Authorized requests | 5 |
| Insufficient permission rejection | 9 |
| Missing or invalid authentication rejection | 3 |
| Unknown document handling | 1 |
| Total | 18 |

All 18 isolated application security tests passed.

Six additional authentication and authorization tests passed through
the encrypted SSH management tunnel.

These tests validate the exercised application endpoints rather than
every possible security property of the backend.

## 11. Security Audit Logging

Security audit records are stored within the persistent application volume.

The audit mechanism records access decisions, identity roles,
resource identifiers and timestamps.

An initial security validation produced:

| Audit outcome | Events |
|---|---:|
| Allowed | 5 |
| Denied | 12 |
| Total | 17 |

Audit validation confirmed:

- Valid JSON records.
- Expected access decisions.
- Application-owned persistent storage.
- No detected exposure of the tested plaintext demonstration credentials.

The subsequent encrypted access validation generated six additional
audit records.

A total of 23 historical audit events were included in the enterprise
application backup.

The nonexistent document test returned HTTP 404 before reaching the
access logging functions. Accordingly, the initial 18 requests produced
17 audit events.

## 12. Persistent Data Security

Application databases are stored independently of the container filesystem.

| Storage property | Verified configuration |
|---|---|
| Operational persistent volume | enterprise-api-data |
| Recovery persistent volume | enterprise-api-recovery |
| Volume directory ownership | UID/GID 10001 |
| Volume directory permissions | 0700 |
| Database ownership | UID/GID 10001 |
| Database file permissions | 0600 |

Both persistent SQLite databases passed integrity validation.

Operational data was retained following container replacement.

The recovery application used independent persistent storage and did
not mount the operational database volume.

## 13. Backup and Recovery Security

The backup utility uses SQLite's native backup functionality and
read-only access to operational database files.

Backup protections include:

- Controlled application shutdown for consistent backup creation.
- Read-only operational data mounts.
- Network-disabled backup execution.
- Restrictive backup directory permissions.
- Restrictive backup file permissions.
- SQLite integrity validation.
- SHA-256 file integrity manifests.
- Unique backup timestamps.
- Cleanup of incomplete backup creation attempts.

Restoration requires verification of the expected file inventory,
file sizes and SHA-256 checksums before copying data.

The restoration utility refuses to overwrite an existing recovery
environment.

The checksum manifest detects file corruption but is not digitally
signed and does not authenticate the backup against a malicious party
with write access.

## 14. Recovery Environment Isolation

The recovery exercise restored:

- 174 financial transactions.
- Five departmental projects.
- 23 historical security audit records.

The independent recovery application generated seven additional audit
events during functional testing.

The operational and recovery audit logs were independently inspected.

| Environment | Audit events |
|---|---:|
| Operational enterprise API | 23 |
| Recovery enterprise API | 30 |

The operational audit history remained unchanged during recovery testing.

The recovery application was gracefully stopped after validation, while
its restored volume was retained.

Both operational applications remained available during the independent
recovery exercise.

## 15. Infrastructure Automation Security

Ansible deployment automation implements explicit configuration
assertions and controlled reconciliation.

The enterprise API deployment validates:

- Availability of the locally imported image.
- Existing persistent database storage.
- Persistent directory ownership and permissions.
- Internal network configuration.
- Container resource restrictions.
- Container execution identity.
- Restricted port publishing.
- Persistent storage mounts.
- Read-only resolver configuration.
- Actual Linux process capabilities.
- Privilege escalation restrictions.
- Application health.

Unexpected container configuration causes deployment validation to fail
rather than automatically replacing the existing application.

Repeated execution demonstrated unchanged container identity and startup
timestamp, with zero reported Ansible changes.

## 16. Repository and Credential Protection

The Git repository excludes sensitive and generated infrastructure
artifacts through its .gitignore configuration.

Excluded categories include:

- Private keys and credential files.
- Environment secrets.
- Local SSH authentication material.
- Virtual machine disks and installation media.
- Container image archives.
- Application databases.
- Backup resources.
- Operational logs.
- Network captures.
- Python virtual environments.
- Generated operational reports.

A local source inspection checked for common credential assignment
patterns, private key markers and selected access token formats.

No matching sensitive credential patterns were detected.

Pattern-based inspection is a preliminary security control and does
not guarantee that every possible secret has been identified.

Repository publication requires a separate review of the final staged
content and selected evidence files.

## 17. External Communication Restrictions

Application deployment uses locally available container images with
external image pulling prohibited.

The container networks are internally configured, and the application
server has no default IPv4 or IPv6 route.

The enterprise API explicitly disables the OpenTelemetry SDK through
its runtime environment configuration.

Monitoring, backup and recovery utilities do not intentionally use
external services or cloud APIs.

No third-party systems were targeted during application security tests.

These controls describe the intended architecture and verified
laboratory configuration. They do not establish a universal guarantee
against unrelated operating system monitoring, host software telemetry
or every possible external communication mechanism.

## 18. Security Limitations

This infrastructure is a controlled laboratory implementation.

It is not intended to be represented as a production-certified or
formally audited enterprise security platform.

Remaining production considerations include:

- Enterprise identity federation and multifactor authentication.
- Centralized secret management.
- Production credential lifecycle policies.
- Signed and independently protected backup manifests.
- Encrypted off-site backup storage.
- Comprehensive vulnerability management.
- Centralized security monitoring.
- Tamper-resistant audit storage.
- Formal penetration testing and threat modelling.
- Independent compliance assessment.
- Multi-host infrastructure redundancy.

Demonstration credentials must not be reused in production environments.

The verified controls apply to the specific configuration and tests
documented in this repository.