[CmdletBinding()]

param(

    [Parameter(Mandatory=$false)]
    [AllowEmptyString()]
    [string] $inputVal
)

[System.String]$script:tmp = $inputVal

function Main {
    if ((Test-Path C:\uipath\projects) -and (Test-Path C:\uipath\projects\aws-temp-tests)) {
        Write-Host "Installing Orchestrator Version" + $tmp
    }
}

Main
