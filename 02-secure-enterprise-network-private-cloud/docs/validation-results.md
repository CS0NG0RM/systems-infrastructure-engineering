# Engineering Validation Results

## 1. Validation Overview

The secure enterprise network and private cloud infrastructure was
validated through automated unit tests, infrastructure inspections,
application security tests, controlled failure scenarios, deployment
reconciliation and independent disaster recovery exercises.

All validation activities were restricted to the locally managed
laboratory infrastructure using fictional enterprise data.

The results document observed behaviour under the tested configuration.
They do not represent production certification or formal security
compliance assessment.

## 2. Virtual Infrastructure Validation

| Component | Verified result |
|---|---|
| Hyper-V virtualization | Operational |
| OPNsense firewall | Running |
| Ubuntu management server | Running |
| Rocky Linux application server | Running |
| Centralized virtual machine inspection | Passed |
| Total assigned virtual machine memory | 5632 MiB |

Three dedicated virtual machines were deployed and administered
successfully through the local Hyper-V environment.

Virtual machine status was also retrieved through the centralized
PowerShell management utility.

## 3. Network Infrastructure Validation

| Validation | Result |
|---|---|
| Management network configuration | Passed |
| Application network configuration | Passed |
| Reserved compute network configuration | Configured |
| Windows-to-Ubuntu administrative connectivity | Passed |
| Ubuntu-to-Rocky SSH connectivity | Passed |
| Authorized application health access | Passed |
| Unauthorized application port access | Blocked |
| Restricted enterprise API port publishing | Passed |
| SSH tunnel connectivity | Passed |
| Direct enterprise API network access from Ubuntu | Blocked |

The application network was reachable through explicitly permitted
administrative and service communication paths.

The reserved compute network was configured but was not populated
with distributed computing workloads.

## 4. Linux Security Baseline

The final Rocky Linux security inspection produced the following
results.

| Security control | Verified state |
|---|---|
| Server hostname | labapp01 |
| SELinux | Enforcing |
| SSH service | Active |
| Host firewall | Active |
| IPv4 forwarding | Disabled |
| Default IPv4 route | Absent |
| Default IPv6 route | Absent |
| Container runtime | Rootless Podman |

The final live security inspection completed successfully.

## 5. Automated Python Unit Tests

The repository includes three automated test modules.

| Test module | Tests | Passed |
|---|---:|---:|
| test_health_service.py | 9 | 9 |
| test_service_lifecycle.py | 3 | 3 |
| test_validator.py | 6 | 6 |
| Total | 18 | 18 |

Final execution result:

```text
Ran 18 tests in 0.074s

OK
```

### Health Service Tests

| Test | Result |
|---|---|
| Data classification | Passed |
| Health endpoint | Passed |
| Health status | Passed |
| Absence of sensitive metadata fields | Passed |
| Root endpoint | Passed |
| Service identity | Passed |
| Undefined administrative endpoint | Passed |
| Unknown endpoint | Passed |
| Non-negative uptime | Passed |

### Application Lifecycle Tests

| Test | Result |
|---|---|
| Duplicate shutdown requests | Passed |
| Shutdown signal registration | Passed |
| Separate shutdown execution thread | Passed |

### Infrastructure Validator Tests

| Test scenario | Expected successful checks | Result |
|---|---:|---|
| Compliant server | 8/8 | Passed |
| Simulated connection timeout | 7/8 | Passed |
| Simulated inactive firewall | 7/8 | Passed |
| Simulated enabled IPv4 forwarding | 7/8 | Passed |
| Simulated disabled SELinux | 7/8 | Passed |
| Simulated unexpected default route | 7/8 | Passed |

The deliberately noncompliant scenarios were expected to produce
individual failed infrastructure checks.

The resulting 7/8 validation scores confirm that the validator
recognized the simulated failures correctly.

All six infrastructure validator unit tests passed.

These simulated conditions must not be confused with failures in
the operational infrastructure.

## 6. Offline Container Engineering

The project implemented offline container image preparation,
application image building and deployment using locally available
artifacts.

The health application was deployed through a locally prepared
Python container image.

The enterprise backend was migrated from an existing Docker-based
application environment into rootless Podman.

Transfer integrity was verified using SHA-256 checksums before
importing the enterprise API image.

### Enterprise API Runtime Compatibility

| Component | Verified result |
|---|---|
| Operating system architecture | Linux amd64 |
| Python runtime | 3.13.18 |
| FastAPI | 0.163.1 |
| Uvicorn | 0.54.0 |
| Application UID/GID | 10001:10001 |
| Python dependency consistency | Passed |
| Offline image execution | Passed |

