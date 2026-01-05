#!/bin/bash
# SmartPGP macOS Helper Self-Test
# Tests all endpoints of the helper service

set -e

# Configuration
HELPER_URL="${HELPER_URL:-https://127.0.0.1:5555}"
RECIPIENT="${RECIPIENT:-ambisecure@outlook.com}"
TEST_MESSAGE="Hello from SmartPGP macOS self-test"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}SmartPGP macOS Helper Self-Test${NC}"
echo "Helper URL: $HELPER_URL"
echo "Test recipient: $RECIPIENT"
echo ""

# Function to print test results
pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    exit 1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v gpg &> /dev/null; then
    fail "GPG not found. Please install GPG (brew install gnupg)"
fi

if ! command -v curl &> /dev/null; then
    fail "curl not found"
fi

pass "Prerequisites check"

# Test 1: Health check
echo ""
echo "Test 1: Health check..."
HEALTH_RESPONSE=$(curl -k -s "$HELPER_URL/healthz")
if [ "$HEALTH_RESPONSE" = "ok" ]; then
    pass "Health check"
else
    fail "Health check returned: $HEALTH_RESPONSE"
fi

# Test 2: Card status
echo ""
echo "Test 2: Card status..."
CARD_STATUS=$(curl -k -s "$HELPER_URL/card-status")
if echo "$CARD_STATUS" | grep -q "cardPresent"; then
    pass "Card status endpoint"
else
    fail "Card status check failed: $CARD_STATUS"
fi

# Test 3: Encrypt via helper
echo ""
echo "Test 3: Encrypt plaintext..."
ENCRYPT_PAYLOAD=$(cat <<EOF
{
  "body": "$TEST_MESSAGE",
  "recipients": ["$RECIPIENT"]
}
EOF
)

ENCRYPT_RESPONSE=$(curl -k -s -X POST "$HELPER_URL/encrypt" \
    -H "Content-Type: application/json" \
    -d "$ENCRYPT_PAYLOAD")

if echo "$ENCRYPT_RESPONSE" | grep -q "armored"; then
    ARMORED=$(echo "$ENCRYPT_RESPONSE" | grep -o '"armored":"[^"]*"' | sed 's/"armored":"\(.*\)"/\1/' | sed 's/\\n/\n/g')
    pass "Encryption via helper"
else
    fail "Encryption failed: $ENCRYPT_RESPONSE"
fi

# Save encrypted message to temp file
TEMP_FILE=$(mktemp)
echo "$ARMORED" > "$TEMP_FILE"

# Test 4: Decrypt via helper
echo ""
echo "Test 4: Decrypt via helper..."
DECRYPT_PAYLOAD=$(cat <<EOF
{
  "body": $(echo "$ARMORED" | jq -Rs .)
}
EOF
)

DECRYPT_RESPONSE=$(curl -k -s -X POST "$HELPER_URL/decrypt" \
    -H "Content-Type: application/json" \
    -d "$DECRYPT_PAYLOAD")

if echo "$DECRYPT_RESPONSE" | grep -q "plaintext"; then
    PLAINTEXT=$(echo "$DECRYPT_RESPONSE" | grep -o '"plaintext":"[^"]*"' | sed 's/"plaintext":"\(.*\)"/\1/')
    if [ "$PLAINTEXT" = "$TEST_MESSAGE" ]; then
        pass "Decryption via helper"
    else
        fail "Decrypted text mismatch. Expected '$TEST_MESSAGE', got '$PLAINTEXT'"
    fi
else
    fail "Decryption failed: $DECRYPT_RESPONSE"
fi

# Test 5: Cross-check with GPG CLI
echo ""
echo "Test 5: Cross-check decryption with GPG CLI..."
GPG_DECRYPT=$(gpg --decrypt "$TEMP_FILE" 2>/dev/null || echo "FAILED")
if [ "$GPG_DECRYPT" = "$TEST_MESSAGE" ]; then
    pass "GPG CLI cross-check"
else
    fail "GPG decrypt mismatch. Expected '$TEST_MESSAGE', got '$GPG_DECRYPT'"
fi

# Clean up
rm -f "$TEMP_FILE"

# Summary
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}All tests passed!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Helper encrypt/decrypt and GPG interop verified successfully."
echo ""
echo "Additional manual tests available:"
echo "  - POST /generate-keypair (requires admin PIN)"
echo "  - POST /change-pin (requires current PIN)"
echo "  - POST /delete-keypair (requires admin PIN)"
