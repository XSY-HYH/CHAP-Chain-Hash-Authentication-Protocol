using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Collections.Concurrent;

namespace ZIM.Server
{
    public class ChapSession
    {
        public string SessionId { get; set; } = "";
        public string ClientId { get; set; } = "";
        public DateTime LastActivity { get; set; }
    }

    public class ChapRequest
    {
        public string? SessionId { get; set; }
        public string? Action { get; set; }
        public JsonElement? Data { get; set; }
    }

    public class ChapResponse
    {
        public bool Success { get; set; }
        public string Message { get; set; } = "";
        public string? NewId { get; set; }
        public object? Data { get; set; }
    }

    public class ChapHandler
    {
        private readonly byte[] _masterKey;
        private readonly ConcurrentDictionary<string, ChapSession> _sessions = new();
        private readonly RandomNumberGenerator _rng = RandomNumberGenerator.Create();

        public ChapHandler(string adminPassword)
        {
            using var sha256 = SHA256.Create();
            _masterKey = sha256.ComputeHash(Encoding.UTF8.GetBytes(adminPassword));
        }

        private byte[] Encrypt(byte[] key, string plaintext)
        {
            using var aes = Aes.Create();
            aes.Key = key;
            aes.Mode = CipherMode.CBC;
            aes.Padding = PaddingMode.PKCS7;
            aes.GenerateIV();

            using var encryptor = aes.CreateEncryptor();
            var plainBytes = Encoding.UTF8.GetBytes(plaintext);
            var cipherBytes = encryptor.TransformFinalBlock(plainBytes, 0, plainBytes.Length);

            var result = new byte[aes.IV.Length + cipherBytes.Length];
            Buffer.BlockCopy(aes.IV, 0, result, 0, aes.IV.Length);
            Buffer.BlockCopy(cipherBytes, 0, result, aes.IV.Length, cipherBytes.Length);
            return result;
        }

        private string? Decrypt(byte[] key, byte[] ciphertextWithIv)
        {
            try
            {
                using var aes = Aes.Create();
                aes.Key = key;
                aes.Mode = CipherMode.CBC;
                aes.Padding = PaddingMode.PKCS7;

                var iv = new byte[16];
                Buffer.BlockCopy(ciphertextWithIv, 0, iv, 0, 16);
                aes.IV = iv;

                var ciphertext = new byte[ciphertextWithIv.Length - 16];
                Buffer.BlockCopy(ciphertextWithIv, 16, ciphertext, 0, ciphertext.Length);

                using var decryptor = aes.CreateDecryptor();
                var plainBytes = decryptor.TransformFinalBlock(ciphertext, 0, ciphertext.Length);
                return Encoding.UTF8.GetString(plainBytes);
            }
            catch
            {
                return null;
            }
        }

        private string GenerateSessionId()
        {
            var bytes = new byte[32];
            _rng.GetBytes(bytes);
            return Convert.ToHexString(bytes);
        }

        private ChapResponse ErrorResponse(string message, string? newId = null)
        {
            return new ChapResponse { Success = false, Message = message, NewId = newId };
        }

        private ChapResponse SuccessResponse(string message, string? newId = null, object? data = null)
        {
            return new ChapResponse { Success = true, Message = message, NewId = newId, Data = data };
        }

        public byte[] HandleLogin(byte[] encryptedData, string clientId)
        {
            var decrypted = Decrypt(_masterKey, encryptedData);
            if (decrypted == null)
            {
                var response = ErrorResponse("authentication_failed");
                return Encrypt(_masterKey, JsonSerializer.Serialize(response));
            }

            var username = decrypted.Trim();
            if (username != "admin")
            {
                var response = ErrorResponse("authentication_failed");
                return Encrypt(_masterKey, JsonSerializer.Serialize(response));
            }

            var sessionId = GenerateSessionId();
            _sessions[sessionId] = new ChapSession
            {
                SessionId = sessionId,
                ClientId = clientId,
                LastActivity = DateTime.UtcNow
            };

            var successResponse = SuccessResponse("login_success", sessionId);
            return Encrypt(_masterKey, JsonSerializer.Serialize(successResponse));
        }

        public byte[] HandleOperation(byte[] encryptedData, string clientId)
        {
            var decrypted = Decrypt(_masterKey, encryptedData);
            if (decrypted == null)
            {
                var response = ErrorResponse("decryption_failed");
                return Encrypt(_masterKey, JsonSerializer.Serialize(response));
            }

            ChapRequest? request;
            try
            {
                request = JsonSerializer.Deserialize<ChapRequest>(decrypted);
            }
            catch
            {
                var response = ErrorResponse("invalid_request");
                return Encrypt(_masterKey, JsonSerializer.Serialize(response));
            }

            if (string.IsNullOrEmpty(request?.SessionId))
            {
                var response = ErrorResponse("missing_session_id");
                return Encrypt(_masterKey, JsonSerializer.Serialize(response));
            }

            if (!_sessions.TryGetValue(request.SessionId, out var session))
            {
                var currentValidId = _sessions.Keys.FirstOrDefault();
                var response = ErrorResponse("session_expired", currentValidId);
                return Encrypt(_masterKey, JsonSerializer.Serialize(response));
            }

            if (session.ClientId != clientId)
            {
                var response = ErrorResponse("client_mismatch");
                return Encrypt(_masterKey, JsonSerializer.Serialize(response));
            }

            _sessions.TryRemove(request.SessionId, out _);

            var newSessionId = GenerateSessionId();
            _sessions[newSessionId] = new ChapSession
            {
                SessionId = newSessionId,
                ClientId = clientId,
                LastActivity = DateTime.UtcNow
            };

            object? operationResult = null;
            if (request.Action != null)
            {
                operationResult = new { action = request.Action, processed = true, timestamp = DateTime.UtcNow };
            }

            var response = SuccessResponse("operation_success", newSessionId, operationResult);
            return Encrypt(_masterKey, JsonSerializer.Serialize(response));
        }

        public bool ValidateSession(string sessionId, string clientId)
        {
            if (!_sessions.TryGetValue(sessionId, out var session))
                return false;
            
            if (session.ClientId != clientId)
                return false;
            
            if (DateTime.UtcNow - session.LastActivity > TimeSpan.FromHours(1))
            {
                _sessions.TryRemove(sessionId, out _);
                return false;
            }
            
            session.LastActivity = DateTime.UtcNow;
            return true;
        }

        public void CleanupExpiredSessions()
        {
            var expired = _sessions
                .Where(s => DateTime.UtcNow - s.Value.LastActivity > TimeSpan.FromHours(1))
                .Select(s => s.Key)
                .ToList();
            
            foreach (var id in expired)
                _sessions.TryRemove(id, out _);
        }
    }
}
