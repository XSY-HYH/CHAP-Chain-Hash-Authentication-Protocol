# CHAP-IEM Technical Document

## I. Overview

CHAP-IEM (ID Encryption Mode) is a derivative variant of the standard CHAP protocol. The core difference between the two is that standard CHAP always uses a pre-shared key (user password hash) for encryption, while CHAP-IEM switches to a chained mode where the ID itself serves as the encryption key after login completion.

## II. Core Differences from Standard CHAP

| Comparison Dimension | Standard CHAP | CHAP-IEM |
|---------------------|---------------|----------|
| Encryption Key | Always uses pre-shared key K | Uses K during login phase, then switches to current ID |
| Purpose of ID | Session identifier only | Both session identifier and encryption key |
| Key Update | Key K remains fixed | Key changes chained with ID |
| Exception Recovery | Server pushes current ID for sync using K | Requires re-authentication to rebuild key chain |

## III. CHAP-IEM Workflow Details

### 3.1 Login Phase (Same as Standard CHAP)

The client inputs a username and a secret key, then converts the key into a hash value as the pre-shared key K. The client encrypts the username using AES with K and sends it to the server.

The server decrypts using the pre-configured key K and verifies the username validity. Upon successful verification, the server generates ID_1, packages the OK result along with ID_1, encrypts them with K, and returns the packet to the client.

The client decrypts with K and obtains ID_1. At this point, the client holds both K and ID_1, but K will not be used in subsequent operations.

### 3.2 Normal Operation Workflow

**First Operation**

The client uses ID_1 as the encryption key, encrypts the operation command with AES, and sends it to the server.

The server decrypts using ID_1 (since ID_1 was generated and issued by the server in the previous step), executes the operation upon successful decryption, and simultaneously generates a new ID_2. The server encrypts the operation result along with ID_2 using ID_1 (the old ID) and returns the packet to the client.

The client decrypts with ID_1, obtains the operation result and ID_2, then updates its current encryption key to ID_2.

**Second Operation**

The client encrypts the operation command using ID_2. The server decrypts with ID_2, executes the operation, generates ID_3, and returns the result encrypted with ID_2. The client updates its key to ID_3.

And so on, forming a key chain: Login with K → ID_1 → ID_2 → ID_3 → ...

### 3.3 Key Design Points

In each response packet, the server uses the **old ID** to encrypt the new ID when returning it to the client. This means:

- Only the client holding the current valid ID can decrypt and obtain the next ID
- The server does not need to additionally store the encryption key for the new ID; the old ID is naturally the best carrier for encrypting the new ID
- The encryption key updates naturally with each operation, requiring no additional negotiation

### 3.4 Exception Recovery Mechanism

When a response packet is lost, the client's local key remains ID_3, but the server's current valid key has been updated to ID_4.

The client encrypts a new operation using ID_3 and sends it. The server successfully decrypts using ID_3 (since ID_3 was indeed the last issued ID), but finds that ID_3 is no longer valid — the server expects to receive a confirmation or subsequent operation encrypted with ID_3, but the operation window corresponding to ID_3 has already closed, and the server has moved to ID_4 state.

Because the server no longer holds ID_3 as a valid key (ID_3 has been destroyed), it cannot encrypt any return information using ID_3. The server can only return a special instruction requiring the client to restart the complete login process.

The client re-authenticates, obtains a new K and a new ID_1', and restarts the key chain.

**Comparison with Standard CHAP**: In standard CHAP, the server always holds the fixed key K, so it can encrypt and push the current valid ID to the client to complete synchronization without requiring re-authentication. In CHAP-IEM, the key changes with each ID, and the server cannot encrypt information using a destroyed old key, forcing re-authentication.

## IV. Security Analysis

### 4.1 Attacker Perspective

**Eavesdropping Attack**: The attacker intercepts any ciphertext packet. Since the encryption key changes after each operation and the key derivation path is irreversible (knowing ID_2 does not allow backward derivation of ID_1), the attacker cannot obtain useful information from a single packet.

**Replay Attack**: The attacker replays an old encrypted packet. The server's current valid key has been updated, so decrypting the old packet with the new key will inevitably fail, rendering the replay attack ineffective.

**Forgery Attack**: The attacker sends any forged ciphertext. The server decryption fails and rejects it directly.

### 4.2 Security Comparison with Standard CHAP

| Security Feature | Standard CHAP | CHAP-IEM |
|------------------|---------------|----------|
| Key Fixity | K remains fixed over long term | Keys change continuously |
| Impact of Single Packet Compromise | Can decrypt all subsequent communications | Affects only the current single packet |
| Forward Secrecy | Not supported (K leak compromises everything) | Supported (old keys cannot derive new keys) |
| Sync Mechanism Security | Server can actively push sync | No active sync capability |

### 4.3 Limitations

When keys become out of sync, re-authentication is mandatory, causing state interruption. If the pre-shared key K from the login phase is compromised, an attacker can complete initial authentication and obtain ID_1, but since K is only used for login, subsequent communications remain protected by the ID chain.

## V. Applicable Scenarios

CHAP-IEM is suitable for the following scenarios:

1. Communication environments with forward secrecy requirements
2. Applications with short single-session lifetimes
3. Systems that can tolerate re-authentication overhead
4. High-security scenarios requiring reduced long-term key exposure risk

Unsuitable scenarios:

1. Environments with poor network quality and high packet loss rates (frequent re-authentication)
2. Services requiring long-term maintenance of a single session
3. Critical systems that cannot tolerate connection interruption

## VI. Summary

CHAP-IEM introduces the design concept of "ID as key" based on the standard CHAP login workflow. The login phase still uses the pre-shared key K for identity authentication and ID_1 distribution, after which it switches to a chained encryption mode using IDs as keys. This design sacrifices automatic exception recovery capability in exchange for forward secrecy through automatic key updates after each operation. The choice between standard CHAP and CHAP-IEM is essentially a trade-off between connection continuity and forward secrecy.
