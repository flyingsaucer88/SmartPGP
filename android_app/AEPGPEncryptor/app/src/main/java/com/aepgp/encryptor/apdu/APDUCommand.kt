package com.aepgp.encryptor.apdu

/**
 * Helper for constructing ISO 7816 APDUs.
 *
 * Supports case 1-4 APDUs with optional Le. All numeric parameters are expected
 * to be in the range 0-255.
 */
data class APDUCommand(
    val cla: Int,
    val ins: Int,
    val p1: Int,
    val p2: Int,
    val data: ByteArray = byteArrayOf(),
    val le: Int? = null
) {
    fun toByteArray(): ByteArray {
        val hasLc = data.isNotEmpty()
        val hasLe = le != null
        val lc = if (hasLc) data.size else 0

        val header = byteArrayOf(
            cla.toByte(),
            ins.toByte(),
            p1.toByte(),
            p2.toByte()
        )

        return when {
            hasLc && hasLe -> {
                ByteArray(5 + lc + 1).apply {
                    System.arraycopy(header, 0, this, 0, 4)
                    this[4] = lc.toByte()
                    System.arraycopy(data, 0, this, 5, lc)
                    this[lastIndex] = le!!.toByte()
                }
            }

            hasLc -> {
                ByteArray(5 + lc).apply {
                    System.arraycopy(header, 0, this, 0, 4)
                    this[4] = lc.toByte()
                    System.arraycopy(data, 0, this, 5, lc)
                }
            }

            hasLe -> {
                ByteArray(5).apply {
                    System.arraycopy(header, 0, this, 0, 4)
                    this[4] = le!!.toByte()
                }
            }

            else -> header
        }
    }

    companion object {
        fun select(aid: ByteArray): APDUCommand =
            APDUCommand(
                cla = CardConstants.CLA,
                ins = CardConstants.INS_SELECT,
                p1 = 0x04,
                p2 = 0x00,
                data = aid
            )

        fun getData(p1: Int, p2: Int, le: Int = 0x00): APDUCommand =
            APDUCommand(
                cla = CardConstants.CLA,
                ins = CardConstants.INS_GET_DATA,
                p1 = p1,
                p2 = p2,
                le = le
            )

        fun putData(p1: Int, p2: Int, data: ByteArray): APDUCommand =
            APDUCommand(
                cla = CardConstants.CLA,
                ins = CardConstants.INS_PUT_DATA,
                p1 = p1,
                p2 = p2,
                data = data
            )
    }
}
