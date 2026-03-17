# SmartPGP applet

SmartPGP is a free and open source implementation of the [OpenPGP card
3.4 specification](https://gnupg.org/ftp/specs/OpenPGP-smart-card-application-3.4.pdf) in JavaCard.

The main improvement introduced in OpenPGP card 3.x specification from
previous version is the support of elliptic curve cryptography with
several existing curves (NIST P-256, NIST P-384, NIST P-521, brainpool
p256r1, brainpool p384r1 and brainpool p512r1).


## Features

The following features are implemented at the applet level, but some
of them depend on underlying hardware support and available
(non-)volatile memory resources:

- RSA (>= 2048 bits modulus, 17 bits exponent) and ECC (NIST P-256,
  NIST P-384, NIST P-521, brainpool p256r1, brainpool p384r1 and
  brainpool p512r1) for signature, encryption and authentication;

- On-board key generation and external private key import;

- PIN codes (user, admin and resetting code) up to 127 characters;

- Certificate up to 1 kB (DER encoded) for each key;

- Login, URL, and private DOs up to 256 bytes;

- Command and response chaining;

- AES 128/256 bits deciphering primitive;

- Secure messaging (see below).


## Default values

The SmartPGP applet is configured with the following default values:

- Admin PIN is 12345678;

- User PIN is 123456;

- No PUK (a.k.a. resetting code) is defined;

- RSA 2048 bits for PGP keys;

- NIST P-256 for the secure messaging key.

These values can be changed by modifying default values in the code
(see the [Constants](src/fr/anssi/smartpgp/Constants.java)
class).

When the applet is installed, one can use the `smartpgp-cli` utility
given in the `bin` directory to change these values. Keep in mind that
when you change the algorithm attributes of a PGP key or of the secure
messaging key, the key and the corresponding certificate are
erased. Also note that hard coded default values will be restored upon
a factory reset.


## Compliance with OpenPGP card 3.4 specification

The SmartPGP applet implements the complete OpenPGP card 3.4
specification, except the secure messaging related features:

- Commands and responses protection is not implemented as described in
  the specification. Motivation and implementation details are
  explained in the
  [secure messaging document](secure_messaging/smartpgp_sm.pdf);

- A command protected by secure messaging is not granted admin
  rights. Secure messaging can thus be used to protect communications
  only, especially when the token is used contactless;

- If and only if secure messaging static key and certificate have been
  provisioned, all commands containing sensitive data (e.g. PIN code,
  decrypted data, private key, ...) emitted through a contactless
  interface must be protected by secure messaging or they will be
  refused;

- The `ACTIVATE FILE` with P1 = P2 = 0, as described in the
  specification, resets everything except the secure messaging static
  key and certificate. Complete reset, including these elements, can
  be performed with `ACTIVATE FILE` with P1 = 0 and P2 = 1.



# Application support

Tokens following the OpenPGP card 3.4 specification are not yet fully
supported by most PGP applications.

## GnuPG

OpenPGP card 3.x is supported by [GnuPG](https://www.gnupg.org/)
starting from version 2.1.16.

The specific secure messaging of the SmartPGP applet is **not**
supported at is not part of the OpenPGP card specification.

## OpenKeychain

OpenPGP card 3.x is supported by [OpenKeychain](https://www.openkeychain.org/)
starting from version 4.2.

The secure messaging of the SmartPGP applet is fully supported in
OpenKeychain. See the section below for more information on the setup process.


# Content of the repository

The repository contains several directories:

- `bin` contains a Python library and command line tool called
  `smartpgp-cli` to interact with an OpenPGP card 3.x but also to deal
  with the specific secure messaging feature of the SmartPGP applet;

  - `bin/windows_context_menu` contains the AEPGP Windows context menu integration
    for easy file encryption/decryption via Windows Explorer (see [Windows Integration](#windows-integration) below);

- `secure_messaging` contains documentation and example scripts to
  play with the secure messaging feature of SmartPGP;

- `src` contains the JavaCard source code of the SmartPGP applet;

- `videos` contains sample videos demonstrating smartcard interactions
  with OpenKeychain and K9 mail on Android Nexus 5.


# Windows Integration

The `bin/windows_context_menu` directory provides a complete Windows Explorer integration for AEPGP SmartPGP cards, enabling easy file encryption and decryption via right-click context menus.

## Features

### File Operations
- **Encrypt File**: Encrypt any file using RSA-2048 encryption with the card's public key
- **Decrypt File**: Decrypt `.enc` files using the card's private key (PIN required)
- Files are encrypted with AES-256-GCM for data and RSA-2048 for key wrapping

### Card Management
- **Generate Keys**: Generate RSA-2048 key pairs directly on the card
  - Prompts for a key alias that is stored on the card (Private DO 0x0102)
  - Alias persists across sessions and can be read without PIN
  - Confirms before overwriting existing keys
- **Delete Keys**: Remove key pairs from the card (requires admin PIN)
- **Change PIN**: Change user PIN or admin PIN

### Automatic File Visibility Management
- **Background Watcher**: Automatically hides/shows `.enc` files based on card presence
  - Hidden when no AEPGP card is detected
  - Visible when an AEPGP card is inserted
  - Runs at user logon via Windows startup registry
  - Monitors Desktop, Documents, and Downloads folders by default
  - Configurable via environment variables:
    - `AEPGP_WATCH_PATHS`: Semicolon-separated list of paths to monitor (e.g., `C:\Files;D:\Data`)
    - `AEPGP_POLL_INTERVAL_SEC`: Card detection interval in seconds (default: 5)
    - `AEPGP_RESCAN_INTERVAL_SEC`: Full file rescan interval in seconds (default: 60)

## Installation

### Quick Install (Recommended)

1. Run the MSI installer (requires Administrator privileges):
   ```powershell
   msiexec /i bin\windows_context_menu\dist\AEPGPContextMenu-1.3.1.msi
   ```

   The installer will:
   - Install all context menu handlers
   - Register the background visibility watcher to start at user logon
   - Set up automatic updates for future versions

### Manual Installation

1. Install Python 3.8+ and required dependencies:
   ```powershell
   pip install pyscard pyasn1 cryptography
   ```

2. Run the installation script with Administrator privileges:
   ```powershell
   python bin\windows_context_menu\install_menu.py
   ```

3. The installer will:
   - Register all context menu handlers in Windows Registry
   - Install the visibility watcher to run at user logon
   - Verify all required files are present

## Usage

### Encrypting Files

1. Right-click any file in Windows Explorer
2. Select **AEPGP: Encrypt File**
3. Insert your AEPGP card when prompted
4. Choose a recipient (or use card owner for self-encryption)
5. The encrypted file will be created with `.enc` extension

### Decrypting Files

1. Right-click any `.enc` file in Windows Explorer
2. Select **AEPGP: Decrypt File**
3. Insert your AEPGP card and enter your PIN when prompted
4. The decrypted file will be saved in the same directory

### Generating Keys

1. Right-click anywhere in Windows Explorer
2. Select **AEPGP: Generate Keys**
3. Insert your AEPGP card
4. Enter a key alias when prompted (stored on the card)
5. Confirm with admin PIN (default: `12345678`)
6. Wait 30-60 seconds for key generation to complete

The key alias is stored in Private DO 0x0102 on the card and can be read without PIN authentication. This allows the system to identify the key pair owner even when the card is not authenticated.

### Card-Stored Alias

The key pair alias is stored directly on the AEPGP card using Private Data Object (DO) 0x0102:
- **Reading**: No PIN required - the alias can be read anytime the card is present
- **Writing**: Requires admin PIN - only set during key generation
- **Persistence**: Survives card removal and reinsertion
- **Format**: ASCII string, maximum 255 bytes
- **Purpose**: Identifies the card owner for encryption operations

This is supported by the SmartPGP applet's private DO implementation (see `SmartPGPApplet.java` lines 1019-1050 and `Constants.java` lines 103-106).

## Technical Details

### Encryption Format
- **Algorithm**: RSA-2048 with AES-256-GCM
- **Key Wrapping**: RSA-OAEP with SHA-256
- **File Format**: OpenPGP-compatible encrypted messages
- **Card Operations**: All private key operations performed on-card

### Card Detection
- Supports multiple ATR patterns for AEPGP/SmartPGP cards
- Compatible with Gemalto/NXP JCOP cards running SmartPGP applet
- Automatic reader selection and card connection management

### File Visibility Management
- Uses Windows hidden file attribute (not encryption-based hiding)
- Background process (`visibility_watcher.py`) monitors card presence every 5 seconds
- Rescans configured directories every 60 seconds for new `.enc` files
- Skips system directories (`.git`, `node_modules`, `__pycache__`, `AppData`)
- Minimal CPU and memory footprint

### Debug Logging
All operations are logged to `%APPDATA%\AEPGP\logs\aepgp_YYYYMMDD.log` for troubleshooting.

## Uninstallation

Run the uninstaller script with Administrator privileges:
```powershell
python bin\windows_context_menu\uninstall_menu.py
```

This will:
- Remove all context menu entries from Windows Registry
- Remove the visibility watcher from user startup
- Preserve encrypted files and debug logs

## Requirements

- Windows 10 or later
- Python 3.8 or later
- Smart card reader (USB CCID compliant)
- AEPGP SmartPGP card with RSA-2048 key pair
- Administrator privileges (for installation only)

## Documentation

Comprehensive documentation is available in `bin/windows_context_menu/README.md`.



# Build and installation instructions


## Prerequisites
- JavaCard Development Kit 3.0.4 (or above) from
  [Oracle website](http://www.oracle.com/technetwork/java/embedded/javacard/downloads/index.html);

- A device compliant with JavaCard 3.0.4 (or above) with enough
  available resources to hold the code (approximately 23 kB of
  non-volatile memory), persistent data (approximately 10 kB of
  non-volatile memory) and volatile data (approximately 2 kB of RAM).

- The [pyscard](https://pypi.org/project/pyscard/) and [pyasn1](https://pypi.org/project/pyasn1/)
  Python libraries for `smartcard-cli`.


## Importing RSA keys above 2048 bits (3072 or 4096 bits)

The size of the internal buffer is set by default to a value that
permits to import RSA 2048 bits. If your card is able to deal with RSA
keys of 3072 or 4096 bits and you want to be able to import such keys,
then you need to adjust the size of this buffer:

- for RSA 2048 bits, `Constants.INTERNAL_BUFFER_MAX_LENGTH` must be at
  least `(short)0x3b0`;

- for RSA 3072 bits, `Constants.INTERNAL_BUFFER_MAX_LENGTH` must be at
  least `(short)0x570`;

- for RSA 4096 bits, `Constants.INTERNAL_BUFFER_MAX_LENGTH` must be at
  least `(short)0x730`.


## Reducing flash and/or RAM consumption

The applet allocates all its data structures to their maximal size
at installation to avoid as much as possible runtime errors caused by
memory allocation failure. If your device does not have enough flash
and/or RAM available, or if you plan not to use some features
(e.g. stored certificates), you can adjust the applet to reduce its
resource consumption by tweaking the following variables:

- `Constants.INTERNAL_BUFFER_MAX_LENGTH`: the size in bytes of the
  internal RAM buffer used for input/output chaining. Chaining is
  especially used in case of long commands and responses such as those
  involved in private key import and certificate import/export;
  
- `Constants.EXTENDED_CAPABILITIES`, bytes 5 and 6: the maximal size
  in bytes of a certificate associated to a key. Following the OpenPGP
  card specification, a certificate can be stored for each of the
  three keys. In SmartPGP, a fourth certificate is stored for secure
  messaging.


## Building the CAP file

- Set path to the JavaCard Development Kit:
  `export JC_HOME="your/path/to/javacardkit"`

- (Optional) Edit the `build.xml` file and replace the `0xAF:0xAF`
  bytes in the `APPLET_AID` with your own manufacturer identifier (see
  section 4.2.1 of OpenPGP card specification). Alternatively, set the
  right AID instance bytes during applet installation.

- Execute `ant` with no parameter will produce the CAP file in
  `SmartPGPApplet.cap`.

## Installing the CAP file

The CAP file installation depends on your device, so you have to refer
to the instructions given by your device manufacturer. Most open cards
relying on Global Platform with default keys are supported by
[GlobalPlatformPro](https://github.com/martinpaljak/GlobalPlatformPro).

Be careful to use a valid AID according to the OpenPGP card
specification (see section 4.2.1) for each card (`-create <AID>` with
GlobalPlatformPro)



# Setting up secure messaging with OpenKeychain

## Secure messaging without token authentication

Without token authentication, you are not protected against
man-in-the-middle attack as your device cannot ensure it is
communicating directly with a trusted token. Nevertheless, the
communications with the token are still protected in confidentiality
against passive attacks (i.e. trafic capture).

If you want to test secure messaging without token authentication, you
can use the following command to order the token to generate its
secure messaging key on-board.

`./smartpgp-cli -r X -I generate-sm-key -o pubkey.raw`

In this case, you have to deactivate the certificate verification in
OpenKeychain: go to "Parameters" > "Experimental features" and
deactivate the option called "SmartPGP verify certificate".


## Secure messaging with token authentication

The `secure_messaging` directory contains a subdirectory called `pki`
which contains two sample scripts to generate a certificate
authority and token certificates.

The sample scripts are given **only** for test purposes of the secure
messaging feature with certificate verification. They require
`openssl` to be installed on your system.

If you want to use your own PKI, you have to generate a specific
intermediate certificate authority to sign the certificates of your
token(s). Then, you have to provision the complete certificate chain
from this new intermediate CA to your root CA in OpenKeychain because
the certificate verification implemented in the given patch does not
rely on the system keystore.

### Generate a sample CA key and certificate

Change your current directory to the `pki` directory and execute the
script `./generate_ca.sh`. It will produce a sample CA key in
`PKI/private/ca.key.pem` and the corresponding certificate in
`PKI/certs/ca.cert.pem`.

### Generate a sample token key and certificate

Change your current directory to the `pki` directory and execute the
script

`./generate_token.sh mycard1`

where `mycard1` is some unique identifier for the token. It will
produce a sample token key in `PKI/private/mycard1.key.pem` and the
corresponding certificate in `PKI/certs/mycard1.cert.pem`.

### Provision the token with its sample key and certificate

Change your current directory to the `bin` directory and execute the
following commands after replacing the reader number `X` by the number
of the reader that contains your token, and the path to the `pki`
directory used in previous sections.

The following command imports the token key in the token.

`./smartpgp-cli -r X -I -i path_to_the_pki_dir/PKI/private/mycard1.key.der put-sm-key`

The following command imports the token certificate in the token.

`./smartpgp-cli -r X -I -i path_to_the_pki_dir/PKI/certs/mycard1.cert.der put-sm-certificate`

These commands have to be executed in this order because the key
import clears any previously stored certificate.

Once the token key is imported, you should remove the token private
key from you system as there is no need to keep it outside of your
token.

### Install the CA in OpenKeychain

- Upload the CA certificate `PKI/certs/ca.cert.pem` to your phone;

- Go to "Parameters" > "Experimental features" and activate the option called "SmartPGP verify certificate`;

- Click on "SmartPGP trusted authorities", and then on "+" at the top left;

- Set a name for this authority and select the file you uploaded.