The imported image was executed successfully without downloading
additional dependencies.

## 7. Container Runtime Security Validation

The enterprise API application process was independently inspected.

| Linux capability attribute | Verified value |
|---|---|
| CapInh | 0000000000000000 |
| CapPrm | 0000000000000000 |
| CapEff | 0000000000000000 |
| CapBnd | 0000000000000000 |
| CapAmb | 0000000000000000 |
| NoNewPrivs | 1 |

Additional verified configuration:

- Rootless container execution.
- Non-root application identity.
- Read-only root filesystem.
- Restricted memory allocation.
- Restricted process count.
- Explicitly controlled network exposure.
- Persistent storage mounted separately.
- External image pulling disabled.

The Ansible deployment automation validates actual Linux process
capabilities in addition to container configuration metadata.

## 8. Application Deployment and Lifecycle Validation

The health service implementation supports controlled deployment,
version management, graceful shutdown and rollback.

| Validation | Result |
|---|---|
| Initial application deployment | Passed |
| Application version upgrade | Passed |
| Graceful shutdown | Passed |
| Private network migration | Passed |
| Automated application health verification | Passed |
| Automated rollback exercise | Passed |
| Existing application preservation during rollback | Passed |
| Deployment reconciliation | Passed |

The final operational health service version was 1.0.1.

### Controlled Rollback Exercise

A disposable application container was used to exercise rollback
against an intentionally incorrect expected target version.

The target version validation failed as intended.

The rollback mechanism restored the original disposable container,
network configuration, published endpoint and healthy application
response.

The operational health application and protected recovery containers
retained their original identities and recorded startup timestamps
during the disposable rollback exercise.

The expected deployment failure was part of the controlled test,
not an unexpected operational incident.

## 9. Persistent Enterprise Data Validation

Fresh application databases were initialized using the original
enterprise backend initialization functions.

| Validation | Result |
|---|---|
| Enterprise database initialization | Passed |
| Identity database initialization | Passed |
| Financial schema creation | Passed |
| Departmental project schema creation | Passed |
| Ingestion history initialization | Passed |
| Identity registry initialization | Passed |
| Financial dataset transfer integrity | Passed |
| Project dataset transfer integrity | Passed |
| Enterprise database integrity | Passed |
| Identity database integrity | Passed |

### Imported Enterprise Records

| Data category | Expected | Actual |
|---|---:|---:|
| Financial transactions | 174 | 174 |
| Departmental projects | 5 | 5 |
| Total enterprise records | 179 | 179 |

Database files were verified to have ownership UID/GID 10001
and restrictive permissions of 0600.

The records remained available following application container
replacement and private network migration.

## 10. Enterprise API Authentication and Authorization

The enterprise API was initially deployed with networking disabled.

Application requests were executed exclusively through the
container's own loopback interface.

| Test | Expected HTTP status | Actual |
|---|---:|---:|
| Anonymous public document request | 401 | 401 |
| Invalid credential request | 401 | 401 |
| Employee public document access | 200 | 200 |
| Employee confidential document access | 403 | 403 |
| Strategy public document access | 200 | 200 |
| Strategy confidential document access | 403 | 403 |
| Finance confidential document access | 200 | 200 |
| AI service public document access | 403 | 403 |
| Finance financial report access | 200 | 200 |
| Strategy financial report access | 403 | 403 |
| Employee financial report access | 403 | 403 |
| AI service financial report access | 403 | 403 |
| Anonymous financial report access | 401 | 401 |
| Finance ingestion monitoring access | 200 | 200 |
| Strategy ingestion monitoring access | 403 | 403 |
| Employee ingestion monitoring access | 403 | 403 |
| AI service ingestion monitoring access | 403 | 403 |
| Unknown document request | 404 | 404 |

Final result: 18/18 security test cases passed.

The tests demonstrate the authentication and authorization behaviour
of the exercised endpoints under the implemented laboratory policy.

They do not constitute comprehensive penetration testing of the
entire application.

## 11. Security Audit Validation

The initial enterprise API security test suite generated 17
persistent audit events.

| Access decision | Events |
|---|---:|
| Allowed | 5 |
| Denied | 12 |
| Total | 17 |

The unknown document request returned HTTP 404 before reaching
the access logging functions.

Audit verification confirmed:

- Valid JSON records.
- Expected access decisions.
- Persistent application-owned storage.
- Recorded identity roles and resources.
- No detected exposure of the tested plaintext credentials.

