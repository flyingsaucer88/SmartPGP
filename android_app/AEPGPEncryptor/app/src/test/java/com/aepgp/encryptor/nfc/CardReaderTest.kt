package com.aepgp.encryptor.nfc

import android.content.Intent
import android.nfc.NfcAdapter
import android.nfc.tech.IsoDep
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.mockito.Mockito.doNothing
import org.mockito.Mockito.mock
import org.mockito.kotlin.whenever
import java.io.IOException

class CardReaderTest {

    @Test
    fun `hasReadyNfc true when available and enabled`() {
        val manager = mock(NFCCardManager::class.java)
        whenever(manager.isNfcAvailable()).thenReturn(true)
        whenever(manager.isNfcEnabled()).thenReturn(true)

        val reader = CardReader(manager)
        assertTrue(reader.hasReadyNfc())
    }

    @Test
    fun `hasReadyNfc false when NFC disabled or missing`() {
        val manager = mock(NFCCardManager::class.java)
        whenever(manager.isNfcAvailable()).thenReturn(true)
        whenever(manager.isNfcEnabled()).thenReturn(false)

        val reader = CardReader(manager)
        assertFalse(reader.hasReadyNfc())
    }

    @Test
    fun `connectFromIntent returns connection on success`() {
        val intent = Intent(NfcAdapter.ACTION_TECH_DISCOVERED)
        val manager = mock(NFCCardManager::class.java)
        val isoDep = mock(IsoDep::class.java)

        whenever(manager.handleIntent(intent)).thenReturn(isoDep)
        doNothing().`when`(isoDep).connect()
        whenever(isoDep.isConnected).thenReturn(true)

        val reader = CardReader(manager)
        val connection = reader.connectFromIntent(intent)

        assertNotNull(connection)
        assertTrue(connection?.isConnected() == true)
    }

    @Test
    fun `connectFromIntent returns null when handleIntent fails`() {
        val intent = Intent(NfcAdapter.ACTION_TECH_DISCOVERED)
        val manager = mock(NFCCardManager::class.java)
        whenever(manager.handleIntent(intent)).thenReturn(null)

        val reader = CardReader(manager)
        val connection = reader.connectFromIntent(intent)

        assertNull(connection)
    }

    @Test
    fun `connectFromIntent returns null when connect throws`() {
        val intent = Intent(NfcAdapter.ACTION_TECH_DISCOVERED)
        val manager = mock(NFCCardManager::class.java)
        val isoDep = mock(IsoDep::class.java)

        whenever(manager.handleIntent(intent)).thenReturn(isoDep)
        org.mockito.Mockito.doThrow(IOException("fail")).`when`(isoDep).connect()

        val reader = CardReader(manager)
        val connection = reader.connectFromIntent(intent)

        assertNull(connection)
    }
}
