from thingy import names_regex


class classproperty(property):

    def __get__(self, cls, owner):
        return self.fget(owner)


def normalize_service_name(service_name, delimiter='-'):
    words = [word.lower() for word in names_regex.findall(service_name)]
    normalized_name = delimiter.join(words)
    return normalized_name


__all__ = ["classproperty", "normalize_service_name"]
