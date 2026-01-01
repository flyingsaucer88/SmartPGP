Param(
    [string]$HelperUrl = "https://127.0.0.1:5555",
    [string]$Recipient = "ambisecure@outlook.com",
    [string]$Message = "Hello from SmartPGP self-test"
)

function Fail($msg) {
    Write-Host "FAIL: $msg" -ForegroundColor Red
    exit 1
}

function Require-Command($cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Fail "Command not found: $cmd"
    }
}

Require-Command "gpg"
Require-Command "curl"

Write-Host "SmartPGP Helper Self-Test" -ForegroundColor Cyan

if (-not $Recipient) {
    Fail "Recipient email/key id is required. Pass -Recipient you@example.com"
}

Write-Host "1) Checking card status via gpg..."
$cardStatus = gpg --card-status 2>$null
if ($LASTEXITCODE -ne 0) { Fail "gpg --card-status failed. Ensure card is inserted and gpg-agent is running." }

Write-Host "2) Checking secret keys (card-backed) via gpg..."
gpg --list-secret-keys 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "gpg --list-secret-keys failed. Ensure keys are available." }

$tmpArmored = New-TemporaryFile

Write-Host "3) Encrypting via helper ($HelperUrl) for recipient $Recipient..."
$payload = @{ body = $Message; recipients = @($Recipient) } | ConvertTo-Json -Compress
$encResp = curl -k -s -X POST "$HelperUrl/encrypt" -H "Content-Type: application/json" -d $payload
if ($LASTEXITCODE -ne 0) { Fail "Helper encrypt request failed." }

try {
    $encJson = $encResp | ConvertFrom-Json
    if (-not $encJson.armored) { Fail "No armored field in helper response." }
    Set-Content -Path $tmpArmored -Value $encJson.armored -Encoding UTF8
} catch {
    Fail "Failed to parse encrypt response: $_"
}

Write-Host "4) Decrypting via helper..."
$decPayload = @{ body = $encJson.armored } | ConvertTo-Json -Compress
$decResp = curl -k -s -X POST "$HelperUrl/decrypt" -H "Content-Type: application/json" -d $decPayload
if ($LASTEXITCODE -ne 0) { Fail "Helper decrypt request failed." }

try {
    $decJson = $decResp | ConvertFrom-Json
    if ($decJson.plaintext -ne $Message) { Fail "Helper decrypt mismatch. Expected '$Message' got '$($decJson.plaintext)'." }
} catch {
    Fail "Failed to parse decrypt response: $_"
}

Write-Host "5) Cross-check decrypt with gpg CLI..."
$gpgOut = gpg --decrypt $tmpArmored 2>$null
if ($LASTEXITCODE -ne 0) { Fail "gpg --decrypt failed on helper output." }
if ($gpgOut.Trim() -ne $Message) { Fail "gpg decrypt mismatch. Expected '$Message' got '$gpgOut'." }

Remove-Item $tmpArmored -ErrorAction SilentlyContinue

Write-Host "PASS: Helper encrypt/decrypt and gpg interop succeeded." -ForegroundColor Green
