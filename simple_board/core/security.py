from pwdlib import PasswordHash

# Argon2 설정
password_hash = PasswordHash.recommended()

# 단방향 암호화 -> 복호화는 없음
# 12345 => 암호화

# 암호화
def has_password(plain: str) -> str:
    return password_hash.hash(plain)

# 암호화된 내용 비교
def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)
