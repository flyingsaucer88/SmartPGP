package com.aepgp.encryptor.apdu

import org.junit.Assert.assertArrayEquals
import org.junit.Test

class APDUCommandTest {

    @Test
    fun `select command builds correct APDU`() {
        val apdu = APDUCommand.select(CardConstants.OPENPGP_AID).toByteArray()
        val expected = byteArrayOf(
            0x00,
            0xA4.toByte(),
            0x04,
            0x00,
            0x06,
            0xD2.toByte(),
            0x76,
            0x00,
            0x01,
            0x24,
            0x01
        )
        assertArrayEquals(expected, apdu)
    }

    @Test
    fun `case 4 command encodes lc and le`() {
        val cmd = APDUCommand(
            cla = 0x00,
            ins = 0xCA,
            p1 = 0x00,
            p2 = 0x00,
            data = byteArrayOf(0x01, 0x02),
            le = 0x10
        )
        val expected = byteArrayOf(0x00, 0xCA.toByte(), 0x00, 0x00, 0x02, 0x01, 0x02, 0x10)
        assertArrayEquals(expected, cmd.toByteArray())
    }
}
