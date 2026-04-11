# Flowchart-code.md

**这个文档是专门给非识图AI看的，如果你是人那你可以忽略了**

**This document is specifically intended for AI that does not perform image recognition. If you are a human, you can ignore it.**

---

## CHAP

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant A as Attacker (Eavesdrop/Replay)

    Note over C: User enters password<br/>Compute hash(password) = Key K

    rect rgb(128, 128, 128)
        Note over C,S: [Login Phase]
        C->>S: ① Login packet = AES256_K(username)
        Note right of A: Intercept ciphertext<br/>No K → Cannot decrypt
        
        S->>S: Decrypt with K<br/>Verify username
        alt Decryption fails or invalid username
            S-->>C: ❌ Error, disconnect
        end
        
        Note over S: Generate random ID_1<br/>(MUST be cryptographically random)
        S->>C: ② Response packet = AES256_K(login success + ID_1)
        Note right of A: Intercept ciphertext<br/>No K → Cannot read ID_1
        
        C->>C: Decrypt to get ID_1<br/>Now holds Key K + ID_1
    end

    rect rgb(128, 128, 128)
        Note over C,S: [First Operation - Normal Flow]
        C->>S: ③ Operation packet = AES256_K(command + ID_1)
        
        S->>S: Decrypt success ✓<br/>ID_1 valid ✓<br/>Execute command<br/>Destroy ID_1<br/>Generate random ID_2 (MUST be random)
        
        S->>C: ④ Response packet = AES256_K(result + ID_2)
        
        C->>C: Decrypt to get ID_2<br/>Update local ID to ID_2
    end

    rect rgb(128, 128, 128)
        Note over C,S: [Second Operation - Normal Flow]
        C->>S: ⑤ Operation packet = AES256_K(command + ID_2)
        
        S->>S: Decrypt success ✓<br/>ID_2 valid ✓<br/>Execute command<br/>Destroy ID_2<br/>Generate random ID_3 (MUST be random)
        
        S->>C: ⑥ Response packet = AES256_K(result + ID_3)
        
        C->>C: Decrypt to get ID_3<br/>Update local ID to ID_3
    end

    rect rgb(255, 255, 150)
        Note over C,S: [Error Scenario: Response lost, client ID out of sync]
        C->>S: ⑦ Operation packet = AES256_K(command + ID_3)
        
        S->>S: Decrypt success ✓<br/>ID_3 valid ✓<br/>Execute command<br/>Destroy ID_3<br/>Generate random ID_4 (MUST be random)
        
        S->>C: ⑧ Response packet = AES256_K(result + ID_4)
        Note over S,C: ❌ Network failure, response lost
        
        C->>C: No response received<br/>Local ID still ID_3
        
        Note over C: User clicks again
        C->>S: ⑨ Operation packet = AES256_K(command + ID_3)
        
        S->>S: Decrypt success ✓<br/>Check ID_3 → Already invalid ❌<br/>(ID_3 destroyed, ID_4 is current)
        
        Note over S: [Auto Recovery Logic]
        S->>C: ⑩ Recovery packet = AES256_K("resync" + ID_4 + "please update local ID")
        
        C->>C: Decrypt to get ID_4<br/>Update local ID to ID_4
        C->>S: ⑪ Ack packet = AES256_K("resync_ack" + ID_4)
        
        S->>S: Verify ID_4 valid ✓
        S->>C: ⑫ Response packet = AES256_K("resync_ok")
        
        Note over C: Client ID synced to ID_4<br/>Normal operation can resume
    end

    rect rgb(70, 130, 255)
        Note over A: [Attacker attempts replay]
        A->>S: Replay old packet ③ (contains ID_1)
        S->>S: Decrypt success ✓<br/>But ID_1 already invalid ❌
        S-->>A: Reject operation, ID invalid
        
        A->>S: Send forged ciphertext
        S->>S: Decrypt fails (no K) ❌
        S-->>A: Reject, decryption failed
    end

    Note over C,S: Normal operation: each request carries current ID → server destroys old ID, generates new random ID → forms chain state<br/>Error recovery: server detects stale ID → returns current ID → client syncs and resumes<br/><br/>⚠️ CRITICAL: All IDs MUST be generated using a cryptographically secure random number generator. Predictable IDs (sequential, timestamp-based, etc.) allow session hijacking and are a severe security vulnerability.
