package com.aepgp.encryptor.card

import java.io.IOException

/**
 * Transport-agnostic card channel interface so NFC and USB connections can be used interchangeably.
 */
interface CardChannel {
    /**
     * Establishes a connection to the card.
     * @return true if the connection is established, false otherwise.
     */
    fun connect(): Boolean

    /**
     * Sends an APDU and returns the raw response (data + status words).
     */
    @Throws(IOException::class)
    fun transceive(apdu: ByteArray): ByteArray

    /** Closes the connection, ignoring errors. */
    fun close()

    /** Whether the channel is currently connected. */
    fun isConnected(): Boolean
}
