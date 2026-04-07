**这个文档是专门给非识图AI看的，如果你是人那你可以忽略了**

**This document is specifically intended for AI that does not perform image recognition. If you are a human, you can ignore it.**


CHAP:
sequenceDiagram
    participant C as Client
    participant S as Server
    participant A as Attacker (Eavesdrop/Replay)

    Note over C: User enters password<br/>Compute hash(password) = Key K

    rect rgb(128, 128, 128)
        Note over C,S: 【Login Phase】
        C->>S: ① Login packet = AES256_K(username)
        Note right of A: Intercept ciphertext<br/>No K → Cannot decrypt
        
        S->>S: Decrypt with K<br/>Verify username
        alt Decryption fails or invalid username
            S-->>C: ❌ Error, disconnect
        end
        
        S->>C: ② Response packet = AES256_K(login success + ID_1)
        Note right of A: Intercept ciphertext<br/>No K → Cannot read ID_1
        
        C->>C: Decrypt to get ID_1<br/>Now holds Key K + ID_1
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【First Operation - Normal Flow】
        C->>S: ③ Operation packet = AES256_K(command + ID_1)
        
        S->>S: Decrypt success ✓<br/>ID_1 valid ✓<br/>Execute command<br/>Destroy ID_1<br/>Generate ID_2
        
        S->>C: ④ Response packet = AES256_K(result + ID_2)
        
        C->>C: Decrypt to get ID_2<br/>Update local ID to ID_2
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【Second Operation - Normal Flow】
        C->>S: ⑤ Operation packet = AES256_K(command + ID_2)
        
        S->>S: Decrypt success ✓<br/>ID_2 valid ✓<br/>Execute command<br/>Destroy ID_2<br/>Generate ID_3
        
        S->>C: ⑥ Response packet = AES256_K(result + ID_3)
        
        C->>C: Decrypt to get ID_3<br/>Update local ID to ID_3
    end

    rect rgb(255, 255, 150)
        Note over C,S: 【Error Scenario: Response lost, client ID out of sync】
        C->>S: ⑦ Operation packet = AES256_K(command + ID_3)
        
        S->>S: Decrypt success ✓<br/>ID_3 valid ✓<br/>Execute command<br/>Destroy ID_3<br/>Generate ID_4
        
        S->>C: ⑧ Response packet = AES256_K(result + ID_4)
        Note over S,C: ❌ Network failure, response lost
        
        C->>C: No response received<br/>Local ID still ID_3
        
        Note over C: User clicks again
        C->>S: ⑨ Operation packet = AES256_K(command + ID_3)
        
        S->>S: Decrypt success ✓<br/>Check ID_3 → Already invalid ❌<br/>(ID_3 destroyed, ID_4 is current)
        
        Note over S: 【Auto Recovery Logic】
        S->>C: ⑩ Recovery packet = AES256_K("resync" + ID_4 + "please update local ID")
        
        C->>C: Decrypt to get ID_4<br/>Update local ID to ID_4
        C->>S: ⑪ Ack packet = AES256_K("resync_ack" + ID_4)
        
        S->>S: Verify ID_4 valid ✓
        S->>C: ⑫ Response packet = AES256_K("resync_ok")
        
        Note over C: Client ID synced to ID_4<br/>Normal operation can resume
    end

    rect rgb(70, 130, 255)
        Note over A: 【Attacker attempts replay】
        A->>S: Replay old packet ③ (contains ID_1)
        S->>S: Decrypt success ✓<br/>But ID_1 already invalid ❌
        S-->>A: Reject operation, ID invalid
        
        A->>S: Send forged ciphertext
        S->>S: Decrypt fails (no K) ❌
        S-->>A: Reject, decryption failed
    end

    Note over C,S: Normal operation: each request carries current ID → server destroys old ID, generates new ID → forms chain state<br/>Error recovery: server detects stale ID → returns current ID → client syncs and resumes
