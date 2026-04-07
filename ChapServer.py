import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class CHAPServer:
    def __init__(self, users_db):
        """
        Initialize CHAP server with PIH optimization.
        
        users_db: List of dict objects with keys: id, username, password
        """
        self.login_index = {}      # SHA256(ciphertext) -> user_id
        self.user_keys = {}        # user_id -> pre-shared key K
        self.user_sessions = {}     # user_id -> current_session {id, key}
        self.user_data = {}         # user_id -> user info
        
        # Phase 1: Startup precomputation
        for user in users_db:
            user_id = user['id']
            username = user['username']
            password = user['password']
            
            # Compute pre-shared key K
            K = hashlib.sha256(password.encode()).digest()
            
            # Compute expected login ciphertext
            ciphertext = self._aes_encrypt(K, username)
            
            # Store hash for O(1) lookup
            login_hash = hashlib.sha256(ciphertext).digest()
            self.login_index[login_hash] = user_id
            
            # Store K for later use
            self.user_keys[user_id] = K
            self.user_data[user_id] = user
            
            # Initialize session state
            self.user_sessions[user_id] = {
                'current_id': None,
                'key': K
            }
    
    def login(self, ciphertext):
        """
        Phase 2: Runtime login with O(1) hash lookup.
        
        Returns: (success, user_id, current_id, message)
        """
        # Compute hash of received ciphertext
        request_hash = hashlib.sha256(ciphertext).digest()
        
        # O(1) lookup
        user_id = self.login_index.get(request_hash)
        
        if user_id is None:
            return (False, None, None, "Invalid credentials")
        
        # Verify with actual decryption (prevents theoretical false positives)
        K = self.user_keys[user_id]
        plaintext = self._aes_decrypt(K, ciphertext)
        
        if plaintext == self.user_data[user_id]['username']:
            # Login success - generate first ID
            current_id = self._generate_id()
            self.user_sessions[user_id]['current_id'] = current_id
            
            # Response: OK + ID_1 encrypted with K
            response = f"OK|{current_id}"
            encrypted_response = self._aes_encrypt(K, response)
            
            return (True, user_id, current_id, encrypted_response)
        else:
            return (False, None, None, "Invalid credentials")
    
    def operation(self, user_id, encrypted_packet):
        """
        Handle operation packet.
        
        encrypted_packet: AES256_K(operation_data + current_id)
        """
        session = self.user_sessions.get(user_id)
        if session is None:
            return (False, None, "Session not found")
        
        K = session['key']
        current_id = session['current_id']
        
        # Decrypt with K
        plaintext = self._aes_decrypt(K, encrypted_packet)
        
        # Expected format: "operation_data|id"
        try:
            operation_data, received_id = plaintext.rsplit('|', 1)
        except ValueError:
            return (False, None, "Invalid packet format")
        
        # Verify ID
        if received_id != str(current_id):
            # Out of sync - return recovery packet
            recovery_packet = f"resync|{current_id}"
            encrypted_recovery = self._aes_encrypt(K, recovery_packet)
            return (False, encrypted_recovery, "ID mismatch, resync required")
        
        # Execute operation
        result = self._execute_operation(operation_data)
        
        # Generate new ID
        new_id = self._generate_id()
        session['current_id'] = new_id
        
        # Response: result + new_id encrypted with K
        response = f"{result}|{new_id}"
        encrypted_response = self._aes_encrypt(K, response)
        
        return (True, encrypted_response, "OK")
    
    def resync_confirm(self, user_id, encrypted_packet):
        """Handle resync confirmation from client."""
        session = self.user_sessions.get(user_id)
        if session is None:
            return (False, None, "Session not found")
        
        K = session['key']
        plaintext = self._aes_decrypt(K, encrypted_packet)
        
        if plaintext.startswith("resync_ack|"):
            received_id = plaintext.split('|')[1]
            if received_id == str(session['current_id']):
                return (True, self._aes_encrypt(K, "resync_ok"), "Resync successful")
        
        return (False, None, "Resync failed")
    
    def _aes_encrypt(self, key, plaintext):
        """AES-256-CBC encryption."""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # PKCS7 padding
        pad_len = 16 - (len(plaintext.encode()) % 16)
        padded = plaintext.encode() + bytes([pad_len] * pad_len)
        
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        return iv + ciphertext
    
    def _aes_decrypt(self, key, ciphertext):
        """AES-256-CBC decryption."""
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded = decryptor.update(actual_ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        pad_len = padded[-1]
        return padded[:-pad_len].decode()
    
    def _generate_id(self):
        """Generate a new session ID."""
        return os.urandom(16).hex()
    
    def _execute_operation(self, operation_data):
        """Execute business logic operation."""
        # Implementation dependent
        return f"Result of: {operation_data}"
