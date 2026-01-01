# Localhost certificate

Place a trusted localhost certificate here for HTTPS binding, e.g. `localhost.pfx`. Update `CertificatePath` and `CertificatePassword` in `appsettings.json` or environment variables.

For development you can use:
```bash
powershell -ExecutionPolicy Bypass -File ../scripts/new-dev-cert.ps1
```
