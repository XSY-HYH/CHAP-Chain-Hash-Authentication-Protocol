# CHAP Protocol and Zigzag Interaction Model (ZIM)

## I. Protocol Positioning

CHAP (Chain Hash Authentication Protocol) is a general-purpose protocol that can theoretically adapt to various transport protocols including HTTP, HTTPS, TCP, and WebSocket.

The core design goal of CHAP is connection state management, not multi-user authentication. An increase in the number of users directly raises the server-side decryption cost, making this protocol unsuitable for large-scale multi-user scenarios.

CHAP is extensible. The original version is indeed not suitable for multiple users, but its derived variants (such as CHAP-IEM, i.e., ID Encryption Mode) can theoretically adapt to a wider range of use cases.

## II. Core Workflow

The client and server must pre-share the same key. The entire interaction flow is as follows:

**Login Phase**

1. The client inputs a username and a secret key, then converts the key into a hash value
2. The client encrypts the username using AES with this hash value
3. The client sends the encrypted packet to the server

**Server Verification**

4. The server decrypts the packet using the pre-configured key
5. If decryption fails or the username does not match, the connection is rejected immediately
6. Upon successful verification, the server returns an OK result along with an ID

**ID Chain Management**

7. The client must carry its current ID in every subsequent operation
8. Upon receiving an operation packet, the server decrypts it using the key and verifies the operation ID
9. After successful verification, the server destroys the current ID and generates a new one
10. The server encrypts the new ID along with the operation result and returns it to the client
11. The client decrypts the packet to obtain the new ID for the next operation

Example: Assume the login response returns ID 1. For the next packet, the client must encrypt the packet using the key, including both the operation data and ID 1. After decrypting and verifying ID 1, the server destroys ID 1, generates ID 2, then encrypts ID 2 along with the result and returns it to the client. Subsequent operations follow the same pattern.

## III. Exception Recovery Mechanism

When a response packet is lost, causing the client's ID to become out of sync with the server, the protocol includes a built-in automatic recovery logic:

1. The client sends an operation packet using its old ID
2. The server decrypts successfully but finds that this ID has already been invalidated
3. The server returns a recovery packet containing the current valid ID and a synchronization instruction
4. The client updates its local ID and sends a confirmation packet
5. After server confirmation, normal communication resumes

For the CHAP-IEM variant (where the ID is used directly as the encryption key), out-of-sync conditions require the client to re-authenticate in order to rebuild the key chain.

## IV. Security Characteristics

An attacker cannot decrypt intercepted ciphertext without the key, nor can they read the ID contained within. Even if the attacker replays an old packet, the server will reject the operation directly because the ID has already been destroyed.

## V. Deeper Essence: Zigzag Interaction Model (ZIM)

CHAP does not represent a proprietary framework. Its deeper essence is the **Zigzag Interaction Model (ZIM)**.

The core characteristic of this model is that during the interaction between client and server, two consecutive sessions are always offset by one "tooth" while maintaining a meshed state as a whole. Each request carries the current tooth position, and each response advances to the next tooth position, forming a continuous chain of state transitions.

CHAP is merely one exemplary implementation of the ZIM model. Any protocol that conforms to this model can be considered a member of the CHAP family.
