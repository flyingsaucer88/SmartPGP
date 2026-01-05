package com.aepgp.encryptor.usb

import android.content.Intent
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import com.aepgp.encryptor.card.CardChannel

class CardReaderUsb(private val usbCardManager: UsbCardManager) {

    fun deviceFromAttachIntent(intent: Intent?): UsbDevice? =
        usbCardManager.handleAttachIntent(intent)

    fun deviceFromPermissionIntent(intent: Intent?): UsbDevice? =
        usbCardManager.handlePermissionResult(intent)

    fun connect(device: UsbDevice): CardChannel? {
        if (!usbCardManager.hasPermission(device)) {
            usbCardManager.requestPermission(device)
            return null
        }
        val connection = usbCardManager.openConnection(device) ?: return null
        return if (connection.connect()) connection else connection.also { it.close() }
    }
}
