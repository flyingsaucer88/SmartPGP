package com.aepgp.encryptor.business

import android.content.Context
import android.net.Uri
import com.aepgp.encryptor.apdu.OpenPGPCard
import com.aepgp.encryptor.crypto.AEPGPCrypto
import com.aepgp.encryptor.utils.FileUtils
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException

class FileDecryptor(
    private val context: Context,
    private val crypto: AEPGPCrypto = AEPGPCrypto()
) {

    suspend fun decryptFile(
        inputUri: Uri,
        outputUri: Uri,
        decryptor: AEPGPCrypto.RsaDecryptor,
        onProgress: (Long, Long?) -> Unit = { _, _ -> }
    ) = withContext(Dispatchers.IO) {
        val totalSize = FileUtils.size(context, inputUri)
        val resolver = context.contentResolver
        resolver.openInputStream(inputUri)?.use { input ->
            resolver.openOutputStream(outputUri, "w")?.use { output ->
                crypto.decryptStream(input, output, decryptor) { processed ->
                    onProgress(processed, totalSize)
                }
            } ?: throw IOException("Unable to open output $outputUri")
        } ?: throw IOException("Unable to open input $inputUri")
    }

    /**
     * Convenience decryptor that uses PSO:DECIPHER on the provided OpenPGP card.
     */
    class CardDecryptor(private val card: OpenPGPCard) : AEPGPCrypto.RsaDecryptor {
        @Throws(IOException::class)
        override fun decrypt(ciphertext: ByteArray): ByteArray {
            if (!card.selectApplet()) throw IOException("Card SELECT failed")
            return card.psoDecipher(ciphertext)
        }
    }
}