Six subsequent authenticated and unauthenticated management
requests generated six additional security audit events.

A total of 23 historical security audit records were included
in the application backup.

## 12. Enterprise API Network Isolation

The enterprise API was migrated from a network-disabled container
to a dedicated internal container network.

| Network control | Final verified configuration |
|---|---|
| Network | enterprise-api-private |
| Subnet | 10.89.60.0/24 |
| Network driver | Bridge |
| Internal network | Enabled |
| Network DNS | Disabled |
| Default IPv4 route | Absent |
| Active default IPv6 route | Absent |
| Resolver file | Empty |
| Published host address | 127.0.0.1:18000 |

### DNS Remediation

Initial runtime validation detected unexpected public DNS addresses
inside the imported application container.

The resolver discrepancy was corrected by explicitly mounting
an empty, read-only resolver configuration.

Subsequent validation confirmed that the resolver file was empty
and that application functionality and persistent data were preserved.

The discovery of resolver addresses did not establish that external
DNS queries had occurred.

No external DNS queries were deliberately performed during testing.

## 13. Encrypted Management Access

The enterprise API was made accessible from Ubuntu using SSH
local port forwarding.

| Validation | Result |
|---|---|
| Rocky loopback health request | Passed |
| Ubuntu tunnel health request | Passed |
| Anonymous protected resource rejection | Passed |
| Employee public document access | Passed |
| Employee confidential access rejection | Passed |
| Finance confidential document access | Passed |
| Finance ingestion monitoring access | Passed |
| AI service financial access rejection | Passed |
| Direct access to Rocky TCP 18000 | Blocked |

All six representative authentication and authorization cases
passed through the encrypted tunnel.

Direct access from Ubuntu to the Rocky application address
on TCP port 18000 timed out.

No additional firewall port was opened for the enterprise API.

## 14. Ansible Deployment Validation

Both operational applications were successfully reconciled through
Ansible.

### Final Centralized Deployment Results

| Metric | Health service | Enterprise API | Total |
|---|---:|---:|---:|
| Successful tasks | 15 | 25 | 40 |
| Changed tasks | 0 | 0 | 0 |
| Failed tasks | 0 | 0 | 0 |
| Unreachable hosts | 0 | 0 | 0 |
| Skipped tasks | 3 | 3 | 6 |

The final centralized deployment was initiated from Windows
through the PowerShell management utility.

### Idempotency Verification

Repeated enterprise API deployment confirmed:

- Unchanged container identity.
- Unchanged application startup timestamp.
- Zero reported configuration changes.
- Successful application health verification.

This establishes idempotent reconciliation against the tested
compliant deployment.

The deployment playbooks do not automatically resolve every
possible configuration discrepancy.

## 15. Backup and Disaster Recovery Validation

The enterprise API backup included both SQLite databases and
the persistent security audit log.

| Backup validation | Result |
|---|---|
| SQLite native backup execution | Passed |
| Enterprise backup database integrity | Passed |
| Identity backup database integrity | Passed |
| Audit record preservation | Passed |
| SHA-256 integrity manifest creation | Passed |
| Application restart after backup | Passed |
| Post-backup API health | Passed |

An independent recovery volume was prepared without overwriting
the operational application storage.

### Restoration Results

| Recovery metric | Expected | Recovered |
|---|---:|---:|
| Protected file checksums | 3 | 3 |
| Financial transactions | 174 | 174 |
| Departmental projects | 5 | 5 |
| Historical security audit events | 23 | 23 |

Both recovered SQLite databases passed integrity validation.

### Functional Recovery

The recovery application successfully started using the restored
persistent storage in a network-disabled container.

Recovery testing exercised authentication, authorization, financial
reporting, ingestion monitoring and audit generation.

Seven additional audit records were generated within the recovery
environment.

Independent inspection established:

| Environment | Security audit records |
|---|---:|
| Operational enterprise API | 23 |
| Independent recovery environment | 30 |

The operational audit history remained unchanged.

The recovery container was gracefully stopped and its persistent
volume retained after the exercise.

Both operational applications remained available during the
independent recovery exercise.

The backup itself required a controlled maintenance interruption.

## 16. Operational Monitoring Validation

The centralized Python monitoring utility was validated against
both healthy and deliberately interrupted infrastructure.

| Monitoring capability | Result |
|---|---|
| HTTP service availability | Passed |
| Application health validation | Passed |
| Response latency measurement | Passed |
| Container status inspection | Passed |
| Storage capacity inspection | Passed |
| Healthy infrastructure exit code | Passed |
| Degraded infrastructure exit code | Passed |
| Controlled failure detection | Passed |
| Recovery recognition | Passed |
| Structured JSON reporting | Passed |

