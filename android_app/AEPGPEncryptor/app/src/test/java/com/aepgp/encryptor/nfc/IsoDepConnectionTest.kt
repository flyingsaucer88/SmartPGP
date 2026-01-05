package com.aepgp.encryptor.nfc

import android.nfc.tech.IsoDep
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.mockito.Mockito.doNothing
import org.mockito.Mockito.doThrow
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.mockito.kotlin.whenever
import java.io.IOException

class IsoDepConnectionTest {

    @Test
    fun `connect returns true when IsoDep connects`() {
        val isoDep = mock(IsoDep::class.java)
        doNothing().`when`(isoDep).connect()
        whenever(isoDep.isConnected).thenReturn(true)

        val connection = IsoDepConnection(isoDep)
        val result = connection.connect()

        assertTrue(result)
        verify(isoDep).timeout = 5_000
        verify(isoDep).connect()
    }

    @Test
    fun `connect returns false when IsoDep throws`() {
        val isoDep = mock(IsoDep::class.java)
        doThrow(IOException("fail")).`when`(isoDep).connect()

        val connection = IsoDepConnection(isoDep)
        val result = connection.connect()

        assertFalse(result)
    }

    @Test(expected = IOException::class)
    fun `transceive throws when not connected`() {
        val isoDep = mock(IsoDep::class.java)
        whenever(isoDep.isConnected).thenReturn(false)

        val connection = IsoDepConnection(isoDep)
        connection.transceive(byteArrayOf(0x00))
    }

    @Test
    fun `transceive returns response when connected`() {
        val isoDep = mock(IsoDep::class.java)
        val request = byteArrayOf(0x00, 0xA4.toByte())
        val response = byteArrayOf(0x90.toByte(), 0x00)
        whenever(isoDep.isConnected).thenReturn(true)
        whenever(isoDep.transceive(request)).thenReturn(response)

        val connection = IsoDepConnection(isoDep)
        val result = connection.transceive(request)

        assertArrayEquals(response, result)
        verify(isoDep).transceive(request)
    }
}
