# CHAP-IEM-SKN Technical Document

## Secure Key Negotiation Extension for CHAP-IEM

> **NOTE: This protocol is NOT the legacy Challenge-Handshake Authentication Protocol (CHAP).** This is a completely different protocol family. CHAP-IEM-SKN is a security-enhanced variant of CHAP-IEM that introduces a pre-shared key mixing exchange mechanism.

---

## I. Overview

CHAP-IEM-SKN (Secure Key Negotiation) is a security-enhanced variant of the CHAP-IEM protocol. The core differences are:

| Comparison Dimension | Standard CHAP | CHAP-IEM | CHAP-IEM-SKN |
|---------------------|---------------|----------|---------------|
| Pre-shared Content | Password (low entropy) | Password (low entropy) | **Shared key (can be low entropy)** |
| Login Key Source | Password hash | Password hash | **Key exchange derived** |
| Offline Brute Force Risk | Yes | Yes | **None** |
| IEM Chain Feature | Not applicable | Yes | Yes |
| Key Exchange Messages | None | None | Plaintext (encryption optional) |

---

## II. Core Principle

### 2.1 Color Analogy

Both parties pre-share a secret value called Yellow. The client generates a private random number Red, and the server generates a private random number Blue. The client mixes Yellow with Red to obtain Orange and sends it to the server. The server mixes Yellow with Blue to obtain Green and sends it to the client.

After receiving Green, the client mixes it with its own Red to obtain Brown. After receiving Orange, the server mixes it with its own Blue to obtain the same Brown. This Brown is the negotiated base value, which is then hashed to become the session key.

Even if an attacker intercepts Orange and Green, without knowing Yellow, they cannot solve three unknowns from two equations and thus cannot compute Brown.

### 2.2 Mathematical Form

Let Y be the pre-shared key, a be the client's random number, and b be the server's random number.

The client computes A = Y ⊕ a and sends it. The server computes B = Y ⊕ b and sends it.

Upon receiving B, the client computes K_base = B ⊕ a = Y ⊕ a ⊕ b. Upon receiving A, the server computes K_base = A ⊕ b = Y ⊕ a ⊕ b.

Both parties obtain the same K_base, then compute the session key K_session = SHA256(K_base). Both parties then discard a, b, and K_base.

### 2.3 Security Properties

An attacker knowing only A and B cannot compute K_session without Y. This security does not rely on the discrete logarithm problem but on the attacker's lack of Y. Even with a quantum computer, the attacker cannot solve three unknowns from two equations.

---

## III. Complete Workflow

![CHAP-IEM-SKN Flowchart](./chap-iem-skn.png)

### 3.1 Pre-shared Phase

The client and server pre-share a secret key Y. Y can be a pre-installed symmetric key, a password hash, or any value known only to both parties. Y may have low entropy (e.g., a 4-6 digit PIN) because the attacker never sees any direct information about Y. If Y is compromised, the entire security system fails — this falls within the user's responsibility.

### 3.2 Key Exchange Phase

The client generates a cryptographically secure random number a, computes A = mix(Y, a), and sends A to the server. The server generates a cryptographically secure random number b, computes B = mix(Y, b), and sends B to the client.

Upon receiving each other's messages, both parties compute K_base = unmix(peer's message, own random number), obtaining the same Y ⊕ a ⊕ b. They then compute K_session = SHA256(K_base) and immediately discard a, b, and K_base.

**Whether A and B need encryption:**

A and B are transmitted in plaintext by default and do not require encryption. An attacker knowing only A and B cannot compute any meaningful information without Y. If higher security is required by engineering constraints, A and B can be encrypted (e.g., using AES with a key derived from Y). However, this requires additional key derivation steps and increases implementation complexity. Whether to encrypt depends on engineering implementation and security requirements. Plaintext transmission is sufficient for most scenarios.

**Choice of mixing function:**

XOR is the recommended default mixing function due to its reversibility, highest performance, and simplicity. HMAC-SHA256 can be used when one-way property is needed. AES256 can be used in hardware-accelerated environments. The specific choice depends on engineering practice requirements.

### 3.3 Login Phase

The client encrypts the username using AES256 with K_session and sends the login packet to the server.

The server decrypts with K_session and verifies the username validity. If decryption fails or the username is invalid, the server rejects the connection and disconnects.

Upon successful verification, the server generates a cryptographically secure random ID₁, packages the OK result with ID₁, encrypts with K_session, and returns it to the client.

The client decrypts to obtain ID₁ and sets the current encryption key to ID₁. K_session is retained solely for subsequent exception recovery. K_session may also be discarded, but this requires ensuring a recovery key is available when needed.

### 3.4 Normal IEM Operation Chain

The client encrypts the operation command using the current ID as the AES256 key and sends it to the server.

The server decrypts with the same ID, executes the operation, generates a new random ID, packages the operation result with the new ID, encrypts with the old ID, and returns it to the client.

The client decrypts with the old ID, obtains the operation result and the new ID, and updates the current encryption key to the new ID.

Each subsequent operation repeats this process, forming a key chain: ID₁ → ID₂ → ID₃ → ...

### 3.5 Exception Recovery Mechanism

When a response packet is lost, causing the client's key to become out of sync with the server, the client sends an operation packet using what it believes to be the current ID. The server successfully decrypts but finds that the ID is no longer valid (already destroyed).

The server encrypts a recovery packet containing the currently valid ID using K_session and sends it to the client. The client decrypts with K_session, obtains the valid ID, updates its local key, and sends a confirmation packet. Upon successful verification, the server returns a success response, and normal communication resumes.

