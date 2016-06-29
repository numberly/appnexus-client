import re


class classproperty(property):

    def __get__(self, cls, owner):
        return self.fget(owner)

SERVICE_NAME_RE = re.compile("[A-Z][a-z]*")


def normalize_service_name(service_name, delimiter='-'):
    words = [word.lower() for word in SERVICE_NAME_RE.findall(service_name)]
    normalized_name = delimiter.join(words)
    return normalized_name

__all__ = ["classproperty", "normalize_service_name"]