```

---

## CHAP-zh

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务端
    participant A as 攻击者(窃听/重放)

    Note over C: 用户输入密码<br/>计算 hash(密码) = 密钥K

    rect rgb(128, 128, 128)
        Note over C,S: 【登录阶段】
        C->>S: ① 登录包 = AES256_K(用户名)
        Note right of A: 截获密文<br/>无K → 无法解密
        
        S->>S: 用K解密<br/>验证用户名
        alt 解密失败或用户名无效
            S-->>C: ❌ 报错断开
        end
        
        Note over S: 生成随机 ID_1<br/>（必须使用密码学安全随机数）
        S->>C: ② 响应包 = AES256_K(登录成功 + ID_1)
        Note right of A: 截获密文<br/>无K → 读不出ID_1
        
        C->>C: 解密得到 ID_1<br/>持有密钥K + ID_1
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【第一次操作 - 正常流程】
        C->>S: ③ 操作包 = AES256_K(操作指令 + ID_1)
        
        S->>S: 解密成功 ✓<br/>校验ID_1有效 ✓<br/>执行操作<br/>销毁ID_1<br/>生成随机 ID_2（必须随机）
        
        S->>C: ④ 响应包 = AES256_K(操作结果 + ID_2)
        
        C->>C: 解密得到 ID_2<br/>更新本地ID为ID_2
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【第二次操作 - 正常流程】
        C->>S: ⑤ 操作包 = AES256_K(操作指令 + ID_2)
        
        S->>S: 解密成功 ✓<br/>校验ID_2有效 ✓<br/>执行操作<br/>销毁ID_2<br/>生成随机 ID_3（必须随机）
        
        S->>C: ⑥ 响应包 = AES256_K(操作结果 + ID_3)
        
        C->>C: 解密得到 ID_3<br/>更新本地ID为ID_3
    end

    rect rgb(255, 255, 150)
        Note over C,S: 【异常场景：响应包丢失，客户端ID不同步】
        C->>S: ⑦ 操作包 = AES256_K(操作指令 + ID_3)
        
        S->>S: 解密成功 ✓<br/>校验ID_3有效 ✓<br/>执行操作<br/>销毁ID_3<br/>生成随机 ID_4（必须随机）
        
        S->>C: ⑧ 响应包 = AES256_K(操作结果 + ID_4)
        Note over S,C: ❌ 网络故障，响应包丢失
        
        C->>C: 未收到响应<br/>本地ID仍为ID_3
        
        Note over C: 用户再次点击操作
        C->>S: ⑨ 操作包 = AES256_K(操作指令 + ID_3)
        
        S->>S: 解密成功 ✓<br/>校验ID_3 → 已失效 ❌<br/>（因为ID_3已被销毁，ID_4是当前有效ID）
        
        Note over S: 【自动恢复逻辑】
        S->>C: ⑩ 恢复包 = AES256_K("resync" + ID_4 + "请更新本地ID")
        
        C->>C: 解密得到 ID_4<br/>更新本地ID为ID_4
        C->>S: ⑪ 确认包 = AES256_K("resync_ack" + ID_4)
        
        S->>S: 校验ID_4有效 ✓
        S->>C: ⑫ 响应包 = AES256_K("resync_ok")
        
        Note over C: 客户端ID已同步为ID_4<br/>可继续正常操作
    end

    rect rgb(70, 130, 255)
        Note over A: 【攻击者尝试重放】
        A->>S: 重放 ③ 的旧包 (含ID_1)
        S->>S: 解密成功 ✓<br/>但ID_1已失效 ❌
        S-->>A: 拒绝操作，ID无效
        
        A->>S: 发送伪造密文
        S->>S: 解密失败 (无K) ❌
        S-->>A: 拒绝，解密失败
    end

    Note over C,S: 正常操作：每次携带当前ID → 服务端销毁旧ID生成新随机ID → 形成链式状态<br/>异常恢复：服务端发现旧ID失效 → 返回当前有效ID → 客户端同步后继续<br/><br/>⚠️ 关键安全要求：所有 ID 必须使用密码学安全随机数生成器生成。可预测的 ID（如递增序列、时间戳等）会导致会话劫持，属于严重安全漏洞。
```

