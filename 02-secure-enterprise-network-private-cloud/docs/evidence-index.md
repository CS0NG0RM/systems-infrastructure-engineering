# Engineering Evidence Index

## 1. Overview

This document indexes the supporting evidence collected during the
implementation and validation of the secure enterprise network and
private cloud infrastructure.

The evidence collection documents infrastructure configuration,
security enforcement, application deployment, engineering remediation,
controlled failure testing, disaster recovery and operational validation.

The original evidence inventory contains 69 files, including screenshots,
architectural illustrations and supplementary engineering documentation.

The evidence filenames listed below correspond to the existing
evidence inventory as of 22 November 2026.

Screenshot descriptions identify their intended engineering coverage.
Individual images require a separate content and publication review.

## 2. Evidence Management Principles

The evidence collection follows these principles:

- Preserve original engineering evidence.
- Maintain chronological traceability.
- Distinguish implementation evidence from architectural illustrations.
- Retain evidence of controlled failures and subsequent remediation.
- Avoid recreating historical engineering events solely for presentation.
- Review screenshots before public distribution.
- Exclude credentials, private keys and sensitive operational information.
- Keep original evidence separate from selected portfolio screenshots.

The complete original evidence collection is maintained separately
from the source code repository.

Not every collected screenshot is intended for public publication.

## 3. Virtual Infrastructure and Network Configuration

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| Initial | 01-hyper-v-private-switch-configuration.png | Hyper-V private virtual switch configuration |
| 02 | 02-opnsense-network-configuration.png | Firewall interface and network configuration |
| 03 | 03-opnsense-routing-isolation.png | Routing isolation |
| 04 | 04-opnsense-operational-dashboard.png | Operational firewall infrastructure |
| 10 | 10-firewall-policy-enforcement.png | Network firewall policy enforcement |
| 11 | 11-firewall-resource-optimization.png | Firewall resource configuration |
| 15 | 15-key-based-automation-validation.png | Key-based administrative automation |
| Supplementary | project-02-ssh-management.png | SSH management architecture |

## 4. Offline Container Engineering

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 22 | 22-automated-offline-container-image-build.png | Offline container base image engineering |
| 23 | 23-automated-application-container-build.png | Automated application image construction |
| 24 | 24-containerized-application-runtime-validation.png | Containerized application execution |
| 25 | 25-container-runtime-security-verification.png | Container runtime security controls |
| 26 | 26-automated-container-security-validation.png | Automated container security inspection |
| 27 | 27-idempotent-container-deployment.png | Deployment idempotency |

## 5. Application Lifecycle and Release Engineering

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 28 | 28-automated-application-recovery.png | Automated application recovery |
| 29 | 29-graceful-shutdown-remediation.png | Application shutdown remediation |
| 30 | 30-controlled-application-release-upgrade.png | Controlled application version upgrade |
| 31 | 31-automated-rollback-trigger.png | Deliberate rollback trigger |
| 32 | 32-automated-rollback-failure-recovery.png | Recovery following a controlled deployment failure |

## 6. Network Segmentation and Application Exposure

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 33 | 33-restricted-application-network-deployment.png | Restricted application network deployment |
| 34 | 34-source-restricted-application-firewall.png | Source-specific host firewall configuration |
| 35 | 35-opnsense-application-access-policy.png | Network firewall application access policy |
| 36 | 36-authorized-cross-segment-application-connectivity.png | Authorized cross-segment communication |
| 37 | 37-firewall-segmentation-enforcement.png | Firewall segmentation enforcement |
| 38 | 38-unauthorized-source-access-denied.png | Unauthorized source access testing |
| 39 | 39-network-enabled-container-security-validation.png | Network-enabled container validation |

Evidence of unsuccessful connection attempts is distinguished from
independently confirmed firewall log attribution.

## 7. Permanent Application Migration and Recovery

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 40 | 40-permanent-private-application-migration.png | Permanent application migration |
| 41 | 41-permanent-application-deployment-idempotency.png | Idempotent private deployment |
| 42 | 42-application-recovery-after-infrastructure-restart.png | Application recovery following infrastructure restart |
| 43 | 43-private-network-automated-release-rollback.png | Private network release rollback |
| 44 | 44-private-network-rollback-independent-verification.png | Independent rollback verification |

## 8. Enterprise Backend Integration

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 45 | 45-offline-backend-image-export.png | Offline backend image export |
| 46 | 46-offline-docker-to-podman-image-migration.png | Docker-to-Podman backend migration |
| 48 | 48-enterprise-persistent-database-initialization.png | Persistent database initialization |
| 49 | 49-persistent-database-integrity-and-permissions.png | Database integrity and filesystem permissions |
| 50 | 50-enterprise-financial-and-project-data-ingestion.png | Fictional enterprise data ingestion |
| 51 | 51-isolated-enterprise-api-deployment.png | Network-isolated enterprise backend deployment |
| 52 | 52-enterprise-api-health-and-network-isolation.png | Backend health and network isolation |

