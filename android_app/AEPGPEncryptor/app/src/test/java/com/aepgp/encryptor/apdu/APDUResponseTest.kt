package com.aepgp.encryptor.apdu

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class APDUResponseTest {

    @Test
    fun `parses success response`() {
        val raw = byteArrayOf(0x01, 0x02, 0x90.toByte(), 0x00)
        val response = APDUResponse.from(raw)

        assertArrayEquals(byteArrayOf(0x01, 0x02), response.data)
        assertEquals(0x90, response.sw1)
        assertEquals(0x00, response.sw2)
        assertTrue(response.isSuccess)
        assertEquals(0x9000, response.statusWord)
    }

    @Test
    fun `parses failure response`() {
        val raw = byteArrayOf(0x6A.toByte(), 0x82.toByte())
        val response = APDUResponse.from(raw)

        assertEquals(0x6A, response.sw1)
        assertEquals(0x82, response.sw2)
        assertEquals(0x6A82, response.statusWord)
    }
}
