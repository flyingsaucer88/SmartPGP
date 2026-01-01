Param(
    [string]$CertName = "SmartPGP-Localhost",
    [string]$CertPassword = "change-me",
    [string]$OutPath = "../certs/localhost.pfx"
)

Write-Host "Creating development HTTPS certificate for localhost..."

# Create self-signed cert
$cert = New-SelfSignedCertificate `
    -DnsName "localhost" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -FriendlyName $CertName `
    -NotAfter (Get-Date).AddYears(2)

# Export PFX
$pwd = ConvertTo-SecureString -String $CertPassword -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $OutPath -Password $pwd | Out-Null

Write-Host "Certificate created at $OutPath"
Write-Host "Install into 'Trusted Root Certification Authorities' if not already trusted."
