package com.aepgp.encryptor.crypto

import org.junit.Assert.assertEquals
import org.junit.Test
import java.security.KeyPairGenerator
import javax.crypto.Cipher

class RSAEncryptionTest {

    @Test
    fun `rsa encrypts with public and decrypts with private key`() {
        val generator = KeyPairGenerator.getInstance("RSA")
        generator.initialize(2048)
        val keyPair = generator.generateKeyPair()

        val rsa = RSAEncryption()
        val message = "hello-smartpgp".toByteArray()
        val cipherText = rsa.encrypt(keyPair.public, message)

        val cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding")
        cipher.init(Cipher.DECRYPT_MODE, keyPair.private)
        val plain = cipher.doFinal(cipherText)

        assertEquals("hello-smartpgp", String(plain))
    }
}
