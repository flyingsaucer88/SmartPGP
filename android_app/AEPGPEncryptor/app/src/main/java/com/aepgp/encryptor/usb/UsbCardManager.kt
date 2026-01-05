package com.aepgp.encryptor.usb

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.os.Build

class UsbCardManager(private val context: Context) {
    private val usbManager: UsbManager? = context.getSystemService(Context.USB_SERVICE) as? UsbManager

    fun isUsbHostAvailable(): Boolean =
        context.packageManager.hasSystemFeature("android.hardware.usb.host")

    fun listReaders(): List<UsbDevice> {
        val manager = usbManager ?: return emptyList()
        return manager.deviceList.values.filter { isLikelyCcidReader(it) }
    }

    fun hasPermission(device: UsbDevice): Boolean {
        val manager = usbManager ?: return false
        return manager.hasPermission(device)
    }

    fun requestPermission(device: UsbDevice) {
        val manager = usbManager ?: return
        val pendingIntent = UsbPermissionHelper.createPermissionIntent(context)
        manager.requestPermission(device, pendingIntent)
    }

    fun openConnection(device: UsbDevice): UsbCardConnection? {
        val manager = usbManager ?: return null
        if (!manager.hasPermission(device)) return null
        return UsbCardConnection(manager, device)
    }

    fun registerReceiver(receiver: BroadcastReceiver): IntentFilter {
        val filter = IntentFilter().apply {
            addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED)
            addAction(UsbManager.ACTION_USB_DEVICE_DETACHED)
            addAction(UsbPermissionHelper.ACTION_USB_PERMISSION)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            context.registerReceiver(receiver, filter, Context.RECEIVER_NOT_EXPORTED)
        } else {
            @Suppress("DEPRECATION")
            context.registerReceiver(receiver, filter)
        }
        return filter
    }

    fun unregisterReceiver(receiver: BroadcastReceiver) {
        try {
            context.unregisterReceiver(receiver)
        } catch (_: IllegalArgumentException) {
            // Already unregistered
        }
    }

    fun handleAttachIntent(intent: Intent?): UsbDevice? {
        if (intent?.action != UsbManager.ACTION_USB_DEVICE_ATTACHED) return null
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
        }
    }

    fun handlePermissionResult(intent: Intent?): UsbDevice? {
        if (intent?.action != UsbPermissionHelper.ACTION_USB_PERMISSION) return null
        val granted = intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false)
        if (!granted) return null
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
        }
    }

    private fun isLikelyCcidReader(device: UsbDevice): Boolean {
        // CCID devices typically use class 0x0B (smart card). Some use vendor class with interfaces of 0x0B.
        if (device.deviceClass == UsbConstantsSmartCard.CLASS_SMART_CARD) return true
        for (i in 0 until device.interfaceCount) {
            val intf = device.getInterface(i)
            if (intf.interfaceClass == UsbConstantsSmartCard.CLASS_SMART_CARD) return true
        }
        return false
    }
}

private object UsbConstantsSmartCard {
    const val CLASS_SMART_CARD = 0x0B
}
