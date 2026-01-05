package com.aepgp.encryptor.nfc

import android.content.Intent

class CardReader(private val nfcCardManager: NFCCardManager) {
    fun hasReadyNfc(): Boolean = nfcCardManager.isNfcAvailable() && nfcCardManager.isNfcEnabled()

    fun connectFromIntent(intent: Intent, timeoutMs: Int = DEFAULT_TIMEOUT_MS): IsoDepConnection? {
        val isoDep = nfcCardManager.handleIntent(intent) ?: return null
        val connection = IsoDepConnection(isoDep)
        return if (connection.connect(timeoutMs)) {
            connection
        } else {
            connection.close()
            null
        }
    }

    companion object {
        private const val DEFAULT_TIMEOUT_MS = 5_000
    }
}