Note: This recovery mechanism depends on K_session. If K_session has been discarded, the client must re-execute the complete key exchange and login process.

---

## IV. Engineering Practice Specifications

### 4.1 Parameter Specifications

| Parameter | Specification | Description |
|-----------|---------------|-------------|
| Y (pre-shared key) | Any length | Recommended ≥ 128 bits, can be low entropy |
| a, b (random numbers) | 256 bits | Must use CSPRNG |
| K_base | 256 bits | Result of Y ⊕ a ⊕ b |
| K_session | 256 bits | Output of SHA256(K_base) |
| IDₙ | 256 bits | Regenerated each operation, must be random |
| AES key | 256 bits | All AES operations use AES-256 |

### 4.2 Random Number Generation Requirements

The random numbers a and b in the key exchange phase must be generated using a cryptographically secure random number generator. ID₁ in the login phase and each new ID generated per operation must also be generated using a CSPRNG. If random numbers are predictable, the entire security system collapses. In CHAP-IEM-SKN, IDs serve as encryption keys — predictable IDs completely break the security model.

### 4.3 Mixing Function Selection

XOR is the recommended default mixing function, requiring Y and the random number to have equal length. If lengths differ, the shorter value should be extended via KDF, or the longer value should be truncated/hashed.

HMAC-SHA256 is suitable for scenarios requiring one-way property, where the mixing process is irreversible and both parties compute and compare results.

AES256 is suitable for hardware-accelerated environments, using Y as the key to encrypt the random number.

### 4.4 Encryption Mode Selection

AES-256-CBC with Encrypt-then-MAC (HMAC-SHA256) is recommended for general scenarios. IV can be random or counter-based. AES-256-GCM is an option for high-performance scenarios, but note that nonce reuse is catastrophic. For resource-constrained scenarios, AES-256-CBC alone may be used, relying on ZIM's ID chain for integrity verification, but implementations MUST return identical error responses for all failure cases.

### 4.5 State Management

The client must store Y long-term, and during a session store a (key exchange phase only), K_session (login and exception recovery), and current_id (current operation key). The server must store Y and the user database long-term, and during a session store b (key exchange phase only), K_session, current_id, and the associated user identity.

All random numbers (a, b, IDₙ) should be cleared from memory immediately when no longer needed. K_session may be discarded after exception recovery, but the cost of re-authentication should be evaluated.

---

## V. Security Analysis

### 5.1 Offline Brute Force Resistance

CHAP-IEM-SKN is inherently resistant to offline brute force attacks. The attacker intercepts A, B, and the login ciphertext. To verify a guessed Y', the attacker would need to derive a' and b' from A and B, compute K_session', and attempt to decrypt the ciphertext. However, the attacker has no method to verify whether Y' is correct, because decryption always produces some string (garbage or a valid username). Without a username database as an oracle, the attacker cannot determine correctness. This is the core distinction between CHAP-IEM-SKN and standard CHAP or CHAP-IEM.

### 5.2 Forward Secrecy

Each session independently generates new a and b. K_session is used only for the current session. Even if the pre-shared key Y is compromised at some future point, past K_session values cannot be derived, as derivation requires the a and b used at that time.

### 5.3 Man-in-the-Middle Attacks

CHAP-IEM-SKN does not require additional man-in-the-middle attack protection. The only prerequisite for a successful MitM attack is that the attacker knows Y. If the attacker does not know Y, they cannot generate valid A' or B' or impersonate either party. If the attacker knows Y, the pre-shared key has been compromised — this falls within the user's responsibility, not a problem the protocol itself needs to solve.

### 5.4 Confidentiality of Key Exchange Messages

A and B do not need encryption. An attacker knowing only A and B cannot compute Y, a, b, or K_session without Y. Security does not depend on the confidentiality of A and B, but on the confidentiality of Y. The only concern is integrity (tamper prevention), which can be addressed at low cost through retry mechanisms. If engineering requirements demand higher security, A and B can be encrypted, but this increases implementation complexity.

---

## VI. Applicable Scenarios

CHAP-IEM-SKN is particularly suitable for:

**Password-less Authentication Environments**: IoT devices with pre-shared keys, device pairing, etc., where no user password input is required.

**Scenarios Requiring Offline Brute Force Resistance**: The pre-shared key can be low entropy (e.g., a PIN), but attackers cannot perform offline enumeration verification.

**Communications Requiring Forward Secrecy**: Each session key is independent; historical messages remain protected even if future keys are compromised.

**Ephemeral Sessions**: Device first-time pairing, guest mode, and other scenarios without long-term pre-shared keys.

**Resource-Constrained Devices**: XOR mixing function has extremely low computational overhead, suitable for embedded environments.

---

## VII. Summary

The core innovation of CHAP-IEM-SKN is: using the pre-shared Yellow as the root, each party mixes in its own random value, and after exchange both parties obtain the same Yellow plus Red plus Blue. The attacker only knows the mixed Orange and Green; without Yellow, they can never derive the final Brown.

**Protocol Hierarchy:**

ZIM (Zigzag Interaction Model) → CHAP (fixed key + ID chain) → CHAP-IEM (ID as key) → CHAP-IEM-SKN (pre-shared key mixing exchange)

**Core Advantages:**

- No need for high-entropy pre-shared secrets; Y can be low entropy
- Inherently resistant to offline brute force; attackers cannot enumerate and verify
- Retains all IEM features: chained key management, forward secrecy, exception recovery
- Simple implementation: XOR + SHA256 + AES
- Key exchange messages can be transmitted in plaintext; no additional encryption layer required

- *Hiss, I always feel like SKN isn't as stable as the IEM variant, so if you really need to use it, just see how things go.*
