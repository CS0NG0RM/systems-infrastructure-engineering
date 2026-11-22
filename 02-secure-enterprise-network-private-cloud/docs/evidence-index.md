# Engineering Evidence Index

## 1. Overview

This document provides a structured record of the technical evidence collected during the design, implementation, security hardening and operational validation of the Secure Enterprise Network & Private Cloud Infrastructure project.

The evidence covers the complete infrastructure engineering lifecycle, including virtualization, network segmentation, Linux administration, container engineering, infrastructure automation, application security, disaster recovery and operational monitoring.

The public repository contains **50 curated engineering screenshots**, linked directly from the tables below. The separate local working archive retains **67 original screenshots**, including implementation-stage and supplementary records not selected for publication.

Each evidence reference documents a specific technical configuration, implementation activity, test scenario or observed validation result.

The curated evidence is published in the repository's [`evidence/`](../evidence/) directory. Each linked file opens the actual screenshot. The full original archive remains local and is not published in its entirety.

## 2. Evidence Organization and Methodology

The evidence collection was structured to preserve traceability between implemented infrastructure components, engineering activities and verification results.

The collection covers:

- **Infrastructure provisioning:** Hyper-V virtual machines, virtual switches and operating system configuration.
- **Network engineering:** Private network segmentation, IP addressing, routing and firewall enforcement.
- **Systems administration:** Linux host configuration, SSH access and security hardening.
- **Container engineering:** Offline image construction, rootless container execution and runtime restrictions.
- **Application lifecycle management:** Deployment automation, upgrades, graceful shutdown and rollback.
- **Enterprise backend integration:** Persistent databases, application migration and controlled data ingestion.
- **Application security:** Authentication, authorization, data access restrictions and audit logging.
- **Disaster recovery:** Backup integrity, independent restoration and recovered application functionality.
- **Operational engineering:** Infrastructure monitoring, controlled failure detection and centralized administration.
- **Final verification:** Automated regression testing and live infrastructure security validation.

The standardized evidence filenames retain their original implementation references where applicable.

The original, uncurated screenshots are retained in the local evidence archive. The selected 50 screenshots are included in the public Git repository.

## 3. Virtual Infrastructure and Network Configuration

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 02 | [02-opnsense-network-configuration.png](../evidence/02-opnsense-network-configuration.png) | OPNsense network interfaces and segmentation |
| 03 | [03-opnsense-routing-isolation.png](../evidence/03-opnsense-routing-isolation.png) | Routing isolation and restricted network connectivity |
| 04 | [04-opnsense-operational-dashboard.png](../evidence/04-opnsense-operational-dashboard.png) | Operational firewall infrastructure |
| 08 | [08-rocky-linux-segment-routing-configuration.png](../evidence/08-rocky-linux-segment-routing-configuration.png) | Static application network routing |
| 10 | [10-firewall-policy-enforcement.png](../evidence/10-firewall-policy-enforcement.png) | OPNsense firewall policy enforcement |
| 13 | [13-opnsense-packet-filter-status.png](../evidence/13-opnsense-packet-filter-status.png) | Packet-filter status and operational statistics |
| 14 | [14-rocky-linux-ssh-and-firewall-verification.png](../evidence/14-rocky-linux-ssh-and-firewall-verification.png) | SSH and host firewall validation |
| 15 | [15-key-based-automation-validation.png](../evidence/15-key-based-automation-validation.png) | SSH key-based infrastructure automation |

### Engineering Outcome

The infrastructure was established using three virtual machines with distinct firewall, management and application hosting responsibilities.

Private and internal Hyper-V virtual switches provided isolated network segments, while OPNsense and host-level firewall rules controlled permitted communication.

The final architecture retained separate management, application and reserved compute networks.

## 4. Offline Container Engineering

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 22 | [22-automated-offline-container-image-build.png](../evidence/22-automated-offline-container-image-build.png) | Offline container base image construction |
| 23 | [23-automated-application-container-build.png](../evidence/23-automated-application-container-build.png) | Automated application image construction |
| 25 | [25-container-runtime-security-verification.png](../evidence/25-container-runtime-security-verification.png) | Rootless container security restrictions |
| 26 | [26-automated-container-security-validation.png](../evidence/26-automated-container-security-validation.png) | Automated runtime security verification |
| 27 | [27-idempotent-container-deployment.png](../evidence/27-idempotent-container-deployment.png) | Repeatable application deployment |

### Engineering Outcome

The application infrastructure was deployed using locally available container images and rootless Podman.

Security controls included non-root execution, read-only root filesystems, dropped Linux capabilities, restricted process and memory limits, and controlled network exposure.

Repeated deployment confirmed that compliant application configurations could be reconciled without unnecessary changes.

