def first_or_default(collection, predicate):
    return next(item for item in collection if predicate(item))