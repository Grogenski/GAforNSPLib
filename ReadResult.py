import numpy as np

def result_import(result_file):
    with open(result_file, 'r') as file:
        lines = file.readlines()

    alllines = len(lines)
    summary = []
    results = []
    linha_atual = 1
    num_employees = 25
    ultima_linha1 = 0
    ultima_linha2 = 0

    for l in range(alllines):
        # Ler informações da segunda linha
        if (linha_atual - ultima_linha1) == 35 or linha_atual == 1:
            ultima_linha1 = linha_atual
            results_line = lines[l].strip().split(',')
            results.append(int(results_line[0]))
            results.append(int(results_line[1]))
            results.append(int(results_line[2]))
            results.append(int(results_line[3]))
            results.append(float(results_line[4]))
        if (linha_atual - ultima_linha2) == 35 or linha_atual == 2:
            ultima_linha2 = linha_atual
            matriz_violação = []
            for i in range(num_employees):
                lin_dem = [int(x) for x in lines[l + i].strip().split(' ')]
                matriz_violação.append(lin_dem[:])

            soma_colunas = np.sum(np.array(matriz_violação), axis=0)
            for y, x in enumerate(list(soma_colunas)):
                results.append(x)
            results.append(sum(soma_colunas))
            summary.append(results)
            results = []
        linha_atual += 1

    return summary


def split_list(lst, n):
    # Calcula o tamanho de cada parte
    k, m = divmod(len(lst), n)

    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def dividir_valores(lista, divisor):
  """
  Função para dividir todos os números de uma lista por um divisor.

  Argumentos:
    lista (list): A lista de números a serem divididos.
    divisor (float): O valor pelo qual dividir os elementos da lista.

  Retorno:
    list: Uma nova lista contendo os resultados da divisão.
  """
  lista_dividida = []
  for numero in lista:
    resultado_divisao = numero / divisor
    lista_dividida.append(resultado_divisao)

  return lista_dividida

def DataAnalysis(summary):
    final_flush = []
    cases = int(len(summary) / 2187)
    case_summary = split_list(summary, cases)
    for case in range(cases):
        soma_colunas = np.sum(np.array(case_summary[case]), axis=0)
        media = dividir_valores(list(soma_colunas), len(case_summary[case]))
        final_flush.append(media)
    return final_flush

summary12 = result_import("results/15062024083357.txt") # 1, 2
summary3 = result_import("results/16062024074119.txt") # 3
summary456 = result_import("results/15062024082323.txt") # 4, 5, 6
summary7 = result_import("results/16062024074044.txt") # 7
summary8 = result_import("results/16062024113247.txt") # 8

Graal = []
for summary in [summary12, summary3, summary456,  summary7,  summary8]:
    Graal.append(DataAnalysis(summary))

# Criar um txt para armazenar resultados
with open(f"results/GGK137.txt", "a") as arquivo:
    arquivo.write(f"{Graal}")
