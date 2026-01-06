package com.aepgp.encryptor.utils

import android.content.ContentResolver
import android.content.Context
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream

object FileUtils {
    private const val DEFAULT_BUFFER = 64 * 1024

    fun tempFile(context: Context, prefix: String, suffix: String): File =
        File.createTempFile(prefix, suffix, context.cacheDir)

    fun pipe(
        input: InputStream,
        output: OutputStream,
        bufferSize: Int = DEFAULT_BUFFER,
        onProgress: (Long) -> Unit = {}
    ): Long {
        val buffer = ByteArray(bufferSize)
        var total: Long = 0
        while (true) {
            val read = input.read(buffer)
            if (read <= 0) break
            output.write(buffer, 0, read)
            total += read
            onProgress(total)
        }
        output.flush()
        return total
    }

    fun readFully(input: InputStream, length: Int): ByteArray {
        val result = ByteArray(length)
        var offset = 0
        while (offset < length) {
            val read = input.read(result, offset, length - offset)
            if (read == -1) throw IOException("Unexpected EOF, need $length bytes")
            offset += read
        }
        return result
    }

    fun getFileName(context: Context, uri: Uri): String? {
        return DocumentFile.fromSingleUri(context, uri)?.name
    }

    fun openInput(contentResolver: ContentResolver, uri: Uri): InputStream {
        return contentResolver.openInputStream(uri)
            ?: throw IOException("Unable to open input stream for $uri")
    }

    fun openOutput(contentResolver: ContentResolver, uri: Uri): OutputStream {
        return contentResolver.openOutputStream(uri, "w")
            ?: throw IOException("Unable to open output stream for $uri")
    }

    fun size(context: Context, uri: Uri): Long? {
        return DocumentFile.fromSingleUri(context, uri)?.length()
    }
}
