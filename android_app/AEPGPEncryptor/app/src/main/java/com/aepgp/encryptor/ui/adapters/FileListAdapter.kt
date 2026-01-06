package com.aepgp.encryptor.ui.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.documentfile.provider.DocumentFile
import androidx.recyclerview.widget.RecyclerView
import com.aepgp.encryptor.R
import java.text.DecimalFormat
import kotlin.math.ln
import kotlin.math.pow

class FileListAdapter(
    private val onClick: (DocumentFile) -> Unit
) : RecyclerView.Adapter<FileListAdapter.ViewHolder>() {

    private var items: List<DocumentFile> = emptyList()

    fun submitFiles(files: List<DocumentFile>) {
        items = files
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_file, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val file = items[position]
        holder.name.text = file.name ?: holder.itemView.context.getString(R.string.app_name)
        holder.size.text = humanReadableByteCount(file.length())
        holder.itemView.setOnClickListener { onClick(file) }
    }

    override fun getItemCount(): Int = items.size

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val name: TextView = view.findViewById(R.id.fileName)
        val size: TextView = view.findViewById(R.id.fileSize)
    }

    private fun humanReadableByteCount(bytes: Long): String {
        if (bytes < 0) return "?"
        if (bytes < 1024) return "$bytes B"
        val unit = 1024.0
        val exp = (ln(bytes.toDouble()) / ln(unit)).toInt()
        val pre = "KMGTPE"[exp - 1]
        return DecimalFormat("#,##0.#").format(bytes / unit.pow(exp.toDouble())) + " ${pre}B"
    }
}
