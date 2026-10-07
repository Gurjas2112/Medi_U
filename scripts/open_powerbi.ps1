$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Pbix = Join-Path $Root "dashboards\powerbi\Hospital_Operational_Dashboard.pbix"
$Python = Join-Path $Root "src\powerbi\launch_desktop.py"

if (-not (Test-Path $Pbix)) {
    Write-Error "Dashboard file not found: $Pbix"
}

Write-Host "Opening Power BI dashboard: $Pbix"
python -m src.powerbi.launch_desktop
if ($LASTEXITCODE -ne 0) {
    $StartMenu = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Power BI Desktop"
    $ExeCandidates = @(
        "C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
        "C:\Program Files (x86)\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
    )
    $Exe = $ExeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($Exe) {
        Start-Process -FilePath $Exe -ArgumentList "`"$Pbix`""
    } elseif (Test-Path $StartMenu) {
        $Shortcut = Get-ChildItem -Path $StartMenu -Filter "*.lnk" -Recurse | Select-Object -First 1
        if ($Shortcut) {
            Start-Process -FilePath $Shortcut.FullName
        } else {
            Invoke-Item $Pbix
        }
    } else {
        Invoke-Item $Pbix
    }
}
