package com.aepgp.encryptor.apdu

import com.aepgp.encryptor.card.CardChannel
import java.io.IOException

class OpenPGPCard(private val channel: CardChannel) {

    @Throws(IOException::class)
    fun selectApplet(): Boolean {
        val apdu = byteArrayOf(
            0x00,
            0xA4.toByte(),
            0x04,
            0x00,
            0x06,
            0xD2.toByte(),
            0x76,
            0x00,
            0x01,
            0x24,
            0x01
        )
        val response = channel.transceive(apdu)
        return isSuccess(response)
    }

    private fun isSuccess(response: ByteArray): Boolean {
        val size = response.size
        if (size < 2) return false
        return response[size - 2] == 0x90.toByte() && response[size - 1] == 0x00.toByte()
    }
}
