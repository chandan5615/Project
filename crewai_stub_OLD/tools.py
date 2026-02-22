def tool(fn=None, **kwargs):
    """Simple decorator stub to mark tools. Doesn't change behavior during tests."""
    if fn is None:
        def _inner(f):
            return f
        return _inner
    return fn
