# TLS Certificates

This directory is for storing TLS certificates for HTTPS operation.

## Development Certificate

For development, you can create a self-signed certificate:

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout localhost.key -out localhost.crt -days 365 -nodes \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

# Convert to P12 format (if needed)
openssl pkcs12 -export -out localhost.p12 -inkey localhost.key -in localhost.crt \
  -passout pass:change-me
```

## Trust the Certificate

### macOS

```bash
# Add to keychain
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain localhost.crt
```

## Configuration

Set the certificate path in `.env`:

```bash
SMARTPGP_CERT_PATH=certs/localhost.p12
SMARTPGP_CERT_PASSWORD=change-me
```

## Security Note

**Never commit certificate files to version control!**

The `.gitignore` is configured to exclude:
- `*.p12`
- `*.pem`
- `*.key`
- `*.crt`
