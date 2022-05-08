def generate_payload(**kwargs):
    """Generates a dictionary of provided keywords and values."""
    return {key: value for (key, value) in kwargs.items()}
