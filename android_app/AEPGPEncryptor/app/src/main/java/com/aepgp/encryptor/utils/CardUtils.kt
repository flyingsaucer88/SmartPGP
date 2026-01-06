package com.aepgp.encryptor.utils

object CardUtils {
    // ATR prefix for AmbiSecure / AEPGP tokens (can be extended as we validate more samples)
    private val AMBISECURE_ATR_PREFIX = byteArrayOf(0x3B, 0xFA.toByte(), 0x18, 0x00)

    fun isAmbiSecureAtr(atr: ByteArray): Boolean {
        if (atr.size < AMBISECURE_ATR_PREFIX.size) return false
        return AMBISECURE_ATR_PREFIX.indices.all { idx ->
            atr[idx] == AMBISECURE_ATR_PREFIX[idx]
        }
    }

    fun statusWordToMessage(sw: Int): String = when (sw) {
        0x9000 -> "Success"
        0x6300 -> "Authentication failed"
        0x6982 -> "Security status not satisfied"
        0x6983 -> "Authentication blocked"
        0x6A82 -> "File or key not found"
        else -> "Card error 0x${sw.toString(16)}"
    }
}
