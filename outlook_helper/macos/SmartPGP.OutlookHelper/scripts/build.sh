#!/bin/bash
# Build script for SmartPGP Outlook Helper (macOS)

set -e

echo "Building SmartPGP Outlook Helper for macOS..."
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v swift &> /dev/null; then
    echo "Error: Swift not found. Please install Xcode Command Line Tools:"
    echo "  xcode-select --install"
    exit 1
fi

if ! command -v gpg &> /dev/null; then
    echo "Error: GPG not found. Please install GnuPG:"
    echo "  brew install gnupg"
    exit 1
fi

if [ ! -f "/opt/homebrew/lib/libgpgme.dylib" ] && [ ! -f "/usr/local/lib/libgpgme.dylib" ]; then
    echo "Error: GPGME library not found. Please install GPGME:"
    echo "  brew install gpgme"
    exit 1
fi

echo "✓ All prerequisites found"
echo ""

# Build
echo "Building release binary..."
swift build -c release

echo ""
echo "✓ Build successful!"
echo ""
echo "Binary location: .build/release/SmartPGP.OutlookHelper"
echo ""
echo "To run:"
echo "  ./.build/release/SmartPGP.OutlookHelper"
echo ""
echo "To run tests:"
echo "  cd tests && ./selftest.sh"