## 5. Application Lifecycle and Release Engineering

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 28 | [28-automated-application-recovery.png](../evidence/28-automated-application-recovery.png) | Automated application recovery |
| 30 | [30-controlled-application-release-upgrade.png](../evidence/30-controlled-application-release-upgrade.png) | Controlled application version upgrade |
| 32 | [32-automated-rollback-failure-recovery.png](../evidence/32-automated-rollback-failure-recovery.png) | Automated rollback and restoration |

### Engineering Outcome

The enterprise health application was validated through controlled deployment, application upgrades, graceful shutdown and rollback exercises.

A deliberately incorrect expected application version triggered the automated recovery mechanism.

The tested rollback restored the original application configuration and healthy service state.

## 6. Network Segmentation and Application Exposure

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 33 | [33-restricted-application-network-deployment.png](../evidence/33-restricted-application-network-deployment.png) | Restricted application networking |
| 34 | [34-source-restricted-application-firewall.png](../evidence/34-source-restricted-application-firewall.png) | Source-specific host firewall configuration |
| 35 | [35-opnsense-application-access-policy.png](../evidence/35-opnsense-application-access-policy.png) | OPNsense application access rules |
| 36 | [36-authorized-cross-segment-application-connectivity.png](../evidence/36-authorized-cross-segment-application-connectivity.png) | Authorized application connectivity |
| 37 | [37-firewall-segmentation-enforcement.png](../evidence/37-firewall-segmentation-enforcement.png) | Network segmentation enforcement |
| 39 | [39-network-enabled-container-security-validation.png](../evidence/39-network-enabled-container-security-validation.png) | Container network security validation |

### Engineering Outcome

Application exposure was restricted through both OPNsense firewall policy and Rocky Linux host firewall controls.

Authorized management-to-application connectivity was verified through HTTP health requests.

Tested unauthorized communication paths were unsuccessful.

The validation distinguishes observed connection failures from independently confirmed firewall log attribution.

## 7. Permanent Application Migration and Recovery

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 40 | [40-permanent-private-application-migration.png](../evidence/40-permanent-private-application-migration.png) | Permanent application network migration |
| 41 | [41-permanent-application-deployment-idempotency.png](../evidence/41-permanent-application-deployment-idempotency.png) | Idempotent private network deployment |
| 43 | [43-private-network-automated-release-rollback.png](../evidence/43-private-network-automated-release-rollback.png) | Private network application rollback |
| 44 | [44-private-network-rollback-independent-verification.png](../evidence/44-private-network-rollback-independent-verification.png) | Independent verification of rollback preservation |

### Engineering Outcome

The application was migrated from its initial isolated runtime configuration into a restricted private container network.

Deployment automation preserved the required network configuration and application exposure.

A separate rollback exercise confirmed the restoration of a protected application instance without modifying the operational service.

## 8. Enterprise Backend Integration

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 45 | [45-offline-backend-image-export.png](../evidence/45-offline-backend-image-export.png) | Offline enterprise backend image export |
| 46 | [46-offline-docker-to-podman-image-migration.png](../evidence/46-offline-docker-to-podman-image-migration.png) | Docker-to-Podman application migration |
| 48 | [48-enterprise-persistent-database-initialization.png](../evidence/48-enterprise-persistent-database-initialization.png) | Persistent enterprise database initialization |
| 50 | [50-enterprise-financial-and-project-data-ingestion.png](../evidence/50-enterprise-financial-and-project-data-ingestion.png) | Fictional enterprise data ingestion |
| 52 | [52-enterprise-api-health-and-network-isolation.png](../evidence/52-enterprise-api-health-and-network-isolation.png) | Application health and network isolation |

### Engineering Outcome

An existing FastAPI enterprise backend was migrated from a Docker-based environment into the rootless Podman infrastructure.

The migration used an offline container image transfer with SHA-256 integrity verification.

Persistent SQLite databases were initialized and populated with 174 fictional financial transactions and five departmental project records.

Database integrity, ownership, permissions and application execution were validated independently.

## 9. Enterprise Application Security

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 53 | [53-enterprise-api-authentication-and-authorization-tests.png](../evidence/53-enterprise-api-authentication-and-authorization-tests.png) | Authentication and authorization testing |
| 54 | [54-persistent-enterprise-security-audit-validation.png](../evidence/54-persistent-enterprise-security-audit-validation.png) | Persistent security audit logging |
| 55 | [55-private-enterprise-api-deployment.png](../evidence/55-private-enterprise-api-deployment.png) | Dedicated private backend deployment |
| 56 | [56-private-api-isolation-persistence-and-loopback-validation.png](../evidence/56-private-api-isolation-persistence-and-loopback-validation.png) | Network isolation, persistent data and restricted port publishing |
| 57 | [57-enterprise-api-encrypted-management-access.png](../evidence/57-enterprise-api-encrypted-management-access.png) | Encrypted SSH application access |
| 58 | [58-encrypted-api-authorization-and-direct-access-restriction.png](../evidence/58-encrypted-api-authorization-and-direct-access-restriction.png) | Authorization through encrypted management access |

