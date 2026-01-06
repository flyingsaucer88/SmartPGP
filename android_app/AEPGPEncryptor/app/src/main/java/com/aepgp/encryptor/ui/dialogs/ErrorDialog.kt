package com.aepgp.encryptor.ui.dialogs

import android.app.Dialog
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.DialogFragment
import com.aepgp.encryptor.R

class ErrorDialog : DialogFragment() {

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val view = requireActivity().layoutInflater.inflate(R.layout.dialog_error, null)
        val message = arguments?.getString(ARG_MESSAGE) ?: getString(R.string.error_generic)
        view.findViewById<TextView>(R.id.errorMessage).text = message

        return AlertDialog.Builder(requireContext())
            .setTitle(R.string.error_generic)
            .setView(view)
            .setPositiveButton(android.R.string.ok, null)
            .create()
    }

    companion object {
        private const val ARG_MESSAGE = "msg"

        fun newInstance(message: String): ErrorDialog {
            val dialog = ErrorDialog()
            dialog.arguments = Bundle().apply { putString(ARG_MESSAGE, message) }
            return dialog
        }
    }
}
