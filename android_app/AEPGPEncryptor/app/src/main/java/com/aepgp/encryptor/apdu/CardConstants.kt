package com.aepgp.encryptor.apdu

object CardConstants {
    val OPENPGP_AID: ByteArray = byteArrayOf(
        0xD2.toByte(),
        0x76.toByte(),
        0x00,
        0x01,
        0x24,
        0x01
    )

    const val CLA = 0x00
    const val INS_SELECT = 0xA4
    const val INS_VERIFY = 0x20
    const val INS_GET_DATA = 0xCA
    const val INS_PUT_DATA = 0xDA
    const val INS_PSO_DECIPHER = 0x2A
    const val INS_GEN_ASYM = 0x47
    const val INS_CHANGE_REFERENCE_DATA = 0x24

    // OpenPGP key references
    const val KEY_REF_SIGN = 0xB6
    const val KEY_REF_DECRYPT = 0xB8
    const val KEY_REF_AUTH = 0xA4

    // Data object tags (P1/P2 for GET/PUT DATA)
    const val DO_PUBKEY_PREFIX = 0x00
    const val DO_PUBKEY_SIGN = 0xC1
    const val DO_PUBKEY_DECRYPT = 0xC2
    const val DO_PUBKEY_AUTH = 0xC3

    // PIN references
    const val P2_PIN_USER = 0x81
    const val P2_PIN_RESET = 0x82
}