### Engineering Outcome

The enterprise API was validated using 18 isolated authentication and authorization test cases.

The tests covered permitted resource access, insufficient permissions, missing or invalid authentication and unknown document handling.

All 18 cases passed.

Six additional access-control cases were successfully tested through encrypted SSH port forwarding.

The application retained persistent security audit records and was configured for loopback-only host exposure.

## 10. Enterprise Deployment Automation

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 59 | [59-automated-enterprise-api-deployment-validation.png](../evidence/59-automated-enterprise-api-deployment-validation.png) | Automated enterprise backend deployment |
| 60 | [60-enterprise-api-deployment-idempotency.png](../evidence/60-enterprise-api-deployment-idempotency.png) | Deployment idempotency and application preservation |

### Engineering Outcome

The enterprise API deployment playbook validates image availability, persistent storage, internal networking, container security settings, process capabilities, DNS restrictions and application health.

Repeated execution confirmed that the tested compliant deployment remained unchanged.

The original container identity and startup timestamp were preserved.

## 11. Backup and Disaster Recovery

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 61 | [61-enterprise-database-backup-and-service-recovery.png](../evidence/61-enterprise-database-backup-and-service-recovery.png) | Enterprise database backup and service recovery |
| 62 | [62-enterprise-backup-integrity-and-independent-restoration.png](../evidence/62-enterprise-backup-integrity-and-independent-restoration.png) | Backup integrity and independent restoration |
| 63 | [63-functional-disaster-recovery-and-operational-continuity.png](../evidence/63-functional-disaster-recovery-and-operational-continuity.png) | Functional recovery testing |
| 64 | [64-disaster-recovery-data-separation-and-cleanup.png](../evidence/64-disaster-recovery-data-separation-and-cleanup.png) | Recovery data separation and cleanup |

### Engineering Outcome

The enterprise backend backup included two SQLite databases and the persistent security audit log.

The restoration process verified the expected file inventory, file sizes, SHA-256 checksums and database integrity.

The independent recovery environment successfully restored:

| Data category | Recovered |
|---|---:|
| Financial transactions | 174 |
| Departmental projects | 5 |
| Historical audit events | 23 |
| Verified file checksums | 3/3 |

The restored application started successfully and generated additional audit events within its independent storage environment.

The operational audit history remained unchanged during recovery validation.

The exercise demonstrated application-level recovery within the local laboratory, rather than off-site disaster recovery.

## 12. Infrastructure Monitoring

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 66 | [66-infrastructure-monitoring-failure-and-recovery-validation.png](../evidence/66-infrastructure-monitoring-failure-and-recovery-validation.png) | Controlled failure detection and recovery |

### Engineering Outcome

A Python monitoring utility was implemented to inspect application health, HTTP response status, response latency, operational container state and filesystem capacity.

A controlled service interruption demonstrated degraded-state detection.

Following application recovery, the monitoring utility confirmed that the infrastructure had returned to a healthy operational state.

## 13. Centralized Infrastructure Orchestration

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 67 | [67-powershell-centralized-hyperv-infrastructure-status.png](../evidence/67-powershell-centralized-hyperv-infrastructure-status.png) | Centralized Hyper-V administration |
| 68 | [68-powershell-centralized-infrastructure-monitoring.png](../evidence/68-powershell-centralized-infrastructure-monitoring.png) | PowerShell infrastructure monitoring |
| 69 | [69-powershell-centralized-ansible-application-deployment.png](../evidence/69-powershell-centralized-ansible-application-deployment.png) | Centralized application deployment |

### Engineering Outcome

A Windows PowerShell management utility was developed to provide centralized administration across the virtualized infrastructure.

The implemented functions include:

- Hyper-V virtual machine status inspection.
- Ansible deployment syntax validation.
- Centralized infrastructure monitoring.
- Automated deployment reconciliation.

All four administrative functions were successfully validated.

The final centralized application deployment completed with 40 successful Ansible tasks, zero configuration changes and zero failed tasks.

## 14. Final Engineering Validation

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 70 | [70-final-automated-engineering-test-suite.png](../evidence/70-final-automated-engineering-test-suite.png) | Automated Python unit test results |
| 71 | [71-final-live-infrastructure-and-security-validation.png](../evidence/71-final-live-infrastructure-and-security-validation.png) | Final live application and security inspection |
| 72 | [72-final-hyper-v-private-network-segmentation.png](../evidence/72-final-hyper-v-private-network-segmentation.png) | Final English-language Hyper-V network configuration |

