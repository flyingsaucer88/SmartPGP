package com.aepgp.encryptor.utils

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Test

class ByteUtilsTest {
    @Test
    fun `hex encode and decode round trip`() {
        val bytes = byteArrayOf(0x01, 0x2A, 0x7F, 0x00, 0xFF.toByte())
        val hex = ByteUtils.toHex(bytes)
        val decoded = ByteUtils.fromHex(hex)
        assertEquals("012A7F00FF", hex)
        assertArrayEquals(bytes, decoded)
    }

    @Test
    fun `tlv parse extracts tags`() {
        val tlv = byteArrayOf(0x81.toByte(), 0x02, 0x01, 0x02, 0x82.toByte(), 0x01, 0x03)
        val parsed = ByteUtils.simpleTlvParse(tlv)
        assertArrayEquals(byteArrayOf(0x01, 0x02), parsed[0x81])
        assertArrayEquals(byteArrayOf(0x03), parsed[0x82])
    }
}
