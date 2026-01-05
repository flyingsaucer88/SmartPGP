package com.aepgp.encryptor.usb

import android.content.Context
import android.content.pm.PackageManager
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever

class UsbCardManagerTest {

    @Test
    fun `listReaders filters for smart card class`() {
        val context = mock<Context>()
        val usbManager = mock<UsbManager>()
        val smartCardDevice = mock<UsbDevice>()
        val otherDevice = mock<UsbDevice>()

        whenever(context.getSystemService(Context.USB_SERVICE)).thenReturn(usbManager)
        whenever(smartCardDevice.deviceClass).thenReturn(0x0B) // smart card
        whenever(otherDevice.deviceClass).thenReturn(0x03) // HID
        whenever(usbManager.deviceList).thenReturn(
            mapOf("smart" to smartCardDevice, "other" to otherDevice)
        )

        val manager = UsbCardManager(context)
        val readers = manager.listReaders()
        assertEquals(1, readers.size)
        assertTrue(readers.contains(smartCardDevice))
    }

    @Test
    fun `isUsbHostAvailable uses feature flag`() {
        val context = mock<Context>()
        val pm = mock<PackageManager>()
        whenever(context.packageManager).thenReturn(pm)
        whenever(pm.hasSystemFeature(PackageManager.FEATURE_USB_HOST)).thenReturn(true)

        val manager = UsbCardManager(context)
        assertTrue(manager.isUsbHostAvailable())
    }
}
