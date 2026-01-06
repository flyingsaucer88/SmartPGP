using System.Text.Json;
using Microsoft.AspNetCore.Http.Json;
using Gpgme;
using System.Text;
using SmartPGP.OutlookHelper;

var builder = WebApplication.CreateBuilder(args);

// Configure isolated GNUPG home with zero cache TTL to avoid persisting secrets
var gnupgHome = Path.Combine(Path.GetTempPath(), $"smartpgp-gnupg-{Guid.NewGuid():N}");
Directory.CreateDirectory(gnupgHome);
var agentConfPath = Path.Combine(gnupgHome, "gpg-agent.conf");
File.WriteAllText(agentConfPath, "default-cache-ttl 0\nmax-cache-ttl 0\nallow-loopback-pinentry\n");
Environment.SetEnvironmentVariable("GNUPGHOME", gnupgHome);

// Configurable options with sensible defaults for local dev
var allowedOrigins = builder.Configuration.GetSection("SmartPgp:AllowedOrigins").Get<string[]>() ??
                    new[] { "https://localhost", "https://outlook.office.com", "https://outlook.live.com" };
var listenPort = builder.Configuration.GetValue("SmartPgp:Port", 5555);
var certPath = builder.Configuration.GetValue<string>("SmartPgp:CertificatePath"); // e.g., certs/localhost.pfx
var certPassword = builder.Configuration.GetValue<string>("SmartPgp:CertificatePassword");
var signerId = builder.Configuration.GetValue<string>("SmartPgp:SignerId"); // optional fingerprint/email for signing

builder.Services.Configure<JsonOptions>(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
});

