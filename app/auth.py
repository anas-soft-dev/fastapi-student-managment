from passlib.context import CryptContext

crypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated = "auto"
)

def make_hash(pwd: str) -> str:
    return crypt_context.hash(pwd)

def verify_hash(pwd: str, hash_pwd) -> bool:
    return crypt_context.verify(pwd, hash_pwd)