---

## CHAP-IEM

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    Note over C: User inputs username & password<br/>Compute hash(password) = Pre-shared Key K

    rect rgb(128, 128, 128)
        Note over C,S: [Login Phase - Using Pre-shared Key K]
        C->>S: 1. Login Packet = AES256_K(username)
        S->>S: Decrypt with K<br/>Verify username
        alt Decrypt fails or username invalid
            S-->>C: Error, connection closed
        end
        
        Note over S: Generate random ID_1<br/>(MUST be cryptographically random)
        S->>C: 2. Response = AES256_K(OK + ID_1)
        C->>C: Decrypt with K<br/>Obtain ID_1<br/>Current encryption key = ID_1<br/>(K retained for recovery only)
    end

    rect rgb(128, 128, 128)
        Note over C,S: [Operation 1 - Using ID_1 as key]
        C->>C: Encrypt command with ID_1
        C->>S: 3. Operation Packet = AES256_ID1(command)
        S->>S: Decrypt with ID_1<br/>Execute command<br/>Generate random ID_2 (MUST be random)
        S->>C: 4. Response = AES256_ID1(result + ID_2)
        C->>C: Decrypt with ID_1<br/>Obtain result and ID_2<br/>Update encryption key to ID_2
    end

    rect rgb(128, 128, 128)
        Note over C,S: [Operation 2 - Using ID_2 as key]
        C->>C: Encrypt command with ID_2
        C->>S: 5. Operation Packet = AES256_ID2(command)
        S->>S: Decrypt with ID_2<br/>Execute command<br/>Generate random ID_3 (MUST be random)
        S->>C: 6. Response = AES256_ID2(result + ID_3)
        C->>C: Decrypt with ID_2<br/>Obtain result and ID_3<br/>Update encryption key to ID_3
    end

    rect rgb(255, 255, 150)
        Note over C,S: [Exception: Response lost, key out of sync]
        C->>C: Local key = ID_3
        C->>S: 7. Operation Packet = AES256_ID3(command)
        S->>S: Decrypt with ID_3<br/>But ID_3 is no longer valid<br/>(Current key is ID_4)
        
        Note over S: [Auto Recovery using K (recovery channel)]
        S->>C: 8. Recovery Packet = AES256_K("resync" + ID_4 + "please update local ID")
        
        C->>C: Decrypt with K (retained since login)<br/>Obtain ID_4<br/>Update encryption key to ID_4
        
        C->>S: 9. Ack Packet = AES256_ID4("resync_ack")
        
        S->>S: Verify ID_4 valid ✓
        S->>C: 10. Response = AES256_ID4("resync_ok")
        
        Note over C,S: Key chain continues: ... → ID_3 → ID_4 → ID_5 → ...
    end

    rect rgb(70, 130, 255)
        Note over A: [Attacker Attempts]
        A->>S: Replay old packet (AES256_ID1)
        S->>S: Current key is ID_2 or ID_3<br/>Decrypt with current key fails
        S-->>A: Rejected
        A->>S: Send forged ciphertext
        S-->>A: Decrypt fails, rejected
    end

    Note over C,S: Key chain: K → ID_1 → ID_2 → ID_3 → ...<br/>Each operation uses current ID as encryption key<br/>K retained for recovery channel only → forward secrecy preserved<br/><br/>⚠️ CRITICAL: All IDs MUST be generated using a cryptographically secure random number generator. Since IDs serve as encryption keys in CHAP-IEM, predictable IDs completely break the security model.
