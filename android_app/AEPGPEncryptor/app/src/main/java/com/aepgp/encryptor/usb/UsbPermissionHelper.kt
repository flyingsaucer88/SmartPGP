package com.aepgp.encryptor.usb

import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build

object UsbPermissionHelper {
    const val ACTION_USB_PERMISSION = "com.aepgp.encryptor.USB_PERMISSION"

    fun createPermissionIntent(context: Context): PendingIntent {
        val flags = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE
        } else {
            PendingIntent.FLAG_UPDATE_CURRENT
        }
        return PendingIntent.getBroadcast(context, 0, Intent(ACTION_USB_PERMISSION), flags)
    }
}