The original evidence filenames are retained, including historical
spelling and filename extension differences.

## 9. Enterprise Application Security

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 53 | 53-enterprise-api-authentication-and-authorization-tests.png | Authentication and authorization testing |
| 54 | 54-persistent-enterprise-security-audit-validation.png | Persistent security audit validation |
| 55 | 55-private-enterprise-api-deployment.png | Dedicated private backend deployment |
| 56 | 56-private-api-isolation-persistence-and-loopback-validation.png | Runtime isolation, persistent data and restricted network exposure |
| 57 | 57-enterprise-api-encrypted-management-access.png | Encrypted SSH management access |
| 58 | 58-encrypted-api-authorization-and-direct-access-restriction.png | Authorization through SSH and direct access restriction |

## 10. Enterprise Deployment Automation

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 59 | 59-automated-enterprise-api-deployment-validation.png | Automated enterprise backend deployment |
| 60 | 60-enterprise-api-deployment-idempotency.png | Deployment idempotency and application preservation |

## 11. Backup and Disaster Recovery

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 61 | 61-enterprise-database-backup-and-service-recovery.png | Application backup and service recovery |
| 62 | 62-enterprise-backup-integrity-and-independent-restoration.png | Backup integrity and independent restoration |
| 63 | 63-functional-disaster-recovery-and-operational-continuity.png | Functional recovery exercise |
| 64 | 64-disaster-recovery-data-separation-and-cleanup.png | Recovery data separation and controlled cleanup |

These evidence references support the documented application-level
backup and recovery exercise.

They do not establish off-site disaster recovery or physical
infrastructure redundancy.

## 12. Infrastructure Monitoring

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 65 | 65-centralized-infrastructure-monitoring-healthy-state.png | Healthy infrastructure monitoring |
| 66 | 66-infrastructure-monitoring-failure-and-recovery-validation.png | Controlled failure detection and recovery recognition |

## 13. Centralized Infrastructure Orchestration

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 67 | 67-powershell-centralized-hyperv-infrastructure-status.png | Centralized virtual machine administration |
| 68 | 68-powershell-centralized-infrastructure-monitoring.png | Windows-based operational monitoring |
| 69 | 69-powershell-centralized-ansible-application-deployment.png | Centralized automated application deployment |

## 14. Final Engineering Validation

| Reference | Evidence filename | Engineering coverage |
|---|---|---|
| 70 | 70-final-automated-engineering-test-suite.png | Final execution of all 18 automated Python tests |
| 71 | 71-final-live-infrastructure-and-security-validation.png | Final live infrastructure and security inspection |

The final validation established healthy operational applications,
a compliant Rocky Linux security baseline and successful automated
test execution.

## 15. Supplementary Evidence

The original evidence inventory also contains supplementary
configuration screenshots, architectural illustrations and
historical project notes.

Generic filenames are not assigned specific engineering conclusions
without inspecting their contents.

Architectural illustrations are treated as explanatory material,
rather than independent proof of operational infrastructure.

The original evidence numbering contains gaps because screenshot
identifiers were assigned during incremental project implementation.

Missing numbered filenames are not represented as available evidence.

## 16. Candidate Portfolio Evidence

The following screenshots are candidates for a concise,
public-facing engineering portfolio.

Selection remains subject to individual security and presentation
review.

| Reference | Engineering capability |
|---|---|
| 22 | Offline image engineering |
| 35 | Network firewall access policy |
| 37 | Network segmentation enforcement |
| 39 | Hardened container networking |
| 44 | Automated release rollback |
| 46 | Cross-runtime container migration |
| 50 | Enterprise data integration |
| 53 | Authentication and authorization |
| 56 | Backend isolation and persistent storage |
| 58 | Encrypted application access |
| 60 | Idempotent application deployment |
| 62 | Backup integrity and independent restoration |
| 64 | Recovery environment data separation |
| 66 | Monitoring failure detection and recovery |
| 69 | Centralized infrastructure orchestration |
| 70 | Automated engineering tests |
| 71 | Final operational and security validation |

Additional English-language infrastructure screenshots may be
captured to improve presentation consistency.

Historical evidence should remain unchanged.

## 17. Evidence Publication Security

Before any screenshot is published, inspect it for:

- Passwords and private key material.
- Authentication tokens and demonstration credentials.
- Personal account information.
- Personal filesystem paths.
- Unrelated desktop applications or notifications.
- Sensitive configuration values.
- Database contents.
- Raw security audit records.
- SSH authentication socket information.
- Unnecessary device identifiers.
- Employer or third-party information.

Private laboratory network addresses may be retained where required
to explain the documented architecture.

