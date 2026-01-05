// GPGME.swift
// Swift wrapper for GPGME C API

import Foundation

// GPGME C API declarations
// Note: In production, these should be in a module map or bridging header

typealias gpgme_ctx_t = OpaquePointer
typealias gpgme_data_t = OpaquePointer
typealias gpgme_key_t = OpaquePointer
typealias gpgme_error_t = UInt32

// GPGME function declarations (import from libgpgme)
@_silgen_name("gpgme_check_version")
func gpgme_check_version(_ req_version: UnsafePointer<CChar>?) -> UnsafePointer<CChar>?

@_silgen_name("gpgme_new")
func gpgme_new(_ ctx: UnsafeMutablePointer<gpgme_ctx_t?>) -> gpgme_error_t

@_silgen_name("gpgme_release")
func gpgme_release(_ ctx: gpgme_ctx_t)

@_silgen_name("gpgme_set_protocol")
func gpgme_set_protocol(_ ctx: gpgme_ctx_t, _ proto: Int32) -> gpgme_error_t

@_silgen_name("gpgme_set_armor")
func gpgme_set_armor(_ ctx: gpgme_ctx_t, _ yes: Int32)

@_silgen_name("gpgme_data_new")
func gpgme_data_new(_ dh: UnsafeMutablePointer<gpgme_data_t?>) -> gpgme_error_t

@_silgen_name("gpgme_data_new_from_mem")
func gpgme_data_new_from_mem(_ dh: UnsafeMutablePointer<gpgme_data_t?>, _ buffer: UnsafePointer<CChar>, _ size: Int, _ copy: Int32) -> gpgme_error_t

@_silgen_name("gpgme_data_release")
func gpgme_data_release(_ dh: gpgme_data_t)

@_silgen_name("gpgme_data_seek")
func gpgme_data_seek(_ dh: gpgme_data_t, _ offset: Int64, _ whence: Int32) -> Int64

@_silgen_name("gpgme_data_read")
func gpgme_data_read(_ dh: gpgme_data_t, _ buffer: UnsafeMutableRawPointer, _ length: Int) -> Int

@_silgen_name("gpgme_op_encrypt")
func gpgme_op_encrypt(_ ctx: gpgme_ctx_t, _ recp: OpaquePointer?, _ flags: UInt32, _ plain: gpgme_data_t, _ cipher: gpgme_data_t) -> gpgme_error_t

@_silgen_name("gpgme_op_decrypt")
func gpgme_op_decrypt(_ ctx: gpgme_ctx_t, _ cipher: gpgme_data_t, _ plain: gpgme_data_t) -> gpgme_error_t

@_silgen_name("gpgme_get_key")
func gpgme_get_key(_ ctx: gpgme_ctx_t, _ fpr: UnsafePointer<CChar>, _ r_key: UnsafeMutablePointer<gpgme_key_t?>, _ secret: Int32) -> gpgme_error_t

@_silgen_name("gpgme_key_release")
func gpgme_key_release(_ key: gpgme_key_t)

@_silgen_name("gpgme_signers_add")
func gpgme_signers_add(_ ctx: gpgme_ctx_t, _ key: gpgme_key_t) -> gpgme_error_t

@_silgen_name("gpgme_signers_clear")
func gpgme_signers_clear(_ ctx: gpgme_ctx_t)

@_silgen_name("gpgme_op_encrypt_sign")
func gpgme_op_encrypt_sign(_ ctx: gpgme_ctx_t, _ recp: OpaquePointer?, _ flags: UInt32, _ plain: gpgme_data_t, _ cipher: gpgme_data_t) -> gpgme_error_t

@_silgen_name("gpgme_strerror")
func gpgme_strerror(_ err: gpgme_error_t) -> UnsafePointer<CChar>?

// Constants
let GPGME_PROTOCOL_OpenPGP: Int32 = 0
let GPGME_ENCRYPT_ALWAYS_TRUST: UInt32 = 128
let SEEK_SET: Int32 = 0

/// Swift wrapper for GPGME context
class GPGMEContext {
    private var ctx: gpgme_ctx_t?

    init() throws {
        // Initialize GPGME
        _ = gpgme_check_version(nil)

        var context: gpgme_ctx_t?
        let err = gpgme_new(&context)
        guard err == 0, let ctx = context else {
            throw GPGMEError.initializationFailed("Failed to create GPGME context: \(err)")
        }

        self.ctx = ctx

        // Set protocol to OpenPGP
        gpgme_set_protocol(ctx, GPGME_PROTOCOL_OpenPGP)

        // Enable ASCII armor
        gpgme_set_armor(ctx, 1)
    }

    deinit {
        if let ctx = ctx {
            gpgme_release(ctx)
        }
    }

