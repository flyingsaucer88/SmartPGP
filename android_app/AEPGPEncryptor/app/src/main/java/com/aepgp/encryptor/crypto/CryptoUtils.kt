package com.aepgp.encryptor.crypto

import com.aepgp.encryptor.utils.ByteUtils
import java.math.BigInteger
import java.security.KeyFactory
import java.security.PublicKey
import java.security.spec.RSAPublicKeySpec

object CryptoUtils {
    /**
        * Attempts to normalize an OpenPGP card public key blob into a standard X.509 encoded RSA key.
        * If the data already appears to be DER (starts with SEQUENCE 0x30), it is returned unchanged.
        */
    fun normalizeRsaPublicKey(cardData: ByteArray): ByteArray {
        if (cardData.isNotEmpty() && cardData[0] == 0x30.toByte()) return cardData

        val tlv = ByteUtils.simpleTlvParse(cardData)
        val modulus = tlv[0x81]
        val exponent = tlv[0x82]
        if (modulus != null && exponent != null) {
            val spec = RSAPublicKeySpec(BigInteger(1, modulus), BigInteger(1, exponent))
            val factory = KeyFactory.getInstance("RSA")
            return factory.generatePublic(spec).encoded
        }
        return cardData
    }

    fun toBigEndianUInt(value: Int): ByteArray = byteArrayOf(
        ((value ushr 24) and 0xFF).toByte(),
        ((value ushr 16) and 0xFF).toByte(),
        ((value ushr 8) and 0xFF).toByte(),
        (value and 0xFF).toByte()
    )

    fun readBigEndianUInt(bytes: ByteArray, offset: Int = 0): Int {
        require(bytes.size - offset >= 4) { "Need 4 bytes to read uint" }
        return ((bytes[offset].toInt() and 0xFF) shl 24) or
            ((bytes[offset + 1].toInt() and 0xFF) shl 16) or
            ((bytes[offset + 2].toInt() and 0xFF) shl 8) or
            (bytes[offset + 3].toInt() and 0xFF)
    }

    fun toPublicKey(modulus: ByteArray, exponent: ByteArray): PublicKey {
        val spec = RSAPublicKeySpec(BigInteger(1, modulus), BigInteger(1, exponent))
        return KeyFactory.getInstance("RSA").generatePublic(spec)
    }
}
