import unicodedata


def canonical_username(value: str) -> str:
    # casefold() can yield non-normalized output, so normalize again afterwards.
    folded = unicodedata.normalize("NFKC", value).casefold()
    return unicodedata.normalize("NFKC", folded)


def find_user(query: str, users: list[str]) -> str | None:
    wanted = canonical_username(query)
    return next((user for user in users if canonical_username(user) == wanted), None)
