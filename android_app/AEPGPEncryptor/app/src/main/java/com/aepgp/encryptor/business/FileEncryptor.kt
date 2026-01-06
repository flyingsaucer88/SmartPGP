package com.aepgp.encryptor.business

import android.content.Context
import android.net.Uri
import com.aepgp.encryptor.crypto.AEPGPCrypto
import com.aepgp.encryptor.utils.FileUtils
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException

class FileEncryptor(
    private val context: Context,
    private val crypto: AEPGPCrypto = AEPGPCrypto()
) {

    /**
     * Encrypts the file at [inputUri] to [outputUri] using the provided RSA public key bytes.
     */
    suspend fun encryptFile(
        inputUri: Uri,
        outputUri: Uri,
        publicKey: ByteArray,
        onProgress: (Long, Long?) -> Unit = { _, _ -> }
    ) = withContext(Dispatchers.IO) {
        val totalSize = FileUtils.size(context, inputUri)
        val resolver = context.contentResolver
        resolver.openInputStream(inputUri)?.use { input ->
            resolver.openOutputStream(outputUri, "w")?.use { output ->
                crypto.encryptStream(context, input, output, publicKey) { processed ->
                    onProgress(processed, totalSize)
                }
            } ?: throw IOException("Unable to open output $outputUri")
        } ?: throw IOException("Unable to open input $inputUri")
    }
}
