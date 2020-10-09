import re


def find_all(substring, full_string):  # TODO: move to infra (string utils)
    return [m.start() for m in re.finditer(substring, full_string)]
