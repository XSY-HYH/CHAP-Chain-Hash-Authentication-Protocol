# CHAP Protocol Family Documentation Index

> **NOTE: This protocol is NOT the legacy Challenge-Handshake Authentication Protocol (CHAP).** This is a completely different protocol named Chain Hash Authentication Protocol.

---

## Project Overview

The CHAP Protocol Family is a collection of lightweight communication protocols designed for connection state management with built-in chain authentication. The core philosophy is derived from the Zigzag Interaction Model (ZIM), where client and server maintain a continuously evolving state through each request-response cycle.

### What is CHAP?

CHAP (Chain Hash Authentication Protocol) is a general-purpose protocol that can adapt to HTTP, HTTPS, TCP, WebSocket, and other transport protocols. Its core design targets connection state management rather than multi-user authentication. The protocol uses pre-shared keys for encryption and maintains a chained ID system where each successful operation destroys the current ID and generates a new one for the next interaction.

**Key features:**
- Pre-shared key authentication
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
