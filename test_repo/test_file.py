def hello():
    """A simple hello function."""
    return "Hello, World!"


class Calculator:
    """A simple calculator class."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        """Subtract two numbers."""
        return a - b


def main():
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"Result: {result}")
    print(hello())


if __name__ == "__main__":
    main()