builder.Services.AddCors(options =>
{
    options.AddPolicy("Default", policy =>
    {
        policy.WithOrigins(allowedOrigins)
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

builder.Services.AddSingleton<PgpService>();
builder.Services.AddSingleton<CardService>();

builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenLocalhost(listenPort, listenOptions =>
    {
        // TODO: point to a trusted localhost certificate and password
        if (!string.IsNullOrWhiteSpace(certPath))
        {
            listenOptions.UseHttps(certPath, certPassword);
        }
        else
        {
            // Dev fallback: uses ASP.NET Core developer certificate
            listenOptions.UseHttps();
        }
    });
});

builder.Services.AddSingleton(sp =>
{
    var logger = sp.GetRequiredService<ILogger<PgpService>>();
    var config = sp.GetRequiredService<IConfiguration>();
    return new PgpService(logger, config);
});

var app = builder.Build();

// Cleanup temp GNUPGHOME on shutdown
app.Lifetime.ApplicationStopping.Register(() =>
{
    try
    {
        Directory.Delete(gnupgHome, true);
    }
    catch
    {
        // best-effort; ignore
    }
});

app.UseCors("Default");

app.MapPost("/encrypt", async Task<IResult> (EncryptRequest? req, PgpService pgp) =>
{
    if (req is null || string.IsNullOrWhiteSpace(req.Body))
    {
        return Results.BadRequest("Missing 'body' in request.");
    }

    var recipients = req.Recipients ?? Array.Empty<string>();
    var result = await pgp.Encrypt(req.Body, recipients);

    return result.IsSuccess
        ? Results.Json(new { armored = result.Value })
        : Results.Problem(result.ErrorMessage, statusCode: 500);
});

app.MapPost("/decrypt", async Task<IResult> (DecryptRequest? req, PgpService pgp) =>
{
    if (req is null || string.IsNullOrWhiteSpace(req.Body))
    {
        return Results.BadRequest("Missing 'body' in request.");
    }

    var result = await pgp.Decrypt(req.Body);

    return result.IsSuccess
        ? Results.Json(new { plaintext = result.Value })
        : Results.Problem(result.ErrorMessage, statusCode: 500);
});

app.MapGet("/healthz", () => Results.Ok("ok"));

// POST /generate-keypair - Generate new keypair on card
app.MapPost("/generate-keypair", async (GenerateKeypairRequest? req, CardService cardService) =>
{
    try
    {
        var keySize = req?.KeySize ?? 2048;
        var adminPin = req?.AdminPin ?? "12345678";

        var result = await cardService.GenerateKeypair(keySize, adminPin);
        return Results.Json(result);
    }
    catch (CardException ex)
    {
        return Results.Problem(ex.Message, statusCode: 500);
    }
    catch (Exception ex)
    {
        return Results.Problem($"Unexpected error: {ex.Message}", statusCode: 500);
    }
});

// POST /change-pin - Change card PIN
app.MapPost("/change-pin", async (ChangePinRequest? req, CardService cardService) =>
{
    if (req is null || string.IsNullOrWhiteSpace(req.CurrentPin) || string.IsNullOrWhiteSpace(req.NewPin))
    {
        return Results.BadRequest("Current PIN and new PIN are required");
    }

    try
    {
        var result = await cardService.ChangePin(req.CurrentPin, req.NewPin);
        return Results.Json(result);
    }
    catch (CardException ex)
    {
        return Results.Problem(ex.Message, statusCode: 500);
    }
    catch (Exception ex)
    {
        return Results.Problem($"Unexpected error: {ex.Message}", statusCode: 500);
    }
});

// POST /delete-keypair - Delete all keys (factory reset)
app.MapPost("/delete-keypair", async (DeleteKeypairRequest? req, CardService cardService) =>
{
    try
    {
        var adminPin = req?.AdminPin ?? "12345678";
        var result = await cardService.DeleteKeypair(adminPin);
        return Results.Json(result);
    }
    catch (CardException ex)
    {
        return Results.Problem(ex.Message, statusCode: 500);
    }
    catch (Exception ex)
    {
        return Results.Problem($"Unexpected error: {ex.Message}", statusCode: 500);
    }
});

// GET /card-status - Get card status information
app.MapGet("/card-status", async (CardService cardService) =>
{
    try
    {
        var status = await cardService.GetCardStatus();
        return Results.Json(status);
    }
    catch (CardException ex)
    {
        return Results.Problem(ex.Message, statusCode: 500);
    }
    catch (Exception ex)
    {
        return Results.Problem($"Unexpected error: {ex.Message}", statusCode: 500);
    }
});

app.Run();

public record EncryptRequest(string Body, string[]? Recipients);
public record DecryptRequest(string Body);
public record GenerateKeypairRequest(int? KeySize, string? AdminPin);
public record ChangePinRequest(string CurrentPin, string NewPin);
public record DeleteKeypairRequest(string? AdminPin);

public record OperationResult<T>(bool IsSuccess, T? Value, string? ErrorMessage)
{
    public static OperationResult<T> Success(T value) => new(true, value, null);
    public static OperationResult<T> Fail(string error) => new(false, default, error);
}

public class PgpService
{
    private readonly ILogger<PgpService> _logger;
    private readonly string? _signerId;
    private readonly Context _ctx;

    public PgpService(ILogger<PgpService> logger, IConfiguration config)
    {
        _logger = logger;
        _signerId = config.GetValue<string>("SmartPgp:SignerId");

        // Initialize GPGME context for OpenPGP with armor enabled
        _ctx = new Context
        {
            Armor = true
        };
        _ctx.SetEngineInfo(Protocol.OpenPgp, null, null);
    }

    public Task<OperationResult<string>> Encrypt(string plaintext, IEnumerable<string> recipients)
    {
        try
        {
            var recipientList = recipients?.Where(r => !string.IsNullOrWhiteSpace(r)).ToArray() ?? Array.Empty<string>();
            if (recipientList.Length == 0)
            {
                return Task.FromResult(OperationResult<string>.Fail("At least one recipient is required."));
            }

            var keys = new List<Key>();
            foreach (var recipient in recipientList)
            {
                var key = _ctx.GetKey(recipient, false);
                if (key == null)
                {
                    return Task.FromResult(OperationResult<string>.Fail($"Recipient key not found: {recipient}"));
                }
                keys.Add(key);
            }

            _ctx.Signers.Clear();
            if (!string.IsNullOrWhiteSpace(_signerId))
            {
                var signer = _ctx.GetKey(_signerId, true);
                if (signer == null)
                {
                    return Task.FromResult(OperationResult<string>.Fail($"Signer key not found: {_signerId}"));
                }
                _ctx.Signers.Add(signer);
            }

            using var plain = new MemoryData(Encoding.UTF8.GetBytes(plaintext));
            using var cipher = new MemoryData();

            _ctx.EncryptAndSign(keys.ToArray(), EncryptFlags.AlwaysTrust, plain, cipher);

            var armored = Encoding.UTF8.GetString(cipher.ToArray());
            return Task.FromResult(OperationResult<string>.Success(armored));
        }
        catch (GpgmeException ex)
        {
            _logger.LogError(ex, "GPGME encryption error: {Message}", ex.Message);
            return Task.FromResult(OperationResult<string>.Fail($"GPGME encryption error: {ex.Message}"));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected encryption error");
            return Task.FromResult(OperationResult<string>.Fail("Unexpected encryption error."));
        }
    }

    public Task<OperationResult<string>> Decrypt(string ciphertext)
    {
        try
        {
            using var cipher = new MemoryData(Encoding.UTF8.GetBytes(ciphertext));
            using var plain = new MemoryData();

            _ctx.Decrypt(cipher, plain);

            var plaintext = Encoding.UTF8.GetString(plain.ToArray());
            return Task.FromResult(OperationResult<string>.Success(plaintext));
        }
        catch (GpgmeException ex)
        {
            _logger.LogError(ex, "GPGME decryption error: {Message}", ex.Message);
            return Task.FromResult(OperationResult<string>.Fail($"GPGME decryption error: {ex.Message}"));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected decryption error");
            return Task.FromResult(OperationResult<string>.Fail("Unexpected decryption error."));
        }
    }

    public void Dispose()
    {
        _ctx.Dispose();
    }
}
