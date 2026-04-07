import hashlib
import secrets
import json
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

class ChapIemSession:
    def __init__(self, session_id: str, client_id: str):
        self.session_id = session_id
        self.client_id = client_id
        self.last_activity = datetime.utcnow()

class ChapIemHandler:
    def __init__(self, admin_password: str):
        self._master_key = hashlib.sha256(admin_password.encode()).digest()
        self._sessions: Dict[str, ChapIemSession] = {}
    
    def _encrypt(self, key: bytes, plaintext: str) -> bytes:
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padder = PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return iv + ciphertext
    
    def _decrypt(self, key: bytes, ciphertext_with_iv: bytes) -> Optional[str]:
        try:
            iv = ciphertext_with_iv[:16]
            ciphertext = ciphertext_with_iv[16:]
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            unpadder = PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data.decode()
        except Exception:
            return None
    
    def _generate_session_id(self) -> str:
        return secrets.token_hex(32)
    
    def _ensure_256bit_key(self, session_id: str) -> bytes:
        id_bytes = session_id.encode()
        if len(id_bytes) == 32:
            return id_bytes
        return hashlib.sha256(id_bytes).digest()
    
    def _error_response(self, message: str, new_id: Optional[str] = None) -> dict:
        return {"success": False, "message": message, "newId": new_id}
    
    def _success_response(self, message: str, new_id: Optional[str] = None, data: Optional[dict] = None) -> dict:
        return {"success": True, "message": message, "newId": new_id, "data": data}
    
    def handle_login(self, encrypted_data: bytes, client_id: str) -> bytes:
        decrypted = self._decrypt(self._master_key, encrypted_data)
        if decrypted is None:
            response = self._error_response("authentication_failed")
            return self._encrypt(self._master_key, json.dumps(response))
        
        username = decrypted.strip()
        if username != "admin":
            response = self._error_response("authentication_failed")
            return self._encrypt(self._master_key, json.dumps(response))
        
        session_id = self._generate_session_id()
        self._sessions[session_id] = ChapIemSession(session_id, client_id)
        
        response = self._success_response("login_success", session_id)
        return self._encrypt(self._master_key, json.dumps(response))
    
    def handle_operation(self, encrypted_data: bytes, client_id: str) -> bytes:
        session_id = None
        current_key = None
        session = None
        
        for s in self._sessions.values():
            if s.client_id == client_id:
                test_key = self._ensure_256bit_key(s.session_id)
                test_decrypt = self._decrypt(test_key, encrypted_data)
                if test_decrypt is not None:
                    session_id = s.session_id
                    current_key = test_key
                    session = s
                    break
        
        if session_id is None or current_key is None or session is None:
            response = self._error_response("out_of_sync")
            return self._encrypt(self._master_key, json.dumps(response))
        
        decrypted = self._decrypt(current_key, encrypted_data)
        if decrypted is None:
            response = self._error_response("decryption_failed")
            return self._encrypt(self._master_key, json.dumps(response))
        
        try:
            request = json.loads(decrypted)
        except json.JSONDecodeError:
            response = self._error_response("invalid_request")
            return self._encrypt(self._master_key, json.dumps(response))
        
        if request.get("sessionId") != session_id:
            response = self._error_response("session_mismatch")
            return self._encrypt(current_key, json.dumps(response))
        
        del self._sessions[session_id]
        
        new_session_id = self._generate_session_id()
        self._sessions[new_session_id] = ChapIemSession(new_session_id, client_id)
        
        operation_result = None
        action = request.get("action")
        if action:
            operation_result = {
                "action": action,
                "processed": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        response = self._success_response("operation_success", new_session_id, operation_result)
        return self._encrypt(current_key, json.dumps(response))
    
    def validate_session(self, session_id: str, client_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        if session.client_id != client_id:
            return False
        
        if datetime.utcnow() - session.last_activity > timedelta(hours=1):
            del self._sessions[session_id]
            return False
        
        session.last_activity = datetime.utcnow()
        return True
    
    def cleanup_expired_sessions(self) -> None:
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session.last_activity > timedelta(hours=1)
        ]
        for sid in expired:
            del self._sessions[sid]
