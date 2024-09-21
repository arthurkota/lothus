import os
import itertools
import random
import requests
from threading import Thread
from time import sleep
from termcolor import colored

os.system('color')

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
    return 8 <= sum(1 for num in combination if num in dezenas) <= 10

def validate_sum(combination):
    return 170 <= sum(combination) <= 220

def validate_evens(combination):
    return 6 <= sum(1 for num in combination if num % 2 == 0) <= 8

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def validate_primes(combination):
    return 4 <= sum(1 for num in combination if is_prime(num)) <= 7

def validate_multi_of_three(combination):
    return 4 <= sum(1 for num in combination if num % 3 == 0) <= 6

def is_fibonacci(n):
    a, b = 0, 1
    while b < n:
        a, b = b, a + b
    return b == n

def validate_fibonacci(combination):
    return 3 <= sum(1 for num in combination if is_fibonacci(num)) <= 5

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
    matrix = [[0] * 5 for _ in range(5)]
    for i, num in enumerate(range(1, 26)):
        matrix[i // 5][i % 5] = num
    for row in matrix:
        if sum(1 for num in row if num in combination) in [0,5]:
            return False
    for col in range(5):
        if sum(1 for row in matrix if row[col] in combination) in [0,5]:
            return False
    return True

def validate_jumps(combination):
    for i in range(len(combination) - 1):
        if combination[i + 1] - combination[i] > 3:
            return False
    return True

def has_duplicates(combination):
    return len(combination) != len(set(combination))

def generate_number_combinations():
    # Generate all combinations of 15 numbers between 1 and 25
    number_combinations = itertools.combinations(range(1, 26), 15)

    number_combinations = filter(validate_repeated, number_combinations)
    number_combinations = filter(validate_sum, number_combinations)
    number_combinations = filter(validate_evens, number_combinations)
    number_combinations = filter(validate_primes, number_combinations)
    number_combinations = filter(validate_multi_of_three, number_combinations)
    number_combinations = filter(validate_fibonacci, number_combinations)
    number_combinations = filter(validate_consecutive_numbers, number_combinations)
    number_combinations = filter(validate_rows_columns, number_combinations)
    number_combinations = filter(validate_jumps, number_combinations)

    return number_combinations

def get_latest_game():
    response = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil')
    return response.json()

dezenas: list[int] = {}

if __name__ == "__main__":
    ultimo_concurso = get_latest_game()
    data_apuracao = ultimo_concurso['dataApuracao']
    dezenas = [int(i) for i in ultimo_concurso['listaDezenas']]

    print(colored(f"Data: {data_apuracao}   Dezenas: {dezenas}\n", "black", "on_blue"))

    # while True:
    #     try:
    #         latest_game = sorted([int(item) for item in input("Dezenas do último sorteio : ").split()])
    #         if len(latest_game) != 15 or has_duplicates(latest_game) or min(latest_game) < 1 or max(latest_game) > 25:
    #             raise
    #         else:
    #             break
    #     except Exception:
    #         print("Jogo inválido!")

    with Loader():
        # Generate and print valid combinations
        valid_combinations = list(generate_number_combinations())

        combinations = random.sample(valid_combinations, 20)

        num = 1
        for combination in random.sample(valid_combinations, 20):
           text = f"\rJogo {num}: {' - '.join(str(x) for x in combination)}"
           if num % 2 == 0:
               print(text, flush=True, end="\n\n")
           else:
               print(colored(text, "black", "on_white"), flush=True, end="\n\n")
           num+=1