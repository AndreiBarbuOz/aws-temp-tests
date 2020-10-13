    [CmdletBinding()]

    param(

        [Parameter()]
        [string] $orchestratorVersion = "19.10.16"
    )


    function Main
    {
        Write-Host "Installing Orchestrator Version" + $orchestratorVersion

        New-Item "c:\cfn-tmp" -ItemType Directory -Force

        $item = "c:\cfn-tmp\" + (Get-Date).ToString("MM-dd-yy-hh-mm")
        New-Item $item -ItemType File
    }

    Main
