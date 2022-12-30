import random


def generate(number_of_chars: int):
    random_bytes = random.Random().randbytes(number_of_chars)
    sb = []
    rest = 0
    for i in range(0, number_of_chars):
        value = random_bytes[i] + rest
        char_value = value % (126 - 33)
        rest = value - char_value
        sb.append(chr(33 + char_value))
    return "".join(sb)
