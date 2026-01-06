package com.aepgp.encryptor.sdk

import android.app.Activity
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.net.Uri
import com.aepgp.encryptor.apdu.OpenPGPCard
import com.aepgp.encryptor.business.CardManager
import com.aepgp.encryptor.business.FileDecryptor
import com.aepgp.encryptor.business.FileEncryptor
import com.aepgp.encryptor.card.CardChannel
import com.aepgp.encryptor.card.CardSessionManager
import com.aepgp.encryptor.nfc.CardReader
import com.aepgp.encryptor.nfc.NFCCardManager
import com.aepgp.encryptor.usb.CardReaderUsb
import com.aepgp.encryptor.usb.UsbCardManager
import com.aepgp.encryptor.usb.UsbPermissionHelper
import java.io.IOException

/**
 * High-level facade that hides APDU details. Consumers handle intents and call encrypt/decrypt,
 * and the client manages NFC/USB connections plus OpenPGP commands internally.
 */
class SmartPGPClient(private val activity: Activity) {

    private val nfcManager = NFCCardManager(activity)
    private val nfcReader = CardReader(nfcManager)
    private val usbManager = UsbCardManager(activity)
    private val usbReader = CardReaderUsb(usbManager)
    private val sessionManager = CardSessionManager(nfcReader, usbReader)

    private val encryptor = FileEncryptor(activity)
    private val decryptor = FileDecryptor(activity)

    private var activeChannel: CardChannel? = null
    private var cardManager: CardManager? = null

    private val usbReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                UsbManager.ACTION_USB_DEVICE_ATTACHED -> handleIntent(intent)
                UsbManager.ACTION_USB_DEVICE_DETACHED -> closeChannel()
                UsbPermissionHelper.ACTION_USB_PERMISSION -> {
                    val device = usbReader.deviceFromPermissionIntent(intent)
                    device?.let { connectUsbDevice(it) }
                }
            }
        }
    }

    fun onResume() {
        nfcManager.enableForegroundDispatch()
        usbManager.registerReceiver(usbReceiver)
    }

    fun onPause() {
        nfcManager.disableForegroundDispatch()
        usbManager.unregisterReceiver(usbReceiver)
    }

    fun onDestroy() = closeChannel()

    /**
     * Handle NFC/USB intents from an Activity or BroadcastReceiver.
     * @return true if a card channel was established.
     */
    fun handleIntent(intent: Intent?): Boolean {
        if (intent == null) return false
        val channel = sessionManager.connectFromIntent(intent) ?: return false
        bindChannel(channel)
        return true
    }

    /**
     * Connects directly from an attached USB device.
     */
    fun connectUsbDevice(device: UsbDevice): Boolean {
        val channel = sessionManager.connectFromUsbDevice(device) ?: return false
        bindChannel(channel)
        return true
    }

    suspend fun fetchPublicKey(): ByteArray {
        val manager = requireCardManager()
        manager.ensureSelected()
        return manager.readEncryptionPublicKey()
    }

    suspend fun encryptFile(
        input: Uri,
        output: Uri,
        onProgress: (Long, Long?) -> Unit = { _, _ -> }
    ) {
        val key = fetchPublicKey()
        encryptor.encryptFile(input, output, key, onProgress)
    }

    suspend fun decryptFile(
        input: Uri,
        output: Uri,
        onProgress: (Long, Long?) -> Unit = { _, _ -> }
    ) {
        val manager = requireCardManager()
        manager.ensureSelected()
        val rsaDecryptor = manager.rsaDecryptor()
        decryptor.decryptFile(input, output, rsaDecryptor, onProgress)
    }

    suspend fun verifyPin(pin: CharArray): Boolean {
        val manager = requireCardManager()
        return manager.verifyPin(pin)
    }

    suspend fun changePin(oldPin: CharArray, newPin: CharArray): Boolean {
        val manager = requireCardManager()
        return manager.changePin(oldPin, newPin)
    }

    suspend fun generateKeyPair(): ByteArray {
        val manager = requireCardManager()
        return manager.generateEncryptionKeyPair()
    }

    fun hasActiveCard(): Boolean = cardManager != null

    private fun bindChannel(channel: CardChannel) {
        activeChannel?.close()
        activeChannel = channel
        cardManager = CardManager(OpenPGPCard(channel))
    }

    private fun closeChannel() {
        try {
            activeChannel?.close()
        } catch (_: IOException) {
        } finally {
            activeChannel = null
            cardManager = null
        }
    }

    private fun requireCardManager(): CardManager =
        cardManager ?: throw IllegalStateException("Card not connected. Call handleIntent first.")
}