```

---

## CHAP-IEM-zh

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务端

    Note over C: 用户输入用户名和密码<br/>计算哈希值 = 预共享密钥 K

    rect rgb(128, 128, 128)
        Note over C,S: 【登录阶段 - 使用预共享密钥 K】
        C->>S: ① 登录包 = AES256_K(用户名)
        S->>S: 用 K 解密<br/>验证用户名
        alt 解密失败或用户名无效
            S-->>C: 错误，连接断开
        end
        
        Note over S: 生成随机 ID_1<br/>（必须使用密码学安全随机数）
        S->>C: ② 响应包 = AES256_K(OK + ID_1)
        C->>C: 用 K 解密<br/>获得 ID_1<br/>当前加密密钥 = ID_1<br/>（K 保留仅用于恢复通道）
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【操作一 - 使用 ID_1 作为密钥】
        C->>C: 用 ID_1 加密指令
        C->>S: ③ 操作包 = AES256_ID1(操作指令)
        S->>S: 用 ID_1 解密<br/>执行操作<br/>生成随机 ID_2（必须随机）
        S->>C: ④ 响应包 = AES256_ID1(操作结果 + ID_2)
        C->>C: 用 ID_1 解密<br/>获得操作结果和 ID_2<br/>更新加密密钥为 ID_2
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【操作二 - 使用 ID_2 作为密钥】
        C->>C: 用 ID_2 加密指令
        C->>S: ⑤ 操作包 = AES256_ID2(操作指令)
        S->>S: 用 ID_2 解密<br/>执行操作<br/>生成随机 ID_3（必须随机）
        S->>C: ⑥ 响应包 = AES256_ID2(操作结果 + ID_3)
        C->>C: 用 ID_2 解密<br/>获得操作结果和 ID_3<br/>更新加密密钥为 ID_3
    end

    rect rgb(255, 255, 150)
        Note over C,S: 【异常场景：响应包丢失，密钥不同步】
        C->>C: 本地密钥 = ID_3
        C->>S: ⑦ 操作包 = AES256_ID3(操作指令)
        S->>S: 用 ID_3 解密成功<br/>但 ID_3 已失效<br/>（当前有效密钥为 ID_4）
        
        Note over S: 【自动恢复 - 使用 K 作为恢复通道】
        S->>C: ⑧ 恢复包 = AES256_K("resync" + ID_4 + "请更新本地ID")
        
        C->>C: 用 K（登录后一直保留）解密<br/>获得 ID_4<br/>更新加密密钥为 ID_4
        
        C->>S: ⑨ 确认包 = AES256_ID4("resync_ack")
        
        S->>S: 校验 ID_4 有效 ✓
        S->>C: ⑩ 响应包 = AES256_ID4("resync_ok")
        
        Note over C,S: 密钥链继续：... → ID_3 → ID_4 → ID_5 → ...
    end

    rect rgb(70, 130, 255)
        Note over A: 【攻击者尝试】
        A->>S: 重放旧包（AES256_ID1）
        S->>S: 当前密钥为 ID_2 或 ID_3<br/>用当前密钥解密失败
        S-->>A: 拒绝
        A->>S: 发送伪造密文
        S-->>A: 解密失败，拒绝
    end

    Note over C,S: 密钥链：K → ID_1 → ID_2 → ID_3 → ...<br/>每次操作使用当前 ID 作为加密密钥<br/>K 仅用于恢复通道 → 前向安全不受影响<br/><br/>⚠️ 关键安全要求：所有 ID 必须使用密码学安全随机数生成器生成。在 CHAP-IEM 中 ID 同时作为加密密钥，可预测的 ID 会彻底破坏整个安全模型。
```

---

