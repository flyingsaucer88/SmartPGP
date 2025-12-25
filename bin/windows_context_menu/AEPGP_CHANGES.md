# AEPGP-Specific Configuration

## Important Changes

This AEPGP version has been customized with the following specific requirements:

### 1. AmbiSecure Token Detection

The card detection has been **restricted to only accept AmbiSecure tokens** with the specific ATR:

```
3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F
```

**What this means:**
- Only AmbiSecure tokens with this exact ATR will be recognized
- Other OpenPGP cards will be ignored, even if they have the correct applet
- This ensures compatibility only with your specific hardware

### 2. Branding

All user-facing text has been rebranded from "SmartPGP" to "AEPGP":
- Context menu items show "Encrypt/Decrypt with **AEPGP**"
- Dialog titles and messages use "**AEPGP**"
- Error messages reference "**AEPGP card**"

### 3. GnuPG Initialization - USER LEVEL ONLY

**IMPORTANT**: GnuPG initialization happens at the **USER level**, NOT during applet installation.

#### When Installing the Applet (Developer/Admin):
- You install the SmartPGP applet onto the JavaCard
- This programs the card hardware
- No user keys are involved

#### When Setting Up for End Users (ONE-TIME per user):
Each user must initialize their card with GnuPG **once** before using encryption:

```cmd
gpg --card-edit
> admin
> generate
```

This generates their **personal encryption keys** on the card.

**Why?** Each user needs their own unique cryptographic identity. This is like creating a user account - it's done once per user, not during software installation.

## Technical Implementation Details

### Modified Files

1. **[card_utils.py](handlers/card_utils.py)**
   - Added `AMBISECURE_ATR` constant with the specific ATR
   - Added `verify_ambisecure_atr()` function to check ATR
   - Modified `find_aepgp_card()` to verify ATR before accepting card
   - Renamed all classes and functions from SmartPGP to AEPGP

2. **[encrypt_handler.py](handlers/encrypt_handler.py)**
   - Updated to call `find_aepgp_card()` instead of `find_smartpgp_card()`
   - Changed all user-facing messages to use "AEPGP"

3. **[decrypt_handler.py](handlers/decrypt_handler.py)**
   - Updated to call `find_aepgp_card()` instead of `find_smartpgp_card()`
   - Changed all user-facing messages to use "AEPGP"

4. **[install_menu.py](install_menu.py)**
   - Registry keys now use `AEPGP.Encrypt` and `AEPGP.Decrypt`
   - Context menu text shows "Encrypt/Decrypt with AEPGP"

5. **[uninstall_menu.py](uninstall_menu.py)**
   - Updated to remove AEPGP registry keys

6. **Batch Files**
   - [INSTALL.bat](INSTALL.bat)
   - [UNINSTALL.bat](UNINSTALL.bat)

### ATR Verification Flow

```
User inserts card
     ↓
Python reads ATR
     ↓
Compare with AMBISECURE_ATR
     ↓
If match → Try to select OpenPGP applet
If no match → Skip this card
     ↓
If applet selection succeeds → Return card connection
If fails → Try next reader
```

## Testing Your Configuration

Run the test script to verify everything is configured correctly:

```cmd
python test_setup.py
```

This will check:
- Python installation
- pyscard library
- Card reader detection
- **AmbiSecure token detection (with ATR verification)**
- GnuPG installation
- Context menu installation

## User Documentation Updates Needed

**Note**: The README.md and QUICKSTART.md files still contain references to "SmartPGP" in some technical/internal sections. For end-user documentation, you may want to create simplified versions that:

1. Only mention "AEPGP" (never "SmartPGP")
2. Clearly explain the one-time GnuPG initialization requirement
3. Specify that only AmbiSecure tokens are supported
4. Provide your organization's support contact information

## Deployment Checklist

Before distributing to end users:

- [ ] Update README.md with AEPGP branding (if needed for end users)
- [ ] Update QUICKSTART.md with AEPGP branding (if needed for end users)
- [ ] Test with actual AmbiSecure token (ATR: 3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F)
- [ ] Test that cards with different ATRs are properly rejected
- [ ] Verify GnuPG initialization workflow with end users
- [ ] Create internal documentation about the AppInit level vs User level setup distinction
- [ ] Package for distribution (consider creating an installer)

## Support Information

### For Card Detection Issues

If users report "AEPGP card not found" errors:

1. **Verify ATR**: Have them run this command to check their card's ATR:
   ```cmd
   python -c "from smartcard.System import readers; r=readers()[0]; c=r.createConnection(); c.connect(); from smartcard.util import toHexString; print(toHexString(c.getATR()))"
   ```

2. **Expected Output**: `3B D5 18 FF 81 B1 FE 45 1F C3 80 73 C8 21 10 6F`

3. **If Different**: The card is not an AmbiSecure token or has different firmware

### For GnuPG Initialization Issues

If users haven't initialized GnuPG:

```cmd
gpg --card-status
```

Should show card information. If not, guide them through:

```cmd
gpg --card-edit
> admin
> generate
> (follow prompts to create keys)
> quit
```

## License

This is a derivative work based on the SmartPGP project by ANSSI, customized for AEPGP deployment with AmbiSecure tokens. The underlying SmartPGP codebase remains under GPL v2.
