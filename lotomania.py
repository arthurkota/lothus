import os
import itertools
import random
import sys
import requests
from threading import Thread
from time import sleep
from termcolor import colored

os.system('color')

multi_of_three = [3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72,75,78,81,84,87,90,93,96,99]
fibonaccis = [1,2,3,5,8,13,21,34,55,89]
primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

class Loader:
    def __init__(self, desc="Loading", end="Done!", timeout=1):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        #self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.steps = [".", "..", "..."]
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in itertools.cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc}{c} ", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        print(f"\r{self.end}", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()

def validate_repeated(combination):
    return sum(1 for num in combination if num in dezenas) == 10

def validate_sum(combination):
    return 170 <= sum(combination) <= 220

def validate_evens(combination):
    return 24 <= sum(1 for num in combination if num % 2 == 0) <= 26

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def validate_primes(combination):
    return 12 <= sum(1 for num in combination if is_prime(num)) <= 13

def validate_multi_of_three(combination):
    return 16 <= sum(1 for num in combination if num % 3 == 0) <= 17

def is_fibonacci(n):
    a, b = 0, 1
    while b < n:
        a, b = b, a + b
    return b == n

def validate_fibonacci(combination):
    return sum(1 for num in combination if is_fibonacci(num)) == 5

def validate_consecutive_numbers(combination):
    count = 1
    for i in range(len(combination) - 1):
        if combination[i] + 1 == combination[i + 1]:
            count += 1
            if count > 5:
                return False
        else:
            count = 1
    return True

def validate_rows_columns(combination):
    # Create a 5x5 matrix and check if the combination does not form a full row or column
    matrix = [[0] * 10 for _ in range(10)]
    for i, num in enumerate(range(1, 100)):
        matrix[i // 10][i % 10] = num
    for row in matrix:
        if sum(1 for num in row if num in combination) not in [5]:
            return False
    return True

def has_duplicates(combination):
    return len(combination) != len(set(combination))

def generate_combination():
    while True:
        combination = random.sample(range(0, 100), 50)
        if (validate_rows_columns(combination)
            # and validate_repeated(combination)
            and validate_evens(combination)
            and validate_multi_of_three(combination)
            and validate_fibonacci(combination)
            and validate_primes(combination)):
            break
        else:
            continue

    return combination

def get_latest_game():
    response = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/lotomania')
    return response.json()

dezenas: list[int] = {}

if __name__ == "__main__":
    ultimo_concurso = get_latest_game()
    data_apuracao = ultimo_concurso['dataApuracao']
    dezenas = [int(i) for i in ultimo_concurso['listaDezenas']]

    print(colored(f"Data: {data_apuracao}   Dezenas: {dezenas}\n", "black", "on_blue"))

    with Loader():
        # Generate and print valid combinations
        valid_combination = sorted(generate_combination())

        print(valid_combination)
        print(f"Repeated: {sum(1 for x in valid_combination if x in dezenas)}")
        print(f"Multi of three: {sum(1 for x in valid_combination if x in multi_of_three)}")
        print(f"Fibonaccis: {sum(1 for x in valid_combination if x in fibonaccis)}")
        print(f"Primes: {sum(1 for x in valid_combination if x in primes)}")