from typing import Union

# Define a type alias for numbers (integers and floats)
Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """Return a + b."""
    return a + b


def subtract(a: Number, b: Number) -> Number:
    """Return a - b."""
    return a - b


def multiply(a: Number, b: Number) -> Number:
    """Return a * b."""
    return a * b


def divide(a: Number, b: Number) -> float:
    """Return a / b, raising ValueError for zero divisor."""
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b
