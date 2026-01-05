// main.swift
// SmartPGP Outlook Helper for macOS
// HTTPS localhost server for PGP operations with SmartPGP card

import Vapor
import Foundation

// MARK: - Configuration

struct SmartPGPConfig {
    let port: Int
    let allowedOrigin: String
    let certificatePath: String?
    let certificatePassword: String?
    let signerId: String?

    static func load() -> SmartPGPConfig {
        return SmartPGPConfig(
            port: Int(ProcessInfo.processInfo.environment["SMARTPGP_PORT"] ?? "5555") ?? 5555,
            allowedOrigin: ProcessInfo.processInfo.environment["SMARTPGP_ALLOWED_ORIGIN"] ?? "https://localhost",
            certificatePath: ProcessInfo.processInfo.environment["SMARTPGP_CERT_PATH"],
            certificatePassword: ProcessInfo.processInfo.environment["SMARTPGP_CERT_PASSWORD"],
            signerId: ProcessInfo.processInfo.environment["SMARTPGP_SIGNER_ID"]
        )
    }
}

// MARK: - Request/Response Models

struct EncryptRequest: Content {
    let body: String
    let recipients: [String]
}

struct EncryptResponse: Content {
    let armored: String
}

struct DecryptRequest: Content {
    let body: String
}

struct DecryptResponse: Content {
    let plaintext: String
}

struct GenerateKeypairRequest: Content {
    let keySize: Int?
    let adminPin: String?
}

struct ChangePinRequest: Content {
    let currentPin: String
    let newPin: String
}

struct DeleteKeypairRequest: Content {
    let adminPin: String?
}

struct ErrorResponse: Content {
    let error: String
}

// MARK: - Application Setup

@main
struct SmartPGPApp {
    static func main() async throws {
        let config = SmartPGPConfig.load()

        var env = try Environment.detect()
        try LoggingSystem.bootstrap(from: &env)

        let app = Application(env)
        defer { app.shutdown() }

        // Configure server
        app.http.server.configuration.hostname = "127.0.0.1"
        app.http.server.configuration.port = config.port

        // Configure TLS if certificate is provided
        if let certPath = config.certificatePath,
           let certPassword = config.certificatePassword {
            // Note: Vapor TLS configuration would go here
            // For now, we'll use HTTP and rely on external TLS termination
            print("Note: TLS certificate specified but not yet implemented in Swift version")
        }

        // Initialize services
        let gpgmeContext = try GPGMEContext()
        let cardService = CardService()

        // CORS middleware
        let cors Configuration = CORSMiddleware.Configuration(
            allowedOrigin: .custom(config.allowedOrigin),
            allowedMethods: [.GET, .POST, .OPTIONS],
            allowedHeaders: [.accept, .authorization, .contentType, .origin]
        )
        app.middleware.use(CORSMiddleware(configuration: corsConfiguration))

        // Error middleware
        app.middleware.use(ErrorMiddleware.default(environment: env))

        // MARK: - Routes

        // Health check
        app.get("healthz") { req -> String in
            return "ok"
        }

        // POST /encrypt - Encrypt plaintext for recipients
        app.post("encrypt") { req -> Response in
            do {
                let encryptRequest = try req.content.decode(EncryptRequest.self)

                guard !encryptRequest.body.isEmpty else {
                    throw Abort(.badRequest, reason: "Missing 'body' in request")
                }

                guard !encryptRequest.recipients.isEmpty else {
                    throw Abort(.badRequest, reason: "At least one recipient is required")
                }

                let armored = try gpgmeContext.encrypt(
                    encryptRequest.body,
                    recipients: encryptRequest.recipients,
                    signerId: config.signerId
                )

                let response = EncryptResponse(armored: armored)
                return try await response.encodeResponse(for: req)

            } catch let error as GPGMEError {
                let errorResponse = ErrorResponse(error: error.description)
                throw Abort(.internalServerError, reason: error.description)
            } catch {
                throw error
            }
        }

        // POST /decrypt - Decrypt PGP message
        app.post("decrypt") { req -> Response in
            do {
                let decryptRequest = try req.content.decode(DecryptRequest.self)

                guard !decryptRequest.body.isEmpty else {
                    throw Abort(.badRequest, reason: "Missing 'body' in request")
                }

                let plaintext = try gpgmeContext.decrypt(decryptRequest.body)

                let response = DecryptResponse(plaintext: plaintext)
                return try await response.encodeResponse(for: req)

            } catch let error as GPGMEError {
                throw Abort(.internalServerError, reason: error.description)
            } catch {
                throw error
            }
        }

        // POST /generate-keypair - Generate new keypair on card
        app.post("generate-keypair") { req -> Response in
            do {
                let genRequest = try req.content.decode(GenerateKeypairRequest.self)

                let keySize = genRequest.keySize ?? 2048
                let adminPin = genRequest.adminPin ?? "12345678"

                let result = try cardService.generateKeypair(keySize: keySize, adminPin: adminPin)
                return try await result.encodeResponse(for: req)

            } catch let error as CardError {
                throw Abort(.internalServerError, reason: error.description)
            } catch {
                throw error
            }
        }

        // POST /change-pin - Change card PIN
        app.post("change-pin") { req -> Response in
            do {
                let pinRequest = try req.content.decode(ChangePinRequest.self)

                guard !pinRequest.currentPin.isEmpty && !pinRequest.newPin.isEmpty else {
                    throw Abort(.badRequest, reason: "Current PIN and new PIN are required")
                }

                let result = try cardService.changePin(
                    currentPin: pinRequest.currentPin,
                    newPin: pinRequest.newPin
                )
                return try await result.encodeResponse(for: req)

            } catch let error as CardError {
                throw Abort(.internalServerError, reason: error.description)
            } catch {
                throw error
            }
        }

        // POST /delete-keypair - Delete all keys (factory reset)
        app.post("delete-keypair") { req -> Response in
            do {
                let deleteRequest = try req.content.decode(DeleteKeypairRequest.self)

                let adminPin = deleteRequest.adminPin ?? "12345678"

                let result = try cardService.deleteKeypair(adminPin: adminPin)
                return try await result.encodeResponse(for: req)

            } catch let error as CardError {
                throw Abort(.internalServerError, reason: error.description)
            } catch {
                throw error
            }
        }

        // GET /card-status - Get card status information
        app.get("card-status") { req -> Response in
            do {
                let status = try cardService.getCardStatus()
                return try await status.encodeResponse(for: req)

            } catch let error as CardError {
                throw Abort(.internalServerError, reason: error.description)
            } catch {
                throw error
            }
        }

        // Start server
        print("SmartPGP Outlook Helper for macOS")
        print("Listening on https://127.0.0.1:\(config.port)")
        print("Allowed origin: \(config.allowedOrigin)")
        if let signerId = config.signerId {
            print("Signer ID: \(signerId)")
        }
        print("")
        print("Available endpoints:")
        print("  POST /encrypt       - Encrypt plaintext for recipients")
        print("  POST /decrypt       - Decrypt PGP message")
        print("  POST /generate-keypair - Generate new keypair on card")
        print("  POST /change-pin    - Change card PIN")
        print("  POST /delete-keypair - Delete all keys (factory reset)")
        print("  GET  /card-status   - Get card status")
        print("  GET  /healthz       - Health check")
        print("")

        try app.run()
    }
}
