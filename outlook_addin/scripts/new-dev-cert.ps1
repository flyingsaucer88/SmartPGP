Param(
    [string]$CertName = "SmartPGP-Addin-Localhost",
    [string]$CertPassword = "change-me",
    [string]$OutPath = "../certs/addin-localhost.pfx"
)

Write-Host "Creating dev cert for add-in host (https://localhost:3000)..."

$cert = New-SelfSignedCertificate `
    -DnsName "localhost" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -FriendlyName $CertName `
    -NotAfter (Get-Date).AddYears(2)

$pwd = ConvertTo-SecureString -String $CertPassword -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $OutPath -Password $pwd | Out-Null

Write-Host "Certificate created at $OutPath"
Write-Host "Install into 'Trusted Root Certification Authorities' if not already trusted."
