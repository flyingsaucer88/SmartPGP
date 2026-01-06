package com.aepgp.encryptor

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbManager
import android.net.Uri
import android.os.Bundle
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.aepgp.encryptor.apdu.OpenPGPCard
import com.aepgp.encryptor.business.CardManager
import com.aepgp.encryptor.business.FileDecryptor
import com.aepgp.encryptor.card.CardChannel
import com.aepgp.encryptor.card.CardSessionManager
import com.aepgp.encryptor.databinding.ActivityDecryptBinding
import com.aepgp.encryptor.nfc.CardReader
import com.aepgp.encryptor.nfc.NFCCardManager
import com.aepgp.encryptor.ui.dialogs.ErrorDialog
import com.aepgp.encryptor.usb.CardReaderUsb
import com.aepgp.encryptor.usb.UsbCardManager
import com.aepgp.encryptor.usb.UsbPermissionHelper
import kotlinx.coroutines.launch
import java.io.IOException

class DecryptActivity : AppCompatActivity() {

    private var binding: ActivityDecryptBinding? = null
    private val ui get() = binding!!
    private lateinit var decryptor: FileDecryptor

    private lateinit var nfcManager: NFCCardManager
    private lateinit var nfcReader: CardReader
    private lateinit var usbManager: UsbCardManager
    private lateinit var usbReader: CardReaderUsb
    private lateinit var sessionManager: CardSessionManager
    private var cardManager: CardManager? = null
    private var activeChannel: CardChannel? = null

    private var encryptedUri: Uri? = null
    private var outputUri: Uri? = null

    private val selectEncryptedLauncher =
        registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
            if (uri != null) {
                contentResolver.takePersistableUriPermission(
                    uri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION
                )
                encryptedUri = uri
                ui.encryptedFileText.text = uri.lastPathSegment ?: uri.toString()
                outputUri = null
            }
        }

    private val createOutputLauncher =
        registerForActivityResult(ActivityResultContracts.CreateDocument("application/octet-stream")) { uri ->
            if (uri != null) {
                outputUri = uri
                startDecryption()
            }
        }

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
        val bind = ActivityDecryptBinding.inflate(layoutInflater)
        binding = bind
        setContentView(bind.root)

        decryptor = FileDecryptor(this)
        nfcManager = NFCCardManager(this)
        nfcReader = CardReader(nfcManager)
        usbManager = UsbCardManager(this)
        usbReader = CardReaderUsb(usbManager)
        sessionManager = CardSessionManager(nfcReader, usbReader)

        ui.selectEncryptedButton.setOnClickListener { selectEncryptedLauncher.launch(arrayOf("*/*")) }
        ui.decryptButton.setOnClickListener { prepareOutputAndDecrypt() }

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
        binding = null
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

    private fun prepareOutputAndDecrypt() {
        val input = encryptedUri
        if (input == null) {
            setStatus(getString(R.string.no_file_selected))
            return
        }
        if (cardManager == null) {
            setStatus(getString(R.string.status_waiting_card))
            return
        }
        if (outputUri == null) {
            val suggested = (ui.encryptedFileText.text?.toString() ?: "decrypted").removeSuffix(".enc")
            createOutputLauncher.launch(suggested)
        } else {
            startDecryption()
        }
    }

    private fun startDecryption() {
        val input = encryptedUri ?: return
        val output = outputUri ?: return
        val manager = cardManager ?: return

        setStatus(getString(R.string.working))
        val decryptor = manager.rsaDecryptor()
        lifecycleScope.launch {
            try {
                try {
                    manager.ensureSelected()
                } catch (_: IOException) {
                }
                this@DecryptActivity.decryptor.decryptFile(input, output, decryptor) { processed, total ->
                    val totalText = total?.let { "/$it bytes" } ?: ""
                    setStatus("Decrypted $processed$totalText")
                }
                setStatus(getString(R.string.decryption_complete))
            } catch (e: Exception) {
                setStatus(getString(R.string.status_failed))
                ErrorDialog.newInstance(e.message ?: getString(R.string.status_failed))
                    .show(supportFragmentManager, "error")
            }
        }
    }

    private fun setStatus(text: String) {
        ui.decryptStatus.text = text
    }
}
