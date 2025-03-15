import os
import itertools
import random
import requests
import argparse
import pandas as pd
from threading import Thread
from time import sleep
from termcolor import colored
from datetime import date

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
        print(f"\r\n{self.end}", flush=True)

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

def validate_edges(combination):
    return (combination[0] in [1, 2] and combination[-1] in [24, 25])

def validate_repeated_game(combination):
    return combination not in sorteios

def download_games():
    url = "https://asloterias.com.br/download_excel.php"  # Exemplo, troque pela URL correta

    payload = {
        "l": "lf",  # Loteria: Lotofácil
        "t": "t",   # Tipo do arquivo (tabela)
        "o": "c",   # Ordenação (crescente)
        "f1": "",   # Filtros opcionais (exemplo: data inicial)
        "f2": ""    # Filtros opcionais (exemplo: data final)
    }

    # Nome do arquivo para salvar
    file_contests = "sorteios_lotofacil.xlsx"

    # Fazer o download do arquivo
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        with open(file_contests, "wb") as f:
            f.write(response.content)
        print("✅ Arquivo baixado com sucesso!")
    else:
        print("❌ Erro ao baixar o arquivo.")


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
    number_combinations = filter(validate_edges, number_combinations)
    number_combinations = filter(validate_repeated_game, number_combinations)

    return number_combinations

def get_latest_game():
    response = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil')
    return response.json()

dezenas: list[int] = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count')
    parser.add_argument('-m', '--manual', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    today = date.today().strftime("%Y%m%d")

    file_path = os.path.expanduser(f'~/Documents/lotofacil/jogos_{today}.txt')

    download_games()

    df = pd.read_excel("sorteios_lotofacil.xlsx", skiprows=6)

    df_dezenas = df.iloc[:, 2:18]  # Como pandas começa em 0, C=2 e Q=17

    sorteios = [set(row) for row in df_dezenas.to_numpy()]

    if args.manual:
        while True:
            try:
                latest_game = sorted([int(item) for item in input("Dezenas do último sorteio : ").split()])
                if len(latest_game) != 15 or has_duplicates(latest_game) or min(latest_game) < 1 or max(latest_game) > 25:
                    raise
                else:
                    break
            except Exception:
                print("Jogo inválido!")
            
        dezenas = latest_game
    else:
        ultimo_concurso = get_latest_game()
        data_apuracao = ultimo_concurso['dataApuracao']
        proximo_concurso = ultimo_concurso['numeroConcursoProximo']
        dezenas = [int(i) for i in ultimo_concurso['listaDezenas']]

        print(colored(f"Data: {data_apuracao}   Dezenas: {dezenas}\n", "black", "on_blue"))

    with Loader():
        # Generate and print valid combinations
        valid_combinations = list(generate_number_combinations())

        count = int(args.count) if args.count else 20

        combinations = random.sample(valid_combinations, count)

        with open(file_path, "a") as file:
            for combination in combinations:
                text = f"{' '.join(str(x) for x in combination)}\r\n"
                file.write(text)
                # print(text, flush=True, end="\n\n")
        
        os.startfile(file_path)