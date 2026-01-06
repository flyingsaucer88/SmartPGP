// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "SmartPGP.OutlookHelper",
    platforms: [
        .macOS(.v12)
    ],
    dependencies: [
        // Vapor for HTTP server
        .package(url: "https://github.com/vapor/vapor.git", from: "4.89.0"),
        .package(url: "https://github.com/apple/swift-nio-ssl.git", from: "2.0.0"),
    ],
    targets: [
        .executableTarget(
            name: "SmartPGP.OutlookHelper",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .product(name: "NIOSSL", package: "swift-nio-ssl"),
            ],
            path: "Sources",
            swiftSettings: [
                .unsafeFlags(["-I", "/opt/homebrew/include", "-I", "/usr/local/include"]),
            ],
            linkerSettings: [
                .linkedLibrary("gpgme"),
                .linkedLibrary("gpg-error"),
                .unsafeFlags(["-L", "/opt/homebrew/lib", "-L", "/usr/local/lib"]),
            ]
        ),
    ]
)
