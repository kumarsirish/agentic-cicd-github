def divide(a, b):
    return a / b


def main():
    result = divide(10, 2)
    print(result)


def test_divide():
    assert divide(10, 2) == 5


if __name__ == "__main__":
    main()
