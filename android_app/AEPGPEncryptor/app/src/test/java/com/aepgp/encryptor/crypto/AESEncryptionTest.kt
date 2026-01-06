package com.aepgp.encryptor.crypto

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Test
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.security.SecureRandom

class AESEncryptionTest {

    @Test
    fun `encrypt and decrypt stream round trip`() {
        val aes = AESEncryption(SecureRandom())
        val key = aes.generateKey()
        val plaintext = ByteArray(2048) { (it % 256).toByte() }

        val cipherOut = ByteArrayOutputStream()
        val result = aes.encryptStream(key, ByteArrayInputStream(plaintext), cipherOut)

        val decryptedOut = ByteArrayOutputStream()
        val processed = aes.decryptStream(
            key = key,
            iv = result.iv,
            authTag = result.authTag,
            cipherInput = ByteArrayInputStream(cipherOut.toByteArray()),
            plainOutput = decryptedOut
        )

        assertEquals(plaintext.size.toLong(), processed)
        assertArrayEquals(plaintext, decryptedOut.toByteArray())
    }
}
