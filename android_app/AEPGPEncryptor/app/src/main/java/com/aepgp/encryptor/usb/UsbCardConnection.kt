package com.aepgp.encryptor.usb

import android.hardware.usb.UsbConstants
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbDeviceConnection
import android.hardware.usb.UsbEndpoint
import android.hardware.usb.UsbInterface
import android.hardware.usb.UsbManager
import com.aepgp.encryptor.card.CardChannel
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.atomic.AtomicInteger

class UsbCardConnection(
    private val usbManager: UsbManager,
    private val device: UsbDevice
) : CardChannel {

    private var deviceConnection: UsbDeviceConnection? = null
    private var smartCardInterface: UsbInterface? = null
    private var bulkIn: UsbEndpoint? = null
    private var bulkOut: UsbEndpoint? = null
    private val seqNumber = AtomicInteger(0)

    override fun connect(): Boolean {
        val connection = usbManager.openDevice(device) ?: return false
        val targetInterface = findSmartCardInterface(device) ?: return false

        if (!connection.claimInterface(targetInterface, true)) {
            connection.close()
            return false
        }

        val out = findEndpoint(targetInterface, UsbConstants.USB_DIR_OUT)
        val `in` = findEndpoint(targetInterface, UsbConstants.USB_DIR_IN)
        if (out == null || `in` == null) {
            connection.releaseInterface(targetInterface)
            connection.close()
            return false
        }

        deviceConnection = connection
        smartCardInterface = targetInterface
        bulkOut = out
        bulkIn = `in`
        return true
    }

    @Throws(IOException::class)
    override fun transceive(apdu: ByteArray): ByteArray {
        val connection = deviceConnection ?: throw IOException("USB device not connected")
        val outEndpoint = bulkOut ?: throw IOException("USB OUT endpoint missing")
        val inEndpoint = bulkIn ?: throw IOException("USB IN endpoint missing")

        val seq = seqNumber.getAndIncrement() and 0xFF
        val header = ByteBuffer.allocate(PC_TO_RDR_HEADER_SIZE).order(ByteOrder.LITTLE_ENDIAN)
        header.put(PC_TO_RDR_XFR_BLOCK)
        header.putInt(apdu.size)
        header.put(SLOT_NUMBER)
        header.put(seq.toByte())
        header.put(0x00) // bBWI (block waiting time)
        header.putShort(0) // wLevelParameter

        val frame = ByteArray(PC_TO_RDR_HEADER_SIZE + apdu.size)
        System.arraycopy(header.array(), 0, frame, 0, PC_TO_RDR_HEADER_SIZE)
        System.arraycopy(apdu, 0, frame, PC_TO_RDR_HEADER_SIZE, apdu.size)

        val written = connection.bulkTransfer(outEndpoint, frame, frame.size, DEFAULT_TIMEOUT_MS)
        if (written != frame.size) {
            throw IOException("Failed to write APDU to reader (sent $written/${frame.size})")
        }

        val responseBuffer = ByteArray(MAX_RESPONSE_SIZE)
        val read = connection.bulkTransfer(inEndpoint, responseBuffer, responseBuffer.size, DEFAULT_TIMEOUT_MS)
        if (read <= 0) throw IOException("No response from card reader")

        if (responseBuffer[0] != RDR_TO_PC_DATABLOCK) {
            throw IOException("Unexpected CCID message type: 0x${responseBuffer[0].toInt().and(0xFF).toString(16)}")
        }

        val respLength = ByteBuffer.wrap(responseBuffer, 1, 4)
            .order(ByteOrder.LITTLE_ENDIAN)
            .int
        val status = responseBuffer[7].toInt() and 0xFF
        val error = responseBuffer[8].toInt() and 0xFF
        if (status and STATUS_ERROR_MASK != 0 || error != 0) {
            throw IOException("CCID error status=$status error=$error")
        }

        val dataOffset = RDR_TO_PC_HEADER_SIZE
        val totalDataLength = respLength.coerceAtMost(read - dataOffset)
        if (totalDataLength <= 0) throw IOException("Empty response from card")

        val apduResponse = ByteArray(totalDataLength)
        System.arraycopy(responseBuffer, dataOffset, apduResponse, 0, totalDataLength)
        return apduResponse
    }

    override fun close() {
        try {
            smartCardInterface?.let { iface ->
                deviceConnection?.releaseInterface(iface)
            }
        } catch (_: Exception) {
        } finally {
            try {
                deviceConnection?.close()
            } catch (_: Exception) {
            }
            deviceConnection = null
            smartCardInterface = null
            bulkIn = null
            bulkOut = null
        }
    }

    override fun isConnected(): Boolean = deviceConnection != null

    private fun findSmartCardInterface(device: UsbDevice): UsbInterface? {
        for (i in 0 until device.interfaceCount) {
            val intf = device.getInterface(i)
            val isSmartCard =
                intf.interfaceClass == SMART_CARD_CLASS ||
                    (intf.interfaceClass == UsbConstants.USB_CLASS_VENDOR_SPEC &&
                        intf.interfaceSubclass == SMART_CARD_CLASS)
            if (isSmartCard) return intf
        }
        return null
    }

    private fun findEndpoint(intf: UsbInterface, direction: Int): UsbEndpoint? {
        for (i in 0 until intf.endpointCount) {
            val ep = intf.getEndpoint(i)
            if (ep.type == UsbConstants.USB_ENDPOINT_XFER_BULK && ep.direction == direction) {
                return ep
            }
        }
        return null
    }

    companion object {
        private const val SLOT_NUMBER: Byte = 0x00
        private const val DEFAULT_TIMEOUT_MS = 10_000
        private const val PC_TO_RDR_XFR_BLOCK: Byte = 0x6F
        private const val RDR_TO_PC_DATABLOCK: Byte = -0x80 // 0x80
        private const val PC_TO_RDR_HEADER_SIZE = 10
        private const val RDR_TO_PC_HEADER_SIZE = 10
        private const val STATUS_ERROR_MASK = 0xC0
        private const val MAX_RESPONSE_SIZE = 4096
        private const val SMART_CARD_CLASS = 0x0B
    }
}
