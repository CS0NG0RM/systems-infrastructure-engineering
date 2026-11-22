param(
    [ValidateSet("Status", "Monitor", "Validate", "Deploy")]
    [string]$Action = "Status"
)

$ErrorActionPreference = "Stop"

# Define the private Ubuntu management endpoint.
$ManagementHost = "labadmin@10.20.40.10"
$RemoteDirectory = "/home/labadmin/infrastructure-automation"

# Reference the protected SSH agent socket on Ubuntu.
$RemoteAgentSocket = "/home/labadmin/.ssh/lab-agent.sock"

# Restrict SSH communication to the established management server.
$SshOptions = @(
    "-o", "StrictHostKeyChecking=yes",
    "-o", "ConnectTimeout=5",
    "-o", "ForwardAgent=no",
    "-o", "ClearAllForwardings=yes"
)

function Invoke-ManagementCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,

        [switch]$RequireAgent
    )

    # Validate the existing authentication agent when required.
    if ($RequireAgent) {

        $Command = "export SSH_AUTH_SOCK=$RemoteAgentSocket && " +
            "test -S $RemoteAgentSocket && " +
            "ssh-add -l >/dev/null 2>&1 && " +
            $Command
    }

    # Execute the predefined command on the management server.
    & ssh @SshOptions $ManagementHost $Command

    $Result = $LASTEXITCODE

    if ($Result -ne 0) {
        throw "Remote operation failed with exit code $Result."
    }
}

function Get-InfrastructureStatus {

    Write-Host "`nHYPER-V INFRASTRUCTURE STATUS"

    # Inspect local virtual machines without changing their state.
    Get-VM |
        Select-Object Name, State, CPUUsage,
            @{Name = "MemoryMiB"; Expression = {
                [math]::Round($_.MemoryAssigned / 1MB, 2)
            }},
            Uptime |
        Format-Table -AutoSize

    Write-Host "`nVirtual machine status inspection completed."
}

function Invoke-InfrastructureMonitoring {

    Write-Host "`nCENTRALIZED INFRASTRUCTURE MONITORING"

    # Reuse the protected Ubuntu authentication agent.
    Invoke-ManagementCommand `
        -Command "cd $RemoteDirectory && python3 scripts/monitor_infrastructure.py" `
        -RequireAgent

    Write-Host "`nInfrastructure monitoring passed."
}

function Invoke-InfrastructureValidation {

    Write-Host "`nANSIBLE DEPLOYMENT SYNTAX VALIDATION"

    # Validate deployment playbooks without modifying containers.
    $Command = "cd $RemoteDirectory && " +
        ".venv/bin/ansible-playbook playbooks/deploy_application.yml --syntax-check && " +
        ".venv/bin/ansible-playbook playbooks/deploy_enterprise_api.yml --syntax-check"

    Invoke-ManagementCommand -Command $Command

    Write-Host "`nDeployment syntax validation passed."
}

function Invoke-ApplicationDeployment {

    Write-Host "`nAUTOMATED APPLICATION DEPLOYMENT"

    # Reconcile both applications through the existing Ansible automation.
    $Command = "cd $RemoteDirectory && " +
        ".venv/bin/ansible-playbook playbooks/deploy_application.yml && " +
        ".venv/bin/ansible-playbook playbooks/deploy_enterprise_api.yml"

    Invoke-ManagementCommand `
        -Command $Command `
        -RequireAgent

    Write-Host "`nApplication deployment completed."
}

try {

    Write-Host "Secure Enterprise Infrastructure Management"
    Write-Host "Selected action: $Action"
    Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

    # Execute only the explicitly selected administrative action.
    switch ($Action) {

        "Status" {
            Get-InfrastructureStatus
        }

        "Monitor" {
            Invoke-InfrastructureMonitoring
        }

        "Validate" {
            Invoke-InfrastructureValidation
        }

        "Deploy" {
            Invoke-ApplicationDeployment
        }
    }

    Write-Host "`nINFRASTRUCTURE OPERATION COMPLETED SUCCESSFULLY" `
        -ForegroundColor Green

    exit 0

}
catch {

    Write-Host "`nINFRASTRUCTURE OPERATION FAILED" `
        -ForegroundColor Red

    Write-Host $_.Exception.Message

    exit 1
}