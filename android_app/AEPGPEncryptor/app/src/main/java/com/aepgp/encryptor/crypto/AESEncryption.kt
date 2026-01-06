package com.aepgp.encryptor.crypto

import com.aepgp.encryptor.utils.FileUtils
import java.io.ByteArrayInputStream
import java.io.File
import java.io.InputStream
import java.io.OutputStream
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.CipherInputStream
import javax.crypto.CipherOutputStream
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

class AESEncryption(
    private val secureRandom: SecureRandom = SecureRandom()
) {

    data class AesEncryptResult(val iv: ByteArray, val authTag: ByteArray, val bytesProcessed: Long)

    fun generateKey(): SecretKey {
        val generator = KeyGenerator.getInstance("AES")
        generator.init(256, secureRandom)
        return generator.generateKey()
    }

    fun keyFromBytes(key: ByteArray): SecretKey = SecretKeySpec(key, "AES")

    fun encryptStream(
        key: SecretKey,
        input: InputStream,
        output: OutputStream,
        onProgress: (Long) -> Unit = {}
    ): AesEncryptResult {
        val iv = ByteArray(GCM_IV_LENGTH)
        secureRandom.nextBytes(iv)

        val cipher = Cipher.getInstance(AES_GCM_TRANSFORMATION)
        val params = GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv)
        cipher.init(Cipher.ENCRYPT_MODE, key, params)

        val tagSink = TagStrippingOutputStream(output, GCM_TAG_LENGTH_BYTES)
        val cipherOut = CipherOutputStream(tagSink, cipher)
        val bytesWritten = FileUtils.pipe(input, cipherOut, onProgress = onProgress)

        cipherOut.flush()
        cipherOut.close()

        val tag = tagSink.finish()
        return AesEncryptResult(iv = iv, authTag = tag, bytesProcessed = bytesWritten)
    }

    fun decryptStream(
        key: SecretKey,
        iv: ByteArray,
        authTag: ByteArray,
        cipherInput: InputStream,
        plainOutput: OutputStream,
        onProgress: (Long) -> Unit = {}
    ): Long {
        val cipher = Cipher.getInstance(AES_GCM_TRANSFORMATION)
        val params = GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, params)

        val combinedInput = cipherInput.sequenceWith(ByteArrayInputStream(authTag))
        val cipherIn = CipherInputStream(combinedInput, cipher)
        return FileUtils.pipe(cipherIn, plainOutput, onProgress = onProgress)
    }

    /**
     * Encrypts to a temporary file so we can obtain the tag before writing the final container header.
     */
    fun encryptToTempFile(
        key: SecretKey,
        input: InputStream,
        tempFile: File,
        onProgress: (Long) -> Unit = {}
    ): AesEncryptResult {
        tempFile.outputStream().use { out ->
            return encryptStream(key, input, out, onProgress)
        }
    }

    private fun InputStream.sequenceWith(next: InputStream): InputStream =
        java.io.SequenceInputStream(this, next)

    private class TagStrippingOutputStream(
        private val delegate: OutputStream,
        private val tagLength: Int
    ) : OutputStream() {
        private val tail = ArrayDeque<Byte>(tagLength)
        private var bytesWritten: Long = 0

        override fun write(b: Int) {
            write(byteArrayOf(b.toByte()), 0, 1)
        }

        override fun write(b: ByteArray, off: Int, len: Int) {
            for (i in off until off + len) {
                val value = b[i]
                if (tail.size == tagLength) {
                    delegate.write(tail.removeFirst().toInt())
                }
                tail.addLast(value)
                bytesWritten++
            }
        }

        override fun flush() {
            delegate.flush()
        }

        override fun close() {
            delegate.flush()
        }

        fun finish(): ByteArray {
            val tag = ByteArray(tail.size)
            var idx = 0
            while (tail.isNotEmpty()) {
                tag[idx++] = tail.removeFirst()
            }
            return tag
        }
    }

    companion object {
        private const val AES_GCM_TRANSFORMATION = "AES/GCM/NoPadding"
        private const val GCM_TAG_LENGTH_BITS = 128
        const val GCM_TAG_LENGTH_BYTES = GCM_TAG_LENGTH_BITS / 8
        const val GCM_IV_LENGTH = 12
    }
}
