from nacl import encoding, public
import base64


def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


print(
    encrypt(
        "KG14zpA08q4+04d+iAisK+Uri2wMk1sdB9pkP3ZHEWk=",
        "Hello World",
    )
)
