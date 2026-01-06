package com.aepgp.encryptor.apdu

/**
 * Parsed APDU response. Last two bytes represent SW1/SW2.
 */
data class APDUResponse(
    val data: ByteArray,
    val sw1: Int,
    val sw2: Int
) {
    val isSuccess: Boolean get() = sw1 == 0x90 && sw2 == 0x00
    val statusWord: Int get() = (sw1 shl 8) or sw2

    companion object {
        fun from(raw: ByteArray): APDUResponse {
            require(raw.size >= 2) { "APDU response must be at least 2 bytes" }
            val sw1 = raw[raw.size - 2].toInt() and 0xFF
            val sw2 = raw[raw.size - 1].toInt() and 0xFF
            val body = raw.copyOfRange(0, raw.size - 2)
            return APDUResponse(body, sw1, sw2)
        }
    }
}