## CHAP-IEM-SKN

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    Note over C,S: [Pre-shared Phase]
    Note over C: Holds pre-shared key Y
    Note over S: Holds pre-shared key Y

    rect rgb(128, 128, 128)
        Note over C,S: [Key Exchange Phase - Plaintext, No Encryption Required]
        C->>C: Generate random a
        S->>S: Generate random b
        C->>C: A = Y ⊕ a
        S->>S: B = Y ⊕ b
        C->>S: Send A
        S->>C: Send B
        C->>C: K_base = B ⊕ a = Y ⊕ a ⊕ b
        S->>S: K_base = A ⊕ b = Y ⊕ a ⊕ b
        C->>C: K_session = SHA256(K_base)
        S->>S: K_session = SHA256(K_base)
        Note over C,S: Discard a, b, K_base
    end

    rect rgb(128, 128, 128)
        Note over C,S: [Login Phase]
        C->>S: Login Packet = AES256_K_session(username)
        S->>S: Decrypt with K_session, verify username
        alt Decrypt fails or username invalid
            S-->>C: Error, connection closed
        end
        S->>S: Generate random ID₁ (MUST be cryptographically random)
        S->>C: Response Packet = AES256_K_session(OK + ID₁)
        C->>C: Decrypt to obtain ID₁
        Note over C: Current encryption key = ID₁
        Note over C: K_session retained for exception recovery
    end

    rect rgb(128, 128, 128)
        Note over C,S: [Operation 1 - Using ID₁ as key]
        C->>C: Encrypt command with ID₁
        C->>S: Operation Packet = AES256_ID₁(command)
        S->>S: Decrypt with ID₁
        S->>S: Execute command
        S->>S: Generate random ID₂ (MUST be random)
        S->>C: Response Packet = AES256_ID₁(result + ID₂)
        C->>C: Decrypt with ID₁
        C->>C: Update encryption key to ID₂
    end

    rect rgb(128, 128, 128)
        Note over C,S: [Operation 2 - Using ID₂ as key]
        C->>C: Encrypt command with ID₂
        C->>S: Operation Packet = AES256_ID₂(command)
        S->>S: Decrypt with ID₂
        S->>S: Execute command
        S->>S: Generate random ID₃ (MUST be random)
        S->>C: Response Packet = AES256_ID₂(result + ID₃)
        C->>C: Decrypt with ID₂
        C->>C: Update encryption key to ID₃
    end

    rect rgb(255, 255, 150)
        Note over C,S: [Exception: Response lost, key out of sync]
        C->>C: Local key = ID₃
        S->>S: Current valid key = ID₄
        C->>S: Operation Packet = AES256_ID₃(command)
        S->>S: Decrypt with ID₃ succeeds, but ID₃ is invalid
        Note over S: Use K_session for recovery packet
        S->>C: Recovery Packet = AES256_K_session("resync" + ID₄)
        C->>C: Decrypt with K_session, obtain ID₄
        C->>C: Update encryption key to ID₄
        C->>S: Ack Packet = AES256_ID₄("resync_ack")
        S->>S: Verify ID₄ valid
        S->>C: Response Packet = AES256_ID₄("resync_ok")
        Note over C,S: Key chain continues: ID₃ → ID₄ → ID₅ → ...
    end

    rect rgb(70, 130, 255)
        Note over A: [Attacker Perspective]
        Note over A: Intercepts A, B, Login Packet
        Note over A: Lacks Y → Cannot compute K_session
        Note over A: Cannot decrypt Login Packet
        Note over A: Cannot obtain ID₁
        Note over A: Cannot participate in any valid communication
    end

    Note over C,S: Key chain: Y → K_session → ID₁ → ID₂ → ID₃ → ...<br/>Key exchange transmitted in plaintext, security depends on confidentiality of Y<br/>K_session used only for login and exception recovery, not for operation chain<br/><br/>⚠️ CRITICAL: All IDs MUST be generated using a cryptographically secure random number generator. Since IDs serve as encryption keys in CHAP-IEM-SKN, predictable IDs completely break the security model.
