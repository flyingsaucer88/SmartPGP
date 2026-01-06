package com.aepgp.encryptor

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbManager
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.aepgp.encryptor.apdu.OpenPGPCard
import com.aepgp.encryptor.business.CardManager
import com.aepgp.encryptor.card.CardChannel
import com.aepgp.encryptor.card.CardSessionManager
import com.aepgp.encryptor.databinding.ActivityCardManagementBinding
import com.aepgp.encryptor.nfc.CardReader
import com.aepgp.encryptor.nfc.NFCCardManager
import com.aepgp.encryptor.ui.dialogs.ErrorDialog
import com.aepgp.encryptor.usb.CardReaderUsb
import com.aepgp.encryptor.usb.UsbCardManager
import com.aepgp.encryptor.usb.UsbPermissionHelper
import kotlinx.coroutines.launch
import java.io.IOException

class CardManagementActivity : AppCompatActivity() {

    private lateinit var binding: ActivityCardManagementBinding
    private lateinit var nfcManager: NFCCardManager
    private lateinit var nfcReader: CardReader
    private lateinit var usbManager: UsbCardManager
    private lateinit var usbReader: CardReaderUsb
    private lateinit var sessionManager: CardSessionManager
    private var cardManager: CardManager? = null
    private var activeChannel: CardChannel? = null

    private val usbReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                UsbManager.ACTION_USB_DEVICE_ATTACHED -> handleIntent(intent)
                UsbManager.ACTION_USB_DEVICE_DETACHED -> setStatus(getString(R.string.status_ready))
                UsbPermissionHelper.ACTION_USB_PERMISSION -> {
                    val device = usbReader.deviceFromPermissionIntent(intent)
                    device?.let { sessionManager.connectFromUsbDevice(it)?.let { channel -> bindChannel(channel) } }
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCardManagementBinding.inflate(layoutInflater)
        setContentView(binding.root)

        nfcManager = NFCCardManager(this)
        nfcReader = CardReader(nfcManager)
        usbManager = UsbCardManager(this)
        usbReader = CardReaderUsb(usbManager)
        sessionManager = CardSessionManager(nfcReader, usbReader)

        binding.generateKeyButton.setOnClickListener { generateKeyPair() }
        binding.changePinButton.setOnClickListener { changePin() }

        handleIntent(intent)
    }

    override fun onResume() {
        super.onResume()
        nfcManager.enableForegroundDispatch()
        usbManager.registerReceiver(usbReceiver)
    }

    override fun onPause() {
        super.onPause()
        nfcManager.disableForegroundDispatch()
        usbManager.unregisterReceiver(usbReceiver)
    }

    override fun onDestroy() {
        super.onDestroy()
        activeChannel?.close()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        if (intent == null) return
        val channel = sessionManager.connectFromIntent(intent)
        channel?.let { bindChannel(it) }
    }

    private fun bindChannel(channel: CardChannel) {
        activeChannel?.close()
        activeChannel = channel
        cardManager = CardManager(OpenPGPCard(channel))
        setStatus(getString(R.string.status_detected))
    }

    private fun generateKeyPair() {
        val manager = cardManager ?: run {
            setStatus(getString(R.string.status_waiting_card))
            return
        }
        lifecycleScope.launch {
            try {
                val pub = manager.generateEncryptionKeyPair()
                binding.keygenStatus.text = getString(R.string.key_loaded) + " (${pub.size} bytes)"
            } catch (e: IOException) {
                ErrorDialog.newInstance(e.message ?: getString(R.string.status_failed))
                    .show(supportFragmentManager, "error")
            }
        }
    }

    private fun changePin() {
        val manager = cardManager ?: run {
            setStatus(getString(R.string.status_waiting_card))
            return
        }
        val oldPin = binding.oldPinInput.text?.toString()?.toCharArray() ?: CharArray(0)
        val newPin = binding.newPinInput.text?.toString()?.toCharArray() ?: CharArray(0)
        lifecycleScope.launch {
            try {
                val success = manager.changePin(oldPin, newPin)
                binding.pinStatus.text = if (success) getString(R.string.change_pin) else getString(R.string.status_failed)
            } catch (e: IOException) {
                ErrorDialog.newInstance(e.message ?: getString(R.string.status_failed))
                    .show(supportFragmentManager, "error")
            }
        }
    }

    private fun setStatus(text: String) {
        binding.keygenStatus.text = text
        binding.pinStatus.text = text
    }
}