    func encrypt(_ plaintext: String, recipients: [String], signerId: String? = nil) throws -> String {
        guard let ctx = ctx else {
            throw GPGMEError.contextNotInitialized
        }

        // Create data buffers
        var plainData: gpgme_data_t?
        var cipherData: gpgme_data_t?

        defer {
            if let plainData = plainData {
                gpgme_data_release(plainData)
            }
            if let cipherData = cipherData {
                gpgme_data_release(cipherData)
            }
        }

        // Create plain data from string
        let plainBytes = plaintext.utf8CString
        let err1 = plainBytes.withUnsafeBufferPointer { buffer in
            gpgme_data_new_from_mem(&plainData, buffer.baseAddress, plainBytes.count - 1, 1)
        }
        guard err1 == 0, plainData != nil else {
            throw GPGMEError.dataCreationFailed("Failed to create plain data: \(err1)")
        }

        // Create cipher data buffer
        let err2 = gpgme_data_new(&cipherData)
        guard err2 == 0, cipherData != nil else {
            throw GPGMEError.dataCreationFailed("Failed to create cipher data: \(err2)")
        }

        // Get recipient keys
        var keys: [gpgme_key_t] = []
        defer {
            keys.forEach { gpgme_key_release($0) }
        }

        for recipient in recipients {
            var key: gpgme_key_t?
            let err = recipient.withCString { fpr in
                gpgme_get_key(ctx, fpr, &key, 0)
            }
            guard err == 0, let recipientKey = key else {
                throw GPGMEError.keyNotFound("Recipient key not found: \(recipient)")
            }
            keys.append(recipientKey)
        }

        // Build key array for encryption (NULL-terminated)
        var keyArray = keys.map { $0 as OpaquePointer? } + [nil]

        // Add signer if specified
        if let signerId = signerId {
            gpgme_signers_clear(ctx)
            var signerKey: gpgme_key_t?
            let err = signerId.withCString { fpr in
                gpgme_get_key(ctx, fpr, &signerKey, 1)
            }
            if err == 0, let signer = signerKey {
                gpgme_signers_add(ctx, signer)
                gpgme_key_release(signer)

                // Use encrypt_sign instead of encrypt
                let encErr = keyArray.withUnsafeMutableBufferPointer { keyBuf in
                    gpgme_op_encrypt_sign(ctx, OpaquePointer(keyBuf.baseAddress), GPGME_ENCRYPT_ALWAYS_TRUST, plainData!, cipherData!)
                }
                guard encErr == 0 else {
                    if let errStr = gpgme_strerror(encErr) {
                        throw GPGMEError.encryptionFailed(String(cString: errStr))
                    }
                    throw GPGMEError.encryptionFailed("Encryption failed: \(encErr)")
                }
            }
        } else {
            // Encrypt without signing
            let encErr = keyArray.withUnsafeMutableBufferPointer { keyBuf in
                gpgme_op_encrypt(ctx, OpaquePointer(keyBuf.baseAddress), GPGME_ENCRYPT_ALWAYS_TRUST, plainData!, cipherData!)
            }
            guard encErr == 0 else {
                if let errStr = gpgme_strerror(encErr) {
                    throw GPGMEError.encryptionFailed(String(cString: errStr))
                }
                throw GPGMEError.encryptionFailed("Encryption failed: \(encErr)")
            }
        }

        // Read encrypted data
        gpgme_data_seek(cipherData!, 0, SEEK_SET)
        var buffer = [CChar](repeating: 0, count: 65536)
        var result = Data()

        while true {
            let bytesRead = gpgme_data_read(cipherData!, &buffer, buffer.count)
            if bytesRead <= 0 { break }
            result.append(contentsOf: buffer.prefix(bytesRead))
        }

        guard let armored = String(data: result, encoding: .utf8) else {
            throw GPGMEError.encodingFailed("Failed to encode encrypted data")
        }

        return armored
    }

    func decrypt(_ ciphertext: String) throws -> String {
        guard let ctx = ctx else {
            throw GPGMEError.contextNotInitialized
        }

        var cipherData: gpgme_data_t?
        var plainData: gpgme_data_t?

        defer {
            if let cipherData = cipherData {
                gpgme_data_release(cipherData)
            }
            if let plainData = plainData {
                gpgme_data_release(plainData)
            }
        }

        // Create cipher data from string
        let cipherBytes = ciphertext.utf8CString
        let err1 = cipherBytes.withUnsafeBufferPointer { buffer in
            gpgme_data_new_from_mem(&cipherData, buffer.baseAddress, cipherBytes.count - 1, 1)
        }
        guard err1 == 0, cipherData != nil else {
            throw GPGMEError.dataCreationFailed("Failed to create cipher data: \(err1)")
        }

        // Create plain data buffer
        let err2 = gpgme_data_new(&plainData)
        guard err2 == 0, plainData != nil else {
            throw GPGMEError.dataCreationFailed("Failed to create plain data: \(err2)")
        }

        // Decrypt
        let decErr = gpgme_op_decrypt(ctx, cipherData!, plainData!)
        guard decErr == 0 else {
            if let errStr = gpgme_strerror(decErr) {
                throw GPGMEError.decryptionFailed(String(cString: errStr))
            }
            throw GPGMEError.decryptionFailed("Decryption failed: \(decErr)")
        }

        // Read decrypted data
        gpgme_data_seek(plainData!, 0, SEEK_SET)
        var buffer = [CChar](repeating: 0, count: 65536)
        var result = Data()

        while true {
            let bytesRead = gpgme_data_read(plainData!, &buffer, buffer.count)
            if bytesRead <= 0 { break }
            result.append(contentsOf: buffer.prefix(bytesRead))
        }

        guard let plaintext = String(data: result, encoding: .utf8) else {
            throw GPGMEError.encodingFailed("Failed to encode decrypted data")
        }

        return plaintext
    }
}

enum GPGMEError: Error, CustomStringConvertible {
    case initializationFailed(String)
    case contextNotInitialized
    case dataCreationFailed(String)
    case keyNotFound(String)
    case encryptionFailed(String)
    case decryptionFailed(String)
    case encodingFailed(String)

    var description: String {
        switch self {
        case .initializationFailed(let msg): return "GPGME initialization failed: \(msg)"
        case .contextNotInitialized: return "GPGME context not initialized"
        case .dataCreationFailed(let msg): return "Data creation failed: \(msg)"
        case .keyNotFound(let msg): return "Key not found: \(msg)"
        case .encryptionFailed(let msg): return "Encryption failed: \(msg)"
        case .decryptionFailed(let msg): return "Decryption failed: \(msg)"
        case .encodingFailed(let msg): return "Encoding failed: \(msg)"
        }
    }
}
