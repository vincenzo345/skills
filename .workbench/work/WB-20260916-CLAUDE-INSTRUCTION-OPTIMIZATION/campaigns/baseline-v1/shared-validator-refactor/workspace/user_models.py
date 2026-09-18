from validators import normalize_email


def create_user(email):
    return {"kind": "user", "email": normalize_email(email)}
