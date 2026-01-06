package com.aepgp.encryptor.ui.dialogs

import android.app.Dialog
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.DialogFragment
import com.aepgp.encryptor.R

class ProgressDialog : DialogFragment() {

    private var messageView: TextView? = null

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val view = requireActivity().layoutInflater.inflate(R.layout.dialog_progress, null)
        messageView = view.findViewById(R.id.progressText)

        return AlertDialog.Builder(requireContext())
            .setView(view)
            .setCancelable(false)
            .create()
    }

    fun updateMessage(message: String) {
        messageView?.text = message
    }
}
