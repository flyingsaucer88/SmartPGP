package com.aepgp.encryptor.crypto

import com.aepgp.encryptor.utils.FileUtils
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.security.interfaces.RSAPublicKey
import javax.crypto.SecretKey

class AEPGPCrypto(
    private val aes: AESEncryption = AESEncryption(),
    private val rsa: RSAEncryption = RSAEncryption()
) {

    data class EncryptMetadata(
        val rsaEncryptedKeyLength: Int,
        val bytesProcessed: Long
    )

    fun interface RsaDecryptor {
        @Throws(IOException::class)
        fun decrypt(ciphertext: ByteArray): ByteArray
    }

    @Throws(IOException::class)
    fun encryptStream(
        input: InputStream,
        output: OutputStream,
        publicKeyBytes: ByteArray,
        onProgress: (Long) -> Unit = {}
    ): EncryptMetadata {
        val normalizedKey = CryptoUtils.normalizeRsaPublicKey(publicKeyBytes)
        val publicKey: RSAPublicKey = rsa.loadPublicKey(normalizedKey)

        val aesKey: SecretKey = aes.generateKey()
        val rsaWrappedKey = rsa.encryptKey(aesKey, publicKey)

        val tempFile = File.createTempFile("aepgp_enc_", ".tmp")
        val aesResult = aes.encryptToTempFile(aesKey, input, tempFile, onProgress)

        output.write(CryptoUtils.toBigEndianUInt(rsaWrappedKey.size))
        output.write(rsaWrappedKey)
        output.write(aesResult.iv)
        output.write(aesResult.authTag)

        tempFile.inputStream().use { cipherIn ->
            FileUtils.pipe(cipherIn, output)
        }
        tempFile.delete()

        return EncryptMetadata(
            rsaEncryptedKeyLength = rsaWrappedKey.size,
            bytesProcessed = aesResult.bytesProcessed
        )
    }

    @Throws(IOException::class)
    fun decryptStream(
        input: InputStream,
        output: OutputStream,
        decryptor: RsaDecryptor,
        onProgress: (Long) -> Unit = {}
    ): Long {
        val keyLengthBytes = FileUtils.readFully(input, 4)
        val keyLength = CryptoUtils.readBigEndianUInt(keyLengthBytes)
        if (keyLength <= 0) throw IOException("Invalid encrypted AES key length: $keyLength")

        val rsaEncryptedKey = FileUtils.readFully(input, keyLength)
        val aesKeyBytes = decryptor.decrypt(rsaEncryptedKey)
        val aesKey = aes.keyFromBytes(aesKeyBytes)

        val iv = FileUtils.readFully(input, AESEncryption.GCM_IV_LENGTH)
        val tag = FileUtils.readFully(input, AESEncryption.GCM_TAG_LENGTH_BYTES)

        return aes.decryptStream(aesKey, iv, tag, input, output, onProgress)
    }
}