### Final Live Monitoring Snapshot

| Metric | Observed result |
|---|---|
| Health service HTTP status | 200 |
| Health service response latency | 4.17 ms |
| Enterprise API HTTP status | 200 |
| Enterprise API response latency | 44.39 ms |
| Operational containers | 2/2 running |
| Total monitored filesystem capacity | 34.39 GiB |
| Available filesystem capacity | 31.44 GiB |
| Filesystem utilization | 9% |
| Storage warning threshold | 90% |
| Overall infrastructure status | Healthy |

The latency measurements are individual laboratory observations,
not statistically representative performance benchmarks.

## 17. PowerShell Orchestration Validation

The centralized Windows management utility implements four
administrative actions.

| Action | Validation result |
|---|---|
| Status | Passed |
| Validate | Passed |
| Monitor | Passed |
| Deploy | Passed |

The Hyper-V status function required an authorized Windows
administrative session.

A session-specific SSH agent authentication issue was identified
during centralized monitoring.

The issue was resolved through a protected local reference to
the existing Ubuntu authentication agent.

The corrected monitoring and deployment functions were subsequently
executed successfully.

No key passphrase removal, stored passwords or SSH agent forwarding
was required.

## 18. Engineering Issues and Remediation

| Issue | Remediation | Final result |
|---|---|---|
| Application graceful shutdown behaviour | Revised signal handling and lifecycle validation | Passed |
| Rootless application lifecycle after logout | Enabled and validated user lingering configuration | Passed in exercised configuration |
| Incorrect CSV volume reference | Corrected filesystem bind mount and removed unintended volume | Passed |
| Unexpected container DNS configuration | Explicit empty read-only resolver mount | Passed |
| Incorrect Ansible inventory group | Corrected deployment host group | Passed |
| Null capability metadata returned by Podman | Corrected metadata handling and added process-level validation | Passed |
| Hyper-V inspection permission restriction | Used authorized administrative session | Passed |
| SSH agent unavailable in independent session | Implemented protected stable authentication reference | Passed |

These issues were identified through incremental validation and
resolved without discarding the established operational data.

## 19. Repository Security Inspection

The repository was inspected for selected sensitive credential
patterns before final documentation preparation.

| Inspection category | Result |
|---|---|
| Private key markers | None detected |
| Password assignment patterns | None detected |
| API secret assignment patterns | None detected |
| Access token assignment patterns | None detected |
| Selected GitHub token patterns | None detected |
| Selected AWS access key patterns | None detected |

Sensitive and generated runtime artifacts are excluded through
repository ignore rules.

Pattern-based source inspection does not establish the absence
of every possible secret.

A separate review of final staged content and selected evidence
is required before public publication.

## 20. Final Engineering Acceptance Summary

| Engineering domain | Final status |
|---|---|
| Virtual infrastructure | Validated |
| Network segmentation | Validated |
| Linux security baseline | Validated |
| Rootless container deployment | Validated |
| Automated Python tests | 18/18 passed |
| Enterprise API security tests | 18/18 passed |
| Encrypted access security tests | 6/6 passed |
| Persistent enterprise data | 179/179 records retained |
| Application deployment and rollback | Validated |
| Ansible deployment reconciliation | 40 successful tasks, zero changes and failures |
| Backup and independent restoration | Validated |
| Recovery data separation | Validated |
| Monitoring failure and recovery detection | Validated |
| PowerShell orchestration | 4/4 functions validated |
| Final live infrastructure health | Healthy |

## 21. Validation Limitations

The project demonstrates practical infrastructure engineering
within the defined laboratory scope.

The following claims are not established by the completed tests:

- Production-grade availability guarantees.
- Comprehensive application vulnerability assessment.
- Formal regulatory compliance.
- Resistance to every possible network attack.
- Complete absence of unrelated host software telemetry.
- Protection against physical host or storage loss.
- Multi-host infrastructure failover.
- Formal recovery time or recovery point objectives.
- Production performance and scalability guarantees.

The automated tests, manual validation exercises and observed
runtime results apply to the specific implemented configuration.

Further production adoption would require additional architectural,
operational and independent security assessment.

## 22. Supporting Documentation

- [Infrastructure Architecture](architecture.md)
- [Security Controls](security-controls.md)
- [Operations Runbook](operations-runbook.md)
- [Backup and Disaster Recovery](backup-and-recovery.md)
- [Evidence Index](evidence-index.md)