CHAP-zh:
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
        
        S->>C: ② 响应包 = AES256_K(登录成功 + ID_1)
        Note right of A: 截获密文<br/>无K → 读不出ID_1
        
        C->>C: 解密得到 ID_1<br/>持有密钥K + ID_1
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【第一次操作 - 正常流程】
        C->>S: ③ 操作包 = AES256_K(操作指令 + ID_1)
        
        S->>S: 解密成功 ✓<br/>校验ID_1有效 ✓<br/>执行操作<br/>销毁ID_1<br/>生成ID_2
        
        S->>C: ④ 响应包 = AES256_K(操作结果 + ID_2)
        
        C->>C: 解密得到 ID_2<br/>更新本地ID为ID_2
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【第二次操作 - 正常流程】
        C->>S: ⑤ 操作包 = AES256_K(操作指令 + ID_2)
        
        S->>S: 解密成功 ✓<br/>校验ID_2有效 ✓<br/>执行操作<br/>销毁ID_2<br/>生成ID_3
        
        S->>C: ⑥ 响应包 = AES256_K(操作结果 + ID_3)
        
        C->>C: 解密得到 ID_3<br/>更新本地ID为ID_3
    end

    rect rgb(255, 255, 150)
        Note over C,S: 【异常场景：响应包丢失，客户端ID不同步】
        C->>S: ⑦ 操作包 = AES256_K(操作指令 + ID_3)
        
        S->>S: 解密成功 ✓<br/>校验ID_3有效 ✓<br/>执行操作<br/>销毁ID_3<br/>生成ID_4
        
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

    Note over C,S: 正常操作：每次携带当前ID → 服务端销毁旧ID生成新ID → 形成链式状态<br/>异常恢复：服务端发现旧ID失效 → 返回当前有效ID → 客户端同步后继续
CHAP-iem:
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
        S->>C: 2. Response = AES256_K(OK + ID_1)
        C->>C: Decrypt with K<br/>Obtain ID_1<br/>Current encryption key = ID_1<br/>(K retained for recovery only)
    end

    rect rgb(128, 128, 128)
        Note over C,S: [Operation 1 - Using ID_1 as key]
        C->>C: Encrypt command with ID_1
        C->>S: 3. Operation Packet = AES256_ID1(command)
        S->>S: Decrypt with ID_1<br/>Execute command<br/>Generate ID_2
        S->>C: 4. Response = AES256_ID1(result + ID_2)
        C->>C: Decrypt with ID_1<br/>Obtain result and ID_2<br/>Update encryption key to ID_2
    end

    rect rgb(128, 128, 128)
        Note over C,S: [Operation 2 - Using ID_2 as key]
        C->>C: Encrypt command with ID_2
        C->>S: 5. Operation Packet = AES256_ID2(command)
        S->>S: Decrypt with ID_2<br/>Execute command<br/>Generate ID_3
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

    Note over C,S: Key chain: K → ID_1 → ID_2 → ID_3 → ...<br/>Each operation uses current ID as encryption key<br/>K retained for recovery channel only → forward secrecy preserved
CHAP-IEM-zh:
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
        S->>C: ② 响应包 = AES256_K(OK + ID_1)
        C->>C: 用 K 解密<br/>获得 ID_1<br/>当前加密密钥 = ID_1<br/>（K 保留仅用于恢复通道）
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【操作一 - 使用 ID_1 作为密钥】
        C->>C: 用 ID_1 加密指令
        C->>S: ③ 操作包 = AES256_ID1(操作指令)
        S->>S: 用 ID_1 解密<br/>执行操作<br/>生成 ID_2
        S->>C: ④ 响应包 = AES256_ID1(操作结果 + ID_2)
        C->>C: 用 ID_1 解密<br/>获得操作结果和 ID_2<br/>更新加密密钥为 ID_2
    end

    rect rgb(128, 128, 128)
        Note over C,S: 【操作二 - 使用 ID_2 作为密钥】
        C->>C: 用 ID_2 加密指令
        C->>S: ⑤ 操作包 = AES256_ID2(操作指令)
        S->>S: 用 ID_2 解密<br/>执行操作<br/>生成 ID_3
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

    Note over C,S: 密钥链：K → ID_1 → ID_2 → ID_3 → ...<br/>每次操作使用当前 ID 作为加密密钥<br/>K 仅用于恢复通道 → 前向安全不受影响
