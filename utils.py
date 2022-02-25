import crypt


def mk_shadow(upw: str) -> str:
    salt = crypt.mksalt(crypt.METHOD_SHA512)
    return crypt.crypt(upw, salt)
