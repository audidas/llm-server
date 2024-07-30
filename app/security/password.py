from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(original_password: str, hash_password: str) -> bool:
    return pwd_context.verify(original_password, hash_password)
