package com.aepgp.encryptor.utils

import android.util.Log

object Logger {
    private const val DEFAULT_TAG = "AEPGP"

    fun d(message: String, tag: String = DEFAULT_TAG) {
        Log.d(tag, message)
    }

    fun w(message: String, tag: String = DEFAULT_TAG, throwable: Throwable? = null) {
        Log.w(tag, message, throwable)
    }

    fun e(message: String, tag: String = DEFAULT_TAG, throwable: Throwable? = null) {
        Log.e(tag, message, throwable)
    }
}
