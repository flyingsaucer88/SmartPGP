package com.aepgp.encryptor.business

import com.aepgp.encryptor.apdu.CardConstants
import com.aepgp.encryptor.apdu.OpenPGPCard
import com.aepgp.encryptor.crypto.AEPGPCrypto
import java.io.IOException

class CardManager(private val card: OpenPGPCard) {

    @Throws(IOException::class)
    fun ensureSelected() {
        if (!card.selectApplet()) throw IOException("Failed to select OpenPGP applet")
    }

    @Throws(IOException::class)
    fun verifyPin(pin: CharArray): Boolean {
        ensureSelected()
        return card.verifyPin(pin)
    }

    @Throws(IOException::class)
    fun readEncryptionPublicKey(): ByteArray {
        ensureSelected()
        return card.getPublicKey(CardConstants.DO_PUBKEY_DECRYPT)
    }

    @Throws(IOException::class)
    fun generateEncryptionKeyPair(): ByteArray {
        ensureSelected()
        return card.generateKeyPair(CardConstants.KEY_REF_DECRYPT)
    }

    @Throws(IOException::class)
    fun changePin(oldPin: CharArray, newPin: CharArray): Boolean {
        ensureSelected()
        return card.changePin(oldPin, newPin)
    }

    fun rsaDecryptor(): AEPGPCrypto.RsaDecryptor = AEPGPCrypto.RsaDecryptor { ciphertext ->
        ensureSelected()
        card.psoDecipher(ciphertext)
    }
}
