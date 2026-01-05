# Android AEPGP Implementation & Test Plan

This document is for the Android developer to finish and verify the dual-mode (NFC + USB OTG) SmartPGP card support on-device.

## Prerequisites
- Android phone with NFC + USB OTG (USB-C preferred), Developer Options + USB debugging ON.
- CCID smart card reader + OTG adapter; AEPGP/OpenPGP smart card.
- Android Studio Hedgehog+ and JDK 17 installed.
- Branch: `Androidgpg`. Module: `android_app/AEPGPEncryptor`.
- If Gradle wrapper is missing, use local Gradle (`gradle ...`) or add wrapper (`gradle wrapper`).

## Build & Install
1) From module root (`android_app/AEPGPEncryptor`):
   - `gradle test` (or `./gradlew test` if wrapper present)
   - `gradle assembleDebug` (or `./gradlew assembleDebug`)
2) Install APK: `adb install -r app/build/outputs/apk/debug/app-debug.apk`
3) Enable NFC in system settings; grant storage permissions if prompted.

## App Behavior to Verify
- App listens for NFC (`IsoDep`) and USB CCID (`UsbManager`) via `CardChannel`.
- MainActivity handles NFC intents + USB attach/permission broadcasts.
- On detect (tap or attach), app runs SELECT OpenPGP applet and updates status.

## NFC Test Flow
1) Enable NFC; launch app.
2) Expect status: “Ready for NFC tap or USB card.”
3) Tap card; expect “Card detected” → “Card applet selected successfully.”
4) Remove card mid-way: expect failure message then recovery to “Ready”.
5) Reopen and re-tap: no crashes, consistent behavior.

## USB OTG Test Flow
1) Plug CCID reader via OTG; insert card.
2) On first attach, app requests permission; tap “Allow”.
3) Expect “Card detected” → “Card applet selected successfully.”
4) Unplug mid-session: status resets to “Ready”.
5) Reattach and confirm repeatability.

## Negative/Edge Cases
- Permission denied: graceful status; retry on next attach.
- Non-CCID USB device: ignored without crash.
- Weak NFC coupling: timeout + failure status; recovery afterward.
- Large APDU timeout (USB): failure surfaced; able to retry.

## Instrumentation & Logs
- NFC logs: `adb logcat -s NfcService,NfcDispatcher,IsoDep`
- USB logs: `adb logcat -s UsbHostManager UsbDeviceManager`
- App: use default logcat; add `Log.d` in MainActivity for tracing if needed.

## Test Matrix
- Devices: Pixel (Android 13/14) and Samsung (One UI) to cover OEM stacks.
- Readers: at least one CCID reader (e.g., ACS ACR122U/1252U or equivalent) + OTG adapter.
- Cards: AEPGP/OpenPGP card with applet.

## Next Implementation Steps (after smoke tests)
1) Expand APDU layer (`verifyPIN`, `getPublicKey`, `psoDecipher`) via `CardChannel`.
2) Build Encrypt/Decrypt flows using whichever channel is available (NFC or USB) with shared crypto.
3) Add UX for longer ops: progress + “keep card near / don’t unplug” hints; optional foreground service if needed.
4) Add UI affordances: “Retry” button, explicit “Use NFC/Use USB” badges, and clear error toasts.

## Handy Commands
- Run unit tests: `gradle test` (or `./gradlew test`).
- Build debug: `gradle assembleDebug` (or `./gradlew assembleDebug`).
- Install debug: `adb install -r app/build/outputs/apk/debug/app-debug.apk`
- Clear app data: `adb shell pm clear com.aepgp.encryptor`
