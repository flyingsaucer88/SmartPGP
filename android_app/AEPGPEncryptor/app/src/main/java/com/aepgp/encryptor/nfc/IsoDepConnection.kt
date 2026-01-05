package com.aepgp.encryptor.nfc

import android.nfc.tech.IsoDep
import com.aepgp.encryptor.card.CardChannel
import java.io.IOException

class IsoDepConnection(private val isoDep: IsoDep) : CardChannel {
    fun connect(timeoutMs: Int = DEFAULT_TIMEOUT_MS): Boolean {
        return try {
            isoDep.timeout = timeoutMs
            isoDep.connect()
            isoDep.isConnected
        } catch (_: IOException) {
            false
        }
    }

    override fun connect(): Boolean = connect(DEFAULT_TIMEOUT_MS)

    @Throws(IOException::class)
    override fun transceive(apdu: ByteArray): ByteArray {
        if (!isoDep.isConnected) throw IOException("IsoDep is not connected")
        return isoDep.transceive(apdu)
    }

    override fun close() {
        try {
            isoDep.close()
        } catch (_: IOException) {
            // No-op
        }
    }

    override fun isConnected(): Boolean = isoDep.isConnected

    companion object {
        private const val DEFAULT_TIMEOUT_MS = 5_000
    }
}
