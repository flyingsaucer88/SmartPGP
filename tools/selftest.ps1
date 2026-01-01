Param(
    [string]$HelperUrl = "https://127.0.0.1:5555",
    [string]$Recipient = "ambisecure@outlook.com",
    [string]$AddinHost = "https://localhost:3000"
)

function Run-Step($name, $scriptBlock) {
    Write-Host "`n=== $name ===" -ForegroundColor Cyan
    try {
        & $scriptBlock
    } catch {
        Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Run-Step "Helper self-test" {
    $testPath = Resolve-Path "../outlook_helper/windows/SmartPGP.OutlookHelper/tests/selftest.ps1"
    & $testPath -HelperUrl $HelperUrl -Recipient $Recipient
}

Run-Step "Add-in host self-test" {
    $node = Get-Command node -ErrorAction SilentlyContinue
    if (-not $node) { throw "Node is required to test add-in host." }
    $testPath = Resolve-Path "../outlook_addin/tests/selftest.js"
    Push-Location "../outlook_addin"
    node $testPath --addiHost $AddinHost
    Pop-Location
}

Write-Host "`nAll self-tests passed." -ForegroundColor Green
