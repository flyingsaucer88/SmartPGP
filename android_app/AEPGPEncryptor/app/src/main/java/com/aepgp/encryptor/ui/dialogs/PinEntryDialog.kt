package com.aepgp.encryptor.ui.dialogs

import android.app.Dialog
import android.os.Bundle
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.DialogFragment
import com.aepgp.encryptor.R
import com.google.android.material.textfield.TextInputEditText

class PinEntryDialog : DialogFragment() {

    interface Listener {
        fun onPinEntered(pin: CharArray)
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val view = requireActivity().layoutInflater.inflate(R.layout.dialog_pin_entry, null)
        val input = view.findViewById<TextInputEditText>(R.id.pinInput)

        return AlertDialog.Builder(requireContext())
            .setTitle(R.string.pin_required)
            .setView(view)
            .setPositiveButton(android.R.string.ok) { _, _ ->
                val pinChars = input.text?.toString()?.toCharArray() ?: CharArray(0)
                (parentFragment as? Listener ?: activity as? Listener)?.onPinEntered(pinChars)
            }
            .setNegativeButton(android.R.string.cancel, null)
            .create()
    }
}