```

---

## CHAP-IEM-SKN-zh

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务端

    Note over C,S: 【预共享阶段】
    Note over C: 持有预共享密钥 Y
    Note over S: 持有预共享密钥 Y

    rect rgb(128, 128, 128)
        Note over C,S: 【密钥交换阶段 - 明文传输，无需加密】
        C->>C: 生成随机数 a
        S->>S: 生成随机数 b
        C->>C: A = Y ⊕ a
        S->>S: B = Y ⊕ b
        C->>S: 发送 A
        S->>C: 发送 B
        C->>C: K_base = B ⊕ a = Y ⊕ a ⊕ b
        S->>S: K_base = A ⊕ b = Y ⊕ a ⊕ b
        C->>C: K_session = SHA256(K_base)
        S->>S: K_session = SHA256(K_base)
        Note over C,S: 废弃 a、b、K_base
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【登录阶段】
        C->>S: 登录包 = AES256_K_session(用户名)
        S->>S: 用 K_session 解密，验证用户名
        alt 解密失败或用户名无效
            S-->>C: 错误，连接断开
        end
        S->>S: 生成随机 ID₁（必须使用密码学安全随机数）
        S->>C: 响应包 = AES256_K_session(OK + ID₁)
        C->>C: 解密得到 ID₁
        Note over C: 当前加密密钥 = ID₁
        Note over C: K_session 保留用于异常恢复
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【操作一 - 使用 ID₁ 作为密钥】
        C->>C: 用 ID₁ 加密指令
        C->>S: 操作包 = AES256_ID₁(操作指令)
        S->>S: 用 ID₁ 解密
        S->>S: 执行操作
        S->>S: 生成随机 ID₂（必须随机）
        S->>C: 响应包 = AES256_ID₁(操作结果 + ID₂)
        C->>C: 用 ID₁ 解密
        C->>C: 更新加密密钥为 ID₂
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【操作二 - 使用 ID₂ 作为密钥】
        C->>C: 用 ID₂ 加密指令
        C->>S: 操作包 = AES256_ID₂(操作指令)
        S->>S: 用 ID₂ 解密
        S->>S: 执行操作
        S->>S: 生成随机 ID₃（必须随机）
        S->>C: 响应包 = AES256_ID₂(操作结果 + ID₃)
        C->>C: 用 ID₂ 解密
        C->>C: 更新加密密钥为 ID₃
    end

    rect rgb(255, 255, 150)
        Note over C,S: 【异常场景：响应包丢失，密钥不同步】
        C->>C: 本地密钥 = ID₃
        S->>S: 当前有效密钥 = ID₄
        C->>S: 操作包 = AES256_ID₃(操作指令)
        S->>S: 用 ID₃ 解密成功，但 ID₃ 已失效
        Note over S: 使用 K_session 加密恢复包
        S->>C: 恢复包 = AES256_K_session("resync" + ID₄)
        C->>C: 用 K_session 解密，获得 ID₄
        C->>C: 更新加密密钥为 ID₄
        C->>S: 确认包 = AES256_ID₄("resync_ack")
        S->>S: 校验 ID₄ 有效
        S->>C: 响应包 = AES256_ID₄("resync_ok")
        Note over C,S: 密钥链继续：ID₃ → ID₄ → ID₅ → ...
    end

    rect rgb(70, 130, 255)
        Note over A: 【攻击者视角】
        Note over A: 截获 A、B、登录包
        Note over A: 缺少 Y → 无法计算 K_session
        Note over A: 无法解密登录包
        Note over A: 无法获取 ID₁
        Note over A: 无法参与任何有效通信
    end

    Note over C,S: 密钥链：Y → K_session → ID₁ → ID₂ → ID₃ → ...<br/>密钥交换明文传输，安全性依赖 Y 的机密性<br/>K_session 仅用于登录和异常恢复，不参与操作链<br/><br/>⚠️ 关键安全要求：所有 ID 必须使用密码学安全随机数生成器生成。在 CHAP-IEM-SKN 中 ID 同时作为加密密钥，可预测的 ID 会彻底破坏整个安全模型。
```

---

## Summary of Changes

| Location | Change |
|----------|--------|
| Login Phase (all diagrams) | Added note: "Generate random ID_1 (MUST be cryptographically random)" |
| Each operation (all diagrams) | Added note: "Generate random ID_n (MUST be random)" |
| Footer note (CHAP) | Added critical warning about predictable IDs leading to session hijacking |
| Footer note (CHAP-IEM) | Added critical warning that predictable IDs completely break security model |
| Footer note (CHAP-IEM-SKN) | Added critical warning that predictable IDs completely break security model |
| CHAP-IEM-SKN (English) | Full flow diagram including key exchange, login, operations, and exception recovery |
| CHAP-IEM-SKN-zh (Chinese) | Full flow diagram including key exchange, login, operations, and exception recovery |