### Final Verified Results

| Validation | Result |
|---|---|
| Python unit tests | 18/18 passed |
| Operational applications | 2/2 healthy |
| SELinux | Enforcing |
| Linux host firewall | Active |
| IPv4 forwarding | Disabled |
| Default IPv4 and IPv6 routes | Absent |
| Container runtime | Rootless |
| Available application server storage | 31.44 GiB |
| Filesystem utilization | 9% |
| Overall infrastructure health | Healthy |

The final validation was completed on 22 November 2026.

The results confirm the tested configuration and operational state at the time of inspection.

## 15. Supplementary Engineering Evidence

The original engineering archive also contains supporting configuration screenshots, architectural illustrations and implementation notes.

These materials record early infrastructure provisioning, connectivity troubleshooting, SSH administration and network configuration activities.

The standardized screenshot numbering retains the historical implementation references where applicable.

Gaps in the sequence reflect the original evidence collection and consolidation process.

## 16. Representative Engineering Evidence

The following selected screenshots provide a quick visual overview. The linked tables in Sections 3–14 provide direct access to all 50 published images.

### Network policy enforcement

OPNsense firewall logs illustrating permitted application traffic and blocked requests to an unauthorized port.

![Network policy enforcement](../evidence/37-firewall-segmentation-enforcement.png)

[Open full-size evidence](../evidence/37-firewall-segmentation-enforcement.png)

### Container security validation

Automated verification of 16 runtime and network-security checks.

![Container security validation](../evidence/39-network-enabled-container-security-validation.png)

[Open full-size evidence](../evidence/39-network-enabled-container-security-validation.png)

### API authorization testing

Eighteen passing authentication and authorization test cases, including expected access denials.

![API authorization testing](../evidence/53-enterprise-api-authentication-and-authorization-tests.png)

[Open full-size evidence](../evidence/53-enterprise-api-authentication-and-authorization-tests.png)

### Independent database restoration

Validated backup checksums, database integrity and restored records in a separate recovery environment.

![Independent database restoration](../evidence/62-enterprise-backup-integrity-and-independent-restoration.png)

[Open full-size evidence](../evidence/62-enterprise-backup-integrity-and-independent-restoration.png)

### Infrastructure monitoring and orchestration

PowerShell-initiated monitoring of the health service, enterprise API and host capacity.

![Infrastructure monitoring and orchestration](../evidence/68-powershell-centralized-infrastructure-monitoring.png)

[Open full-size evidence](../evidence/68-powershell-centralized-infrastructure-monitoring.png)

### Final infrastructure validation

Point-in-time security and service verification for the application host.

![Final infrastructure validation](../evidence/71-final-live-infrastructure-and-security-validation.png)

[Open full-size evidence](../evidence/71-final-live-infrastructure-and-security-validation.png)

## 17. Evidence Storage and Security

The complete 67-screenshot working archive is retained locally. A curated subset of 50 screenshots is published in the Git repository.

The repository contains the implementation source code, automation scripts, technical documentation, the 50 selected screenshots and this evidence index.

The published screenshots include point-in-time infrastructure configuration, private laboratory addressing and operational command output.

Publishing only the curated subset limits unnecessary disclosure of implementation-stage screenshots while retaining the complete original record locally.

All enterprise application data used in the laboratory is fictional.

## 18. Evidence Interpretation and Limitations

Screenshots provide supporting technical evidence of configuration, execution and validation at specific points during the project.

They do not independently establish continuous infrastructure availability, comprehensive security assurance or production-level compliance.

Evidence is interpreted together with the source code, Ansible playbooks, automated tests, operational results and architectural documentation.

The backup and restoration evidence demonstrates application-level recovery within a single physical laboratory environment.

The completed project is an engineering demonstrator rather than a production-certified private cloud platform.

## 19. Related Documentation

- [Infrastructure Architecture](architecture.md)
- [Security Controls](security-controls.md)
- [Operations Runbook](operations-runbook.md)
- [Backup and Disaster Recovery](backup-and-recovery.md)
- [Engineering Validation Results](validation-results.md)

## 20. Published Screenshot Inventory

**Published:** 50 selected PNG screenshots in [`evidence/`](../evidence/), covering the project stages documented in Sections 3–14. Each entry in those tables links directly to the corresponding image in the repository.

**Retained locally:** 67 original screenshots in the separate engineering evidence archive. The published filenames preserve their original numerical identifiers, so gaps in the sequence indicate intentionally unpublished or historically omitted references, not broken links.

Only the curated set is represented as publicly available evidence.
