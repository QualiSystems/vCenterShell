# util methods to help us work with collections


def first_or_default(collection, predicate):
    return next(item for item in collection if predicate(item))


# numeric utils


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
