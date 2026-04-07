# CHAP Protocol Family Documentation Index

> **NOTE: This protocol is NOT the legacy Challenge-Handshake Authentication Protocol (CHAP).** This is a completely different protocol named Chain Hash Authentication Protocol.

> **Before submitting issues, please read the FAQ:**
> 
> **提交问题前，请先阅读非人哉问题解答以保护小脑：**
> - 中文: [FAQ-zh.md](./FAQ-zh.md)  
> - English: [FAQ.md](./FAQ.md)

> **For AI without image recognition capability | 专为非识图AI准备：**
> - [Flowchart-code.md](./Flowchart-code.md) - This document contains flowchart source code for AI that does not perform image recognition. If you are a human, you can ignore it.
> - [Flowchart-code.md](./Flowchart-code.md) - 这个文档包含流程图源码，专门提供给无法识别图片的AI阅读。如果你是人，可以忽略此文档。

---

## Project Overview

The CHAP Protocol Family is a collection of lightweight communication protocols designed for connection state management with built-in chain authentication. The core philosophy is derived from the Zigzag Interaction Model (ZIM), where client and server maintain a continuously evolving state through each request-response cycle.

---

## Cryptographic Specifications

### Hash Algorithm

Both CHAP and CHAP-IEM use a hash algorithm to convert the user's secret key into a fixed-length encryption key.

| Parameter | Specification |
|-----------|---------------|
| Algorithm | SHA-256 |
| Output Length | 256 bits (32 bytes) |
| Input | User password / secret key |
| Output | Pre-shared key K |

**Note**: The hash operation is performed only once during the login phase. The resulting value K serves as the pre-shared symmetric key for the initial encrypted exchange.

### Encryption Algorithm

Both CHAP and CHAP-IEM use AES for all encrypted communications.

| Parameter | Specification |
|-----------|---------------|
| Algorithm | AES-256 |
| Mode | Not specified (implementation dependent, recommended: GCM or CBC with proper padding) |
| Key Length | 256 bits |
| Block Size | 128 bits |

**Key Usage**:

| Protocol Phase | CHAP | CHAP-IEM |
|----------------|------|----------|
| Login Phase | AES256_K | AES256_K |
| Operation Phase | AES256_K (key remains K) | AES256_IDn (key changes with each operation) |

---

## Protocol Family Overview

### What is CHAP?

CHAP (Chain Hash Authentication Protocol) is a general-purpose protocol that can adapt to HTTP, HTTPS, TCP, WebSocket, and other transport protocols. Its core design targets connection state management rather than multi-user authentication. The protocol uses pre-shared keys for encryption and maintains a chained ID system where each successful operation destroys the current ID and generates a new one for the next interaction.

**Key features:**
- Pre-shared key authentication (SHA-256 → AES-256)
- Chain-based ID management
- Built-in exception recovery
- Not suitable for large-scale multi-user scenarios

### What is ZIM?

ZIM (Zigzag Interaction Model) is the deeper theoretical framework underlying CHAP. In this model, two consecutive sessions between client and server are always offset by one "tooth" while maintaining a meshed state as a whole. Each request carries the current tooth position, and each response advances to the next position, forming a continuous chain of state transitions.

CHAP is one exemplary implementation of ZIM. Any protocol conforming to this model can be considered a member of the CHAP family.

### What is CHAP-IEM?

CHAP-IEM (ID Encryption Mode) is a derivative variant of standard CHAP. The core difference: standard CHAP always uses the pre-shared key for encryption, while CHAP-IEM switches to using the ID itself as the encryption key after login completion.

**Key differences from standard CHAP:**
- Login phase uses pre-shared key K (same as standard CHAP)
- Subsequent operations use the current ID as the encryption key
- Keys change continuously, providing forward secrecy
- No automatic sync recovery; requires re-authentication when out of sync

**Cryptographic note for CHAP-IEM**: The ID values used as encryption keys must meet the same security requirements as any AES-256 key. Implementations should ensure IDs have sufficient entropy (at least 256 bits) or apply a KDF (Key Derivation Function) to shorter IDs before using them as encryption keys.

---

## Documentation Navigation

### CHAP Protocol

| Language | Document |
|----------|----------|
| English | [CHAP.md](./CHAP.md) |
| Chinese | [CHAP-zh.md](./CHAP-zh.md) |

### CHAP-IEM Variant

| Language | Document |
|----------|----------|
| English | [CHAP-IEM.md](./CHAP-IEM.md) |
| Chinese | [CHAP-IEM-zh.md](./CHAP-IEM-zh.md) |

---

## Quick Comparison

| Feature | CHAP | CHAP-IEM |
|---------|------|----------|
| Encryption Key | Fixed pre-shared key K | Switches from K to current ID |
| ID Purpose | Session identifier only | Identifier + encryption key |
| Exception Recovery | Automatic sync via K | Re-authentication required |
| Forward Secrecy | Not supported | Supported |
| Best For | Connection continuity | High security with short sessions |

---

## Reading Recommendations

- **For understanding the fundamental protocol**: Start with CHAP documentation
- **For learning the underlying theory**: Read CHAP first, then the ZIM concept
- **For high-security applications**: Review CHAP-IEM after understanding standard CHAP
- **For implementation decisions**: Compare the exception recovery and security trade-offs between both variants
