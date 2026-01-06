package com.aepgp.encryptor.crypto

import android.content.Context
import org.junit.Assert.assertArrayEquals
import org.junit.Test
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.security.KeyPairGenerator
import java.io.File
import org.mockito.Mockito
import javax.crypto.Cipher

class AEPGPCryptoTest {

    @Test
    fun `encrypt stream produces readable container and decrypts`() {
        val generator = KeyPairGenerator.getInstance("RSA")
        generator.initialize(2048)
        val keyPair = generator.generateKeyPair()

        val crypto = AEPGPCrypto()
        val context = Mockito.mock(Context::class.java)
        val tempDir = File(System.getProperty("java.io.tmpdir"))
        Mockito.`when`(context.cacheDir).thenReturn(tempDir)
        val inputData = ByteArray(4096) { (it % 251).toByte() }

        val encryptedOut = ByteArrayOutputStream()
        crypto.encryptStream(context, ByteArrayInputStream(inputData), encryptedOut, keyPair.public.encoded)

        val decryptor = AEPGPCrypto.RsaDecryptor { ciphertext ->
            val cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding")
            cipher.init(Cipher.DECRYPT_MODE, keyPair.private)
            cipher.doFinal(ciphertext)
        }

        val decryptedOut = ByteArrayOutputStream()
        crypto.decryptStream(ByteArrayInputStream(encryptedOut.toByteArray()), decryptedOut, decryptor)

        assertArrayEquals(inputData, decryptedOut.toByteArray())
    }
}
