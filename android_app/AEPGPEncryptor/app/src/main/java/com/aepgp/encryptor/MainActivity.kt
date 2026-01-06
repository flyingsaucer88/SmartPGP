package com.aepgp.encryptor

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.nfc.NfcAdapter
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.aepgp.encryptor.apdu.OpenPGPCard
import com.aepgp.encryptor.card.CardChannel
import com.aepgp.encryptor.card.CardSessionManager
import com.aepgp.encryptor.databinding.ActivityMainBinding
import com.aepgp.encryptor.nfc.CardReader
import com.aepgp.encryptor.nfc.NFCCardManager
import com.aepgp.encryptor.usb.CardReaderUsb
import com.aepgp.encryptor.usb.UsbCardManager
import com.aepgp.encryptor.usb.UsbPermissionHelper
import java.io.IOException

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var nfcCardManager: NFCCardManager
    private lateinit var nfcReader: CardReader
    private lateinit var usbCardManager: UsbCardManager
    private lateinit var usbReader: CardReaderUsb
    private lateinit var sessionManager: CardSessionManager

    private val usbReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                UsbManager.ACTION_USB_DEVICE_ATTACHED -> handleIntent(intent)
                UsbManager.ACTION_USB_DEVICE_DETACHED -> setStatus(getString(R.string.status_ready))
                UsbPermissionHelper.ACTION_USB_PERMISSION -> {
                    val device = usbReader.deviceFromPermissionIntent(intent)
                    device?.let { connectUsbDevice(it) }
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        nfcCardManager = NFCCardManager(this)
        nfcReader = CardReader(nfcCardManager)
        usbCardManager = UsbCardManager(this)
        usbReader = CardReaderUsb(usbCardManager)
        sessionManager = CardSessionManager(nfcReader, usbReader)

        binding.openEncrypt.setOnClickListener {
            startActivity(Intent(this, EncryptActivity::class.java))
        }
        binding.openDecrypt.setOnClickListener {
            startActivity(Intent(this, DecryptActivity::class.java))
        }
        binding.openCardMgmt.setOnClickListener {
            startActivity(Intent(this, CardManagementActivity::class.java))
        }

        handleIntent(intent)
    }

    override fun onResume() {
        super.onResume()
        nfcCardManager.enableForegroundDispatch()
        usbCardManager.registerReceiver(usbReceiver)
        setStatus(getString(R.string.status_ready))
    }

    override fun onPause() {
        super.onPause()
        nfcCardManager.disableForegroundDispatch()
        usbCardManager.unregisterReceiver(usbReceiver)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        if (intent == null) return
        when (intent.action) {
            NfcAdapter.ACTION_TECH_DISCOVERED,
            NfcAdapter.ACTION_TAG_DISCOVERED,
            NfcAdapter.ACTION_NDEF_DISCOVERED -> setStatus(getString(R.string.status_detected))
            UsbManager.ACTION_USB_DEVICE_ATTACHED -> setStatus(getString(R.string.status_detected))
        }
        val channel = sessionManager.connectFromIntent(intent)
        channel?.let { attemptSelect(it) }
    }

    private fun connectUsbDevice(device: UsbDevice) {
        val channel = sessionManager.connectFromUsbDevice(device)
        channel?.let { attemptSelect(it) }
    }

    private fun attemptSelect(channel: CardChannel) {
        try {
            val card = OpenPGPCard(channel)
            val selected = card.selectApplet()
            if (selected) {
                setStatus(getString(R.string.status_selected))
            } else {
                setStatus(getString(R.string.status_failed))
            }
        } catch (_: IOException) {
            setStatus(getString(R.string.status_failed))
        } finally {
            channel.close()
        }
    }

    private fun setStatus(text: String) {
        binding.statusText.text = text
    }
}
