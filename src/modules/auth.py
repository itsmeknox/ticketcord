
import jwt
import time


from utils.exceptions import AuthenticationFailed

class JWT:
    def __init__(self, encryption_key: str) -> None:
        self.encryption_key = encryption_key
    
    def encrypt(self, data: dict, expire_seconds=None):
        if expire_seconds is None:
            expire_seconds = 3600*24*365*10
            
        current_time = time.time()
        expire_time = current_time + expire_seconds
        data['exp'] = expire_time
        return jwt.encode(data, self.encryption_key, algorithm='HS256')

    def decrypt(self, token: str):
        try:
            return jwt.decode(token, self.encryption_key, algorithms=['HS256'])
        except Exception as e:
            raise AuthenticationFailed

    