Screenshots containing sensitive information should either remain
private or be appropriately redacted in separate publication copies.

Original evidence must not be modified during redaction.

## 18. Evidence Limitations

Screenshots provide supporting point-in-time observations.

They do not independently establish continuous service availability,
comprehensive security assurance or production-level compliance.

The evidence index should be interpreted together with the source
code, automation playbooks, test results and architecture documentation.

No external publication is performed by creating this index.

## 19. Related Documentation

- [Infrastructure Architecture](architecture.md)
- [Security Controls](security-controls.md)
- [Operations Runbook](operations-runbook.md)
- [Backup and Disaster Recovery](backup-and-recovery.md)
- [Engineering Validation Results](validation-results.md)

## 20. Standardized Local Evidence Collection

The standardized evidence collection is maintained outside the Git repository.

Original historical evidence has been preserved separately.

The collection includes two additional English-language Hyper-V screenshots.

Total inventoried local screenshots: 67.

The inventory records filenames only. Individual publication approval
requires a separate content and security review.

| Evidence filename |
|---|
| 01-hyper-v-private-switch-configuration.png |
| 02-opnsense-network-configuration.png |
| 03-opnsense-routing-isolation.png |
| 04-opnsense-operational-dashboard.png |
| 05-ubuntu-management-server-installation.png |
| 06-windows-to-management-server-connectivity.png |
| 07-rocky-linux-initial-network-configuration.png |
| 08-rocky-linux-segment-routing-configuration.png |
| 09-rocky-linux-host-firewall-hardening.png |
| 10-firewall-policy-enforcement.png |
| 11-firewall-resource-optimization.png |
| 12-opnsense-packet-filter-rules.png |
| 13-opnsense-packet-filter-status.png |
| 14-rocky-linux-ssh-and-firewall-verification.png |
| 15-key-based-automation-validation.png |
| 16-cross-segment-ssh-and-management-network-validation.png |
| 22-automated-offline-container-image-build.png |
| 23-automated-application-container-build.png |
| 24-containerized-application-runtime-validation.png |
| 25-container-runtime-security-verification.png |
| 26-automated-container-security-validation.png |
| 27-idempotent-container-deployment.png |
| 28-automated-application-recovery.png |
| 29-graceful-shutdown-remediation.png |
| 30-controlled-application-release-upgrade.png |
| 31-automated-rollback-trigger.png |
| 32-automated-rollback-failure-recovery.png |
| 33-restricted-application-network-deployment.png |
| 34-source-restricted-application-firewall.png |
| 35-opnsense-application-access-policy.png |
| 36-authorized-cross-segment-application-connectivity.png |
| 37-firewall-segmentation-enforcement.png |
| 38-unauthorized-source-access-denied.png |
| 39-network-enabled-container-security-validation.png |
| 40-permanent-private-application-migration.png |
| 41-permanent-application-deployment-idempotency.png |
| 42-application-recovery-after-infrastructure-restart.png |
| 43-private-network-automated-release-rollback.png |
| 44-private-network-rollback-independent-verification.png |
| 45-offline-backend-image-export.png |
| 46-offline-docker-to-podman-image-migration.png |
| 48-enterprise-persistent-database-initialization.png |
| 49-persistent-database-integrity-and-permissions.png |
| 50-enterprise-financial-and-project-data-ingestion.png |
| 51-isolated-enterprise-api-deployment.png |
| 52-enterprise-api-health-and-network-isolation.png |
| 53-enterprise-api-authentication-and-authorization-tests.png |
| 54-persistent-enterprise-security-audit-validation.png |
| 55-private-enterprise-api-deployment.png |
| 56-private-api-isolation-persistence-and-loopback-validation.png |
| 57-enterprise-api-encrypted-management-access.png |
| 58-encrypted-api-authorization-and-direct-access-restriction.png |
| 59-automated-enterprise-api-deployment-validation.png |
| 60-enterprise-api-deployment-idempotency.png |
| 61-enterprise-database-backup-and-service-recovery.png |
| 62-enterprise-backup-integrity-and-independent-restoration.png |
| 63-functional-disaster-recovery-and-operational-continuity.png |
| 64-disaster-recovery-data-separation-and-cleanup.png |
| 65-centralized-infrastructure-monitoring-healthy-state.png |
| 66-infrastructure-monitoring-failure-and-recovery-validation.png |
| 67-powershell-centralized-hyperv-infrastructure-status.png |
| 68-powershell-centralized-infrastructure-monitoring.png |
| 69-powershell-centralized-ansible-application-deployment.png |
| 70-final-automated-engineering-test-suite.png |
| 71-final-live-infrastructure-and-security-validation.png |
| 72-final-hyper-v-private-network-segmentation.png |
| 73-final-hyper-v-virtual-infrastructure-overview.png |
