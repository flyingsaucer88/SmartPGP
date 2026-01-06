package com.aepgp.encryptor.apdu

import com.aepgp.encryptor.card.CardChannel
import java.io.IOException
import java.nio.charset.StandardCharsets

class OpenPGPCard(private val channel: CardChannel) {

    @Throws(IOException::class)
    fun selectApplet(): Boolean {
        val response = send(APDUCommand.select(CardConstants.OPENPGP_AID))
        return response.isSuccess
    }

    /**
     * Verifies the user PIN (PW1) using VERIFY command (INS 0x20).
     */
    @Throws(IOException::class)
    fun verifyPin(pin: CharArray): Boolean {
        val pinBytes = String(pin).toByteArray(StandardCharsets.US_ASCII)
        val command = APDUCommand(
            cla = CardConstants.CLA,
            ins = CardConstants.INS_VERIFY,
            p1 = 0x00,
            p2 = CardConstants.P2_PIN_USER,
            data = pinBytes
        )
        return send(command).isSuccess
    }

    /**
     * GET DATA to fetch a public key for a specific key reference.
     */
    @Throws(IOException::class)
    fun getPublicKey(keyRef: Int = CardConstants.DO_PUBKEY_DECRYPT): ByteArray {
        val response = send(APDUCommand.getData(CardConstants.DO_PUBKEY_PREFIX, keyRef))
        if (!response.isSuccess) throw IOException("GET PUBLIC KEY failed sw=${response.statusWord.toString(16)}")
        return response.data
    }

    /**
     * GENERATE ASYMMETRIC KEYPAIR for given key slot.
     */
    @Throws(IOException::class)
    fun generateKeyPair(keyRef: Int = CardConstants.KEY_REF_DECRYPT): ByteArray {
        val command = APDUCommand(
            cla = CardConstants.CLA,
            ins = CardConstants.INS_GEN_ASYM,
            p1 = 0x80,
            p2 = keyRef
        )
        val response = send(command)
        if (!response.isSuccess) throw IOException("Key generation failed sw=${response.statusWord.toString(16)}")
        return response.data
    }

    /**
     * Performs RSA private key decrypt (PSO:DECIPHER).
     */
    @Throws(IOException::class)
    fun psoDecipher(ciphertext: ByteArray): ByteArray {
        val command = APDUCommand(
            cla = CardConstants.CLA,
            ins = CardConstants.INS_PSO_DECIPHER,
            p1 = 0x80,
            p2 = 0x86,
            data = ciphertext
        )
        val response = send(command)
        if (!response.isSuccess) throw IOException("PSO:DECIPHER failed sw=${response.statusWord.toString(16)}")
        return response.data
    }

    /**
     * CHANGE REFERENCE DATA for user PIN.
     */
    @Throws(IOException::class)
    fun changePin(oldPin: CharArray, newPin: CharArray): Boolean {
        val oldBytes = String(oldPin).toByteArray(StandardCharsets.US_ASCII)
        val newBytes = String(newPin).toByteArray(StandardCharsets.US_ASCII)
        val payload = ByteArray(oldBytes.size + newBytes.size)
        System.arraycopy(oldBytes, 0, payload, 0, oldBytes.size)
        System.arraycopy(newBytes, 0, payload, oldBytes.size, newBytes.size)

        val command = APDUCommand(
            cla = CardConstants.CLA,
            ins = CardConstants.INS_CHANGE_REFERENCE_DATA,
            p1 = 0x00,
            p2 = CardConstants.P2_PIN_USER,
            data = payload
        )
        return send(command).isSuccess
    }

    /**
     * Generic PUT DATA for OpenPGP data objects.
     */
    @Throws(IOException::class)
    fun putData(p1: Int, p2: Int, data: ByteArray): Boolean {
        val response = send(APDUCommand.putData(p1, p2, data))
        return response.isSuccess
    }

    /**
     * Generic GET DATA for OpenPGP data objects.
     */
    @Throws(IOException::class)
    fun getData(p1: Int, p2: Int): ByteArray {
        val response = send(APDUCommand.getData(p1, p2))
        if (!response.isSuccess) throw IOException("GET DATA failed sw=${response.statusWord.toString(16)}")
        return response.data
    }

    @Throws(IOException::class)
    private fun send(command: APDUCommand): APDUResponse {
        val response = channel.transceive(command.toByteArray())
        return APDUResponse.from(response)
    }
}
