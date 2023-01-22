def to_camel(string: str) -> str:
    """BaseModel alias_generator setup to convert
    snake case to camel case attribute"""
    words = string.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])
