from validators import normalize_email


def create_admin(email):
    return {"kind": "admin", "email": normalize_email(email)}
