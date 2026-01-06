package com.aepgp.encryptor.crypto

import org.bouncycastle.jce.provider.BouncyCastleProvider
import java.security.KeyFactory
import java.security.PublicKey
import java.security.Security
import java.security.interfaces.RSAPublicKey
import java.security.spec.X509EncodedKeySpec
import javax.crypto.Cipher
import javax.crypto.SecretKey

class RSAEncryption {
    private val provider = BouncyCastleProvider()

    init {
        if (Security.getProvider(provider.name) == null) {
            Security.addProvider(provider)
        }
    }

    fun loadPublicKey(encoded: ByteArray): RSAPublicKey {
        val spec = X509EncodedKeySpec(encoded)
        val factory = KeyFactory.getInstance("RSA")
        return factory.generatePublic(spec) as RSAPublicKey
    }

    fun encryptKey(aesKey: SecretKey, publicKey: RSAPublicKey): ByteArray {
        return encrypt(publicKey, aesKey.encoded)
    }

    fun encrypt(publicKey: PublicKey, data: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding", provider)
        cipher.init(Cipher.ENCRYPT_MODE, publicKey)
        return cipher.doFinal(data)
    }
}
