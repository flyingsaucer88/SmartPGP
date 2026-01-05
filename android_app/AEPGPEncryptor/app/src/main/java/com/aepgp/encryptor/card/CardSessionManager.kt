package com.aepgp.encryptor.card

import android.content.Intent
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.nfc.NfcAdapter
import com.aepgp.encryptor.nfc.CardReader
import com.aepgp.encryptor.usb.CardReaderUsb

/**
 * Chooses the first available card channel from NFC or USB based on incoming intents.
 */
class CardSessionManager(
    private val nfcReader: CardReader,
    private val usbReader: CardReaderUsb
    ) {

    fun connectFromIntent(intent: Intent): CardChannel? {
        return when (intent.action) {
            NfcAdapter.ACTION_TECH_DISCOVERED,
            NfcAdapter.ACTION_TAG_DISCOVERED,
            NfcAdapter.ACTION_NDEF_DISCOVERED -> {
                nfcReader.connectFromIntent(intent)
            }
            UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                usbReader.deviceFromAttachIntent(intent)?.let { usbReader.connect(it) }
            }
            else -> {
                usbReader.deviceFromPermissionIntent(intent)?.let { usbReader.connect(it) }
            }
        }
    }

    fun connectFromUsbDevice(device: UsbDevice): CardChannel? = usbReader.connect(device)
}
