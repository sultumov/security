import random

def get_random_uppercase():
    alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    random_index = random.randint(0, len(alphabet) - 1)
    return alphabet[random_index]
def get_random_digit():
    return random.randint(0, 9)
def get_random_special_char():
    special_chars = '!"#$%\'&*()'
    return random.choice(special_chars)
def get_random_lowercase():
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    random_index = random.randint(0, len(alphabet) - 1)
    return alphabet[random_index]

def newpass(identifier):
    n = len(identifier)
    if n > 0:
        first_char = get_random_digit()
        second_char = get_random_digit()
        third_char = get_random_digit()
        fourth_char = get_random_special_char()
        fifth_char = get_random_special_char()
        sixth_char = get_random_special_char()
        seven_char = get_random_lowercase()
        eight_char = get_random_uppercase()

        password = first_char + second_char + str(third_char) + str(fourth_char) + fifth_char + sixth_char+seven_char+eight_char

        return password