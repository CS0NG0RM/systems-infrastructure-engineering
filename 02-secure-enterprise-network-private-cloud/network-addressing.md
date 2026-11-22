
# Laboratory Network Addressing Plan

Status: Proposed, not yet deployed or validated.

## Internal Networks

| VirtualBox Network | Subnet | Planned Gateway | Purpose |
|---|---|---|---|
| lab-wan | 172.30.100.0/24 | None | Simulated external network |
| lab-mgmt | 10.20.10.0/24 | 10.20.10.1 | Infrastructure management |
| lab-app | 10.20.20.0/24 | 10.20.20.1 | Application services |
| lab-compute | 10.20.30.0/24 | 10.20.30.1 | Container and compute infrastructure |

## Planned Devices

| Device | Network | Planned IP |
|---|---|---|
| LAB-FW-01 | lab-mgmt | 10.20.10.1 |
| LAB-FW-01 | lab-app | 10.20.20.1 |
| LAB-FW-01 | lab-compute | 10.20.30.1 |
| LAB-MGMT-01 | lab-mgmt | 10.20.10.10 |

## Security Boundaries

- All four networks use VirtualBox Internal Network mode.
- No physical, bridged or NAT adapters are currently planned.
- No direct internet access is provided.
- Inter-network communication will require explicit firewall configuration.
- Default inter-network access policy: deny unless explicitly allowed.
- Network isolation and firewall enforcement remain untested.
- No real credentials, customer data or employer infrastructure will be used.

## Deployment Status

- Virtual machines created: LAB-MGMT-01, LAB-FW-01
- Operating systems installed: No
- Firewall policies deployed: No
- Connectivity tests completed: No
