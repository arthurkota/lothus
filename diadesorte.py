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
    return 1 <= sum(1 for num in combination if num in dezenas) <= 2

def validate_sum(combination):
    return 79 <= sum(combination) <= 145

def validate_evens(combination):
    return 2 <= sum(1 for num in combination if num % 2 == 0) <= 4

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def validate_primes(combination):
    return 1 <= sum(1 for num in combination if is_prime(num)) <= 4

def validate_multi_of_three(combination):
    return 1 <= sum(1 for num in combination if num % 3 == 0) <= 3

def is_fibonacci(n):
    a, b = 0, 1
    while b < n:
        a, b = b, a + b
    return b == n

def validate_fibonacci(combination):
    return 1 <= sum(1 for num in combination if is_fibonacci(num)) <= 2

def has_duplicates(combination):
    return len(combination) != len(set(combination))

def generate_number_combinations():
    # Generate all combinations of 15 numbers between 1 and 25
    number_combinations = itertools.combinations(range(1, 32), 7)

    number_combinations = filter(validate_repeated, number_combinations)
    number_combinations = filter(validate_sum, number_combinations)
    number_combinations = filter(validate_evens, number_combinations)
    number_combinations = filter(validate_primes, number_combinations)
    number_combinations = filter(validate_multi_of_three, number_combinations)
    number_combinations = filter(validate_fibonacci, number_combinations)

    return number_combinations

def get_latest_game():
    response = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte')
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

        print(len(valid_combinations))

        combinations = random.sample(valid_combinations, 20)

        num = 1
        for combination in random.sample(valid_combinations, 20):
           text = f"\rJogo {num}: {' - '.join(str(x) for x in combination)}"
           if num % 2 == 0:
               print(text, flush=True, end="\n\n")
           else:
               print(colored(text, "black", "on_white"), flush=True, end="\n\n")
           num+=1