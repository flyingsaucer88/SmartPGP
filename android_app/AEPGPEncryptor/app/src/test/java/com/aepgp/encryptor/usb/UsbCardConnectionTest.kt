package com.aepgp.encryptor.usb

import android.hardware.usb.UsbConstants
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbDeviceConnection
import android.hardware.usb.UsbEndpoint
import android.hardware.usb.UsbInterface
import android.hardware.usb.UsbManager
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.mockito.ArgumentMatchers.anyInt
import org.mockito.Mockito.eq
import org.mockito.Mockito.same
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import java.nio.ByteBuffer
import java.nio.ByteOrder

class UsbCardConnectionTest {

    @Test
    fun `connect succeeds when interface and endpoints exist`() {
        val usbManager = mock<UsbManager>()
        val device = buildMockDevice()
        val connection = mock<UsbDeviceConnection>()

        whenever(usbManager.openDevice(device)).thenReturn(connection)
        whenever(connection.claimInterface(any(), eq(true))).thenReturn(true)

        val cardConnection = UsbCardConnection(usbManager, device)
        assertTrue(cardConnection.connect())
    }

    @Test
    fun `connect fails when openDevice returns null`() {
        val usbManager = mock<UsbManager>()
        val device = mock<UsbDevice>()

        whenever(usbManager.openDevice(device)).thenReturn(null)

        val cardConnection = UsbCardConnection(usbManager, device)
        assertFalse(cardConnection.connect())
    }

    @Test
    fun `transceive sends APDU and returns response`() {
        val usbManager = mock<UsbManager>()
        val device = buildMockDevice()
        val connection = mock<UsbDeviceConnection>()
        val outEndpoint = device.getInterface(0).getEndpoint(0)
        val inEndpoint = device.getInterface(0).getEndpoint(1)

        whenever(usbManager.openDevice(device)).thenReturn(connection)
        whenever(connection.claimInterface(any(), eq(true))).thenReturn(true)

        // Outgoing bulk transfer writes full frame
        whenever(
            connection.bulkTransfer(
                same(outEndpoint),
                any(),
                anyInt(),
                anyInt()
            )
        ).thenAnswer { invocation ->
            invocation.getArgument<ByteArray>(1).size
        }

        // Incoming bulk transfer fills a CCID response with SW=9000
        whenever(
            connection.bulkTransfer(
                same(inEndpoint),
                any(),
                anyInt(),
                anyInt()
            )
        ).thenAnswer { invocation ->
            val buffer = invocation.getArgument<ByteArray>(1)
            val responseData = byteArrayOf(0x90.toByte(), 0x00)
            val header = ByteBuffer.allocate(10).order(ByteOrder.LITTLE_ENDIAN)
            header.put(0x80.toByte())
            header.putInt(responseData.size)
            header.put(0x00) // slot
            header.put(0x00) // seq
            header.put(0x00) // status
            header.put(0x00) // error
            header.put(0x00) // chain
            val resp = header.array() + responseData
            System.arraycopy(resp, 0, buffer, 0, resp.size)
            resp.size
        }

        val cardConnection = UsbCardConnection(usbManager, device)
        assertTrue(cardConnection.connect())

        val command = byteArrayOf(0x00, 0xA4.toByte(), 0x04, 0x00)
        val response = cardConnection.transceive(command)

        assertArrayEquals(byteArrayOf(0x90.toByte(), 0x00), response)
    }

    private fun buildMockDevice(): UsbDevice {
        val device = mock<UsbDevice>()
        val iface = mock<UsbInterface>()
        val outEndpoint = mock<UsbEndpoint>()
        val inEndpoint = mock<UsbEndpoint>()

        whenever(device.interfaceCount).thenReturn(1)
        whenever(device.getInterface(0)).thenReturn(iface)

        whenever(iface.interfaceClass).thenReturn(0x0B)
        whenever(iface.endpointCount).thenReturn(2)
        whenever(iface.getEndpoint(0)).thenReturn(outEndpoint)
        whenever(iface.getEndpoint(1)).thenReturn(inEndpoint)

        whenever(outEndpoint.type).thenReturn(UsbConstants.USB_ENDPOINT_XFER_BULK)
        whenever(outEndpoint.direction).thenReturn(UsbConstants.USB_DIR_OUT)

        whenever(inEndpoint.type).thenReturn(UsbConstants.USB_ENDPOINT_XFER_BULK)
        whenever(inEndpoint.direction).thenReturn(UsbConstants.USB_DIR_IN)

        return device
    }
}
