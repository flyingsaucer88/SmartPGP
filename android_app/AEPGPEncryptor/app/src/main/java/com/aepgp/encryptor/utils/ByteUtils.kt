package com.aepgp.encryptor.utils

object ByteUtils {
    fun toHex(bytes: ByteArray): String = bytes.joinToString("") { "%02X".format(it) }

    fun fromHex(hex: String): ByteArray {
        val clean = hex.replace("\\s".toRegex(), "")
        require(clean.length % 2 == 0) { "Hex must have even length" }
        return ByteArray(clean.length / 2) { i ->
            clean.substring(i * 2, i * 2 + 2).toInt(16).toByte()
        }
    }

    fun concat(vararg arrays: ByteArray): ByteArray {
        val total = arrays.sumOf { it.size }
        val result = ByteArray(total)
        var offset = 0
        arrays.forEach { arr ->
            System.arraycopy(arr, 0, result, offset, arr.size)
            offset += arr.size
        }
        return result
    }

    /**
     * Very small TLV helper for one-byte tags (used by OpenPGP public key blobs).
     */
    fun simpleTlvParse(data: ByteArray): Map<Int, ByteArray> {
        val map = mutableMapOf<Int, ByteArray>()
        var idx = 0
        while (idx < data.size - 1) {
            val tag = data[idx].toInt() and 0xFF
            val len = data[idx + 1].toInt() and 0xFF
            val start = idx + 2
            val end = (start + len).coerceAtMost(data.size)
            map[tag] = data.copyOfRange(start, end)
            idx = end
        }
        return map
    }
}
