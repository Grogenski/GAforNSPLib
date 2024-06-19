import numpy as np
import random
import time
from datetime import datetime
import pytz


def gen_import(gen_file):
    with open(gen_file, 'r') as file:
        lines = file.readlines()

    # Number of Assignments (min and max)
    num_assignments = lines[2].strip().split('\t')
    num_assignments_min = int(num_assignments[0])
    num_assignments_max = int(num_assignments[1])

    # Consecutive Working Shifts (min and max)
    consecutive_assignments = lines[4].strip().split('\t')
    consecutive_assignments_min = int(consecutive_assignments[0])
    consecutive_assignments_max = int(consecutive_assignments[1])

    # Consecutive same working shifts
    # Manhã
    consecutive_early_shifts = lines[7].strip().split('\t')
    consecutive_early_shifts_min = int(consecutive_early_shifts[0])
    consecutive_early_shifts_max = int(consecutive_early_shifts[1])
    # Tarde
    consecutive_day_shifts = lines[8].strip().split('\t')
    consecutive_day_shifts_min = int(consecutive_day_shifts[0])
    consecutive_day_shifts_max = int(consecutive_day_shifts[1])
    # Noite
    consecutive_night_shifts = lines[9].strip().split('\t')
    consecutive_night_shifts_min = int(consecutive_night_shifts[0])
    consecutive_night_shifts_max = int(consecutive_night_shifts[1])
    # Folga
    consecutive_dayoff_shifts = lines[10].strip().split('\t')
    consecutive_dayoff_shifts_min = int(consecutive_dayoff_shifts[0])
    consecutive_dayoff_shifts_max = int(consecutive_dayoff_shifts[1])

    # Number of assignements per shift
    # Manhã
    num_early_assignments = lines[7].strip().split('\t')
    num_early_assignments_min = int(num_early_assignments[2])
    num_early_assignments_max = int(num_early_assignments[3])
    # Tarde
    num_day_assignments = lines[8].strip().split('\t')
    num_day_assignments_min = int(num_day_assignments[2])
    num_day_assignments_max = int(num_day_assignments[3])
    # Noite
    num_night_assignments = lines[9].strip().split('\t')
    num_night_assignments_min = int(num_night_assignments[2])
    num_night_assignments_max = int(num_night_assignments[3])
    # Folga
    num_dayoff_assignments = lines[10].strip().split('\t')
    num_dayoff_assignments_min = int(num_dayoff_assignments[2])
    num_dayoff_assignments_max = int(num_dayoff_assignments[3])

    staff_infos = {
        'num_assignments_min': num_assignments_min,
        'num_assignments_max': num_assignments_max,
        'consecutive_assignments_min': consecutive_assignments_min,
        'consecutive_assignments_max': consecutive_assignments_max,
        'consecutive_early_shifts_min': consecutive_early_shifts_min,
        'consecutive_early_shifts_max': consecutive_early_shifts_max,
        'consecutive_day_shifts_min': consecutive_day_shifts_min,
        'consecutive_day_shifts_max': consecutive_day_shifts_max,
        'consecutive_night_shifts_min': consecutive_night_shifts_min,
        'consecutive_night_shifts_max': consecutive_night_shifts_max,
        'consecutive_dayoff_shifts_min': consecutive_dayoff_shifts_min,
        'consecutive_dayoff_shifts_max': consecutive_dayoff_shifts_max,
        'num_early_assignments_min': num_early_assignments_min,
        'num_early_assignments_max': num_early_assignments_max,
        'num_day_assignments_min': num_day_assignments_min,
        'num_day_assignments_max': num_day_assignments_max,
        'num_night_assignments_min': num_night_assignments_min,
        'num_night_assignments_max': num_night_assignments_max,
        'num_dayoff_assignments_min': num_dayoff_assignments_min,
        'num_dayoff_assignments_max': num_dayoff_assignments_max
    }

    return staff_infos

def nsp_import(nsp_file):
    with open(nsp_file, 'r') as file:
        lines = file.readlines()

    # Ler os parâmetros da primeira linha
    params = lines[0].strip().split('\t')
    num_employees = int(params[0])
    num_days = int(params[1])
    num_turnos = int(params[2])

    matriz_demanda = []
    matriz_geral = []
    matriz_preferencia = []
    matriz_folga = []

    for i in range(num_days):
        lin_dem = [int(x) for x in lines[2 + i].strip().split()]
        matriz_demanda.append(lin_dem[:-1])

    for i in range(num_employees):
        lin_pref = [int(x) for x in lines[3 + num_days + i].strip().split()]
        matriz_geral.append(lin_pref)

    for lista in matriz_geral:
        preferencia = []
        folga = []
        for pos, num in enumerate(lista):
            if (pos + 1) % num_turnos == 0:
                folga.append(num)
            else:
                preferencia.append(num)
        matriz_preferencia.append(preferencia)
        matriz_folga.append(folga)

    return num_employees, num_days, num_turnos, matriz_demanda, matriz_preferencia, matriz_folga


def data_converter(matriz_preferencia, num_enfermeiros, num_turnos, num_dias, turnos):
    # Lista para armazenar as tuplas
    resultado = []

    # Iterar sobre a matriz e gerar as tuplas
    for enfermeiro_id in range(num_enfermeiros):
        for dia in range(num_dias):
            if len(turnos.items()) == 1:
                preferencia = matriz_preferencia[enfermeiro_id][dia]
                resultado.append((enfermeiro_id, dia, preferencia))

            else:
                for turno_nome, turno_id in turnos.items():
                    #turno = turnos[turno_id]
                    preferencia = matriz_preferencia[enfermeiro_id][dia * num_turnos + turno_id]
                    resultado.append((enfermeiro_id, dia, turno_nome, preferencia))

    return resultado


def data_converter_demanda(matriz_demanda, num_dias, turnos, weight_under=100, weight_over=25):
    # Lista para armazenar as tuplas
    resultado_demanda = []

    # Iterar sobre a matriz e gerar as tuplas
    for dia in range(num_dias):
        for turno_nome, turno_id in turnos.items():
            requisito = matriz_demanda[dia][turno_id]
            resultado_demanda.append((dia, turno_nome, requisito, weight_under, weight_over))

    return resultado_demanda


class Schedule:
    def __init__(self, schedule_matrix, staff_info, shifts):
        self.schedule_matrix = schedule_matrix
        self.staff_info = staff_info
        self.shifts = shifts
        self.fitness, self.total_pref, self.penalties = self.evaluate_fitness()


    def evaluate_fitness(self):
        num_days, num_employees = self.schedule_matrix.shape

        total_pref = 0
        fitness = 0
        # Matriz para contabilizar o número de restrições violadas (24 restrições flexíveis e 3 restrições rígidas)
        penalties = np.zeros((num_employees, 27), dtype=int)

        # Restrição 1: Mínimo de turnos
        for emp_id in range(num_employees):
            min_shifts = self.staff_info['num_assignments_min']
            shifts_worked = np.sum(self.schedule_matrix[:, emp_id] != -1)
            if shifts_worked < min_shifts:
                penalties[emp_id][0] += 1
                fitness += (min_shifts - shifts_worked) * 100  # Penalidade por exceder o número mínimo de turnos

        # Restrição 2: Máximo de turnos
        for emp_id in range(num_employees):
            max_shifts = self.staff_info['num_assignments_max']
            shifts_worked = np.sum(self.schedule_matrix[:, emp_id] != -1)
            if shifts_worked > max_shifts:
                penalties[emp_id][1] += 1
                fitness += (shifts_worked - max_shifts) * 100  # Penalidade por exceder o número máximo de turnos

        # Restrição 3: Mínimo de turnos consecutivos
        for emp_id in range(num_employees):
            min_consecutive_shifts = self.staff_info['consecutive_assignments_min']
            consecutive_shifts = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] != -1:
                    consecutive_shifts += 1
                    if consecutive_shifts < min_consecutive_shifts:
                        penalties[emp_id][2] += 1
                        fitness += (min_consecutive_shifts - consecutive_shifts) * 100  # Penalidade por não atingir o número mínimo de turnos consecutivos
                else:
                    consecutive_shifts = 0

        # Restrição 4: Máximo de turnos consecutivos
        for emp_id in range(num_employees):
            max_consecutive_shifts = self.staff_info['consecutive_assignments_max']
            consecutive_shifts = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] != -1:
                    consecutive_shifts += 1
                    if consecutive_shifts > max_consecutive_shifts:
                        penalties[emp_id][3] += 1
                        fitness += (consecutive_shifts - max_consecutive_shifts) * 100  # Penalidade por exceder o número máximo de turnos consecutivos
                else:
                    consecutive_shifts = 0

        # Restrição 5: Mínimo de turnos da manhã consecutivos
        for emp_id in range(num_employees):
            consecutive_early_shifts_min = self.staff_info['consecutive_early_shifts_min']
            consecutive_early_shifts = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] == 0:
                    consecutive_early_shifts += 1
                    if consecutive_early_shifts < consecutive_early_shifts_min:
                        penalties[emp_id][4] += 1
                        fitness += (consecutive_early_shifts_min - consecutive_early_shifts) * 100  # Penalidade por não atingir o número mínimo de dias de folga consecutivos
                else:
                    consecutive_early_shifts = 0

        # Restrição 6: Máximo de turnos da manhã consecutivos
        for emp_id in range(num_employees):
            consecutive_early_shifts_max = self.staff_info['consecutive_early_shifts_max']
            consecutive_early_shifts = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] == 0:
                    consecutive_early_shifts += 1
                    if consecutive_early_shifts > consecutive_early_shifts_max:
                        penalties[emp_id][5] += 1
                        fitness += (consecutive_early_shifts - consecutive_early_shifts_max) * 100  # Penalidade por não atingir o número mínimo de dias de folga consecutivos
                else:
                    consecutive_early_shifts = 0

        # Restrição 7: Mínimo de turnos da tarde consecutivos
        for emp_id in range(num_employees):
            consecutive_day_shifts_min = self.staff_info['consecutive_day_shifts_min']
            consecutive_day_shifts = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] == 1:
                    consecutive_day_shifts += 1
                    if consecutive_day_shifts < consecutive_day_shifts_min:
                        penalties[emp_id][6] += 1
                        fitness += (consecutive_day_shifts_min - consecutive_day_shifts) * 100  # Penalidade por não atingir o número mínimo de turnos consecutivos
                else:
                    consecutive_day_shifts = 0

        # Restrição 8: Máximo de turnos da tarde consecutivos
        for emp_id in range(num_employees):
            consecutive_day_shifts_max = self.staff_info['consecutive_day_shifts_max']
            consecutive_day_shifts = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] == 1:
                    consecutive_day_shifts += 1
                    if consecutive_day_shifts > consecutive_day_shifts_max:
                        penalties[emp_id][7] += 1
                        fitness += (consecutive_day_shifts - consecutive_day_shifts_max) * 100  # Penalidade por não atingir o número mínimo de turnos consecutivos
                else:
                    consecutive_day_shifts = 0

        # Restrição 9: Mínimo de turnos da noite consecutivos
        for emp_id in range(num_employees):
            consecutive_night_shifts_min = self.staff_info['consecutive_night_shifts_min']
            consecutive_night_shifts = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] == 2:
                    consecutive_night_shifts += 1
                    if consecutive_night_shifts < consecutive_night_shifts_min:
                        penalties[emp_id][8] += 1
                        fitness += (consecutive_night_shifts_min - consecutive_night_shifts) * 100  # Penalidade por não atingir o número mínimo de turnos consecutivos
                else:
                    consecutive_night_shifts = 0

        # Restrição 10: Máximo de turnos da noite consecutivos
        for emp_id in range(num_employees):
            consecutive_night_shifts_max = self.staff_info['consecutive_night_shifts_max']
            consecutive_night_shifts = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] == 2:
                    consecutive_night_shifts += 1
                    if consecutive_night_shifts > consecutive_night_shifts_max:
                        penalties[emp_id][9] += 1
                        fitness += (consecutive_night_shifts - consecutive_night_shifts_max) * 100  # Penalidade por não atingir o número mínimo de turnos consecutivos
                else:
                    consecutive_night_shifts = 0

        # Restrição 11: Mínimo de dias de folga consecutivos
        for emp_id in range(num_employees):
            consecutive_dayoff_shifts_min = self.staff_info['consecutive_dayoff_shifts_min']
            consecutive_days_off = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] == -1:
                    consecutive_days_off += 1
                    if consecutive_days_off < consecutive_dayoff_shifts_min:
                        penalties[emp_id][10] += 1
                        fitness += (consecutive_dayoff_shifts_min - consecutive_days_off) * 100  # Penalidade por não atingir o número mínimo de dias de folga consecutivos
                else:
                    consecutive_days_off = 0

        # Restrição 12: Máximo de dias de folga consecutivos
        for emp_id in range(num_employees):
            consecutive_dayoff_shifts_max = self.staff_info['consecutive_dayoff_shifts_max']
            consecutive_days_off = 0
            for day in range(num_days):
                if self.schedule_matrix[day, emp_id] == -1:
                    consecutive_days_off += 1
                    if consecutive_days_off > consecutive_dayoff_shifts_max:
                        penalties[emp_id][11] += 1
                        fitness += (consecutive_days_off - consecutive_dayoff_shifts_max) * 100  # Penalidade por não atingir o número mínimo de dias de folga consecutivos
                else:
                    consecutive_days_off = 0

        # Restrição 13: Mínimo de turnos da manhã
        for emp_id in range(num_employees):
            min_early_shifts = self.staff_info['num_early_assignments_min']
            early_shifts_worked = np.sum(self.schedule_matrix[:, emp_id] == 0)
            if early_shifts_worked < min_early_shifts:
                penalties[emp_id][12] += 1
                fitness += (min_early_shifts - early_shifts_worked) * 100  # Penalidade por exceder o número mínimo de turnos da manhã

        # Restrição 14: Máximo de turnos da manhã
        for emp_id in range(num_employees):
            max_early_shifts = self.staff_info['num_early_assignments_max']
            early_shifts_worked = np.sum(self.schedule_matrix[:, emp_id] == 0)
            if early_shifts_worked > max_early_shifts:
                penalties[emp_id][13] += 1
                fitness += (early_shifts_worked - max_early_shifts) * 100  # Penalidade por exceder o número máximo de turnos da manhã

        # Restrição 15: Mínimo de turnos da tarde
        for emp_id in range(num_employees):
            min_day_shifts = self.staff_info['num_day_assignments_min']
            day_shifts_worked = np.sum(self.schedule_matrix[:, emp_id] == 0)
            if day_shifts_worked < min_day_shifts:
                penalties[emp_id][14] += 1
                fitness += (min_day_shifts - day_shifts_worked) * 100  # Penalidade por exceder o número mínimo de turnos da tarde

        # Restrição 16: Máximo de turnos da tarde
        for emp_id in range(num_employees):
            max_day_shifts = self.staff_info['num_day_assignments_max']
            day_shifts_worked = np.sum(self.schedule_matrix[:, emp_id] == 0)
            if day_shifts_worked > max_day_shifts:
                penalties[emp_id][15] += 1
                fitness += (day_shifts_worked - max_day_shifts) * 100  # Penalidade por exceder o número máximo de turnos da tarde

        # Restrição 17: Mínimo de turnos da noite
        for emp_id in range(num_employees):
            min_night_shifts = self.staff_info['num_night_assignments_min']
            night_shifts_worked = np.sum(self.schedule_matrix[:, emp_id] == 0)
            if night_shifts_worked < min_night_shifts:
                penalties[emp_id][16] += 1
                fitness += (min_night_shifts - night_shifts_worked) * 100  # Penalidade por exceder o número mínimo de turnos da noite

        # Restrição 18: Máximo de turnos da noite
        for emp_id in range(num_employees):
            max_night_shifts = self.staff_info['num_night_assignments_max']
            night_shifts_worked = np.sum(self.schedule_matrix[:, emp_id] == 0)
            if night_shifts_worked > max_night_shifts:
                penalties[emp_id][17] += 1
                fitness += (night_shifts_worked - max_night_shifts) * 100  # Penalidade por exceder o número máximo de turnos da noite

        # Restrição 19: Mínimo de folgas
        for emp_id in range(num_employees):
            min_day_off_shifts = self.staff_info['num_dayoff_assignments_min']
            day_off = np.sum(self.schedule_matrix[:, emp_id] == 0)
            if day_off < min_day_off_shifts:
                penalties[emp_id][18] += 1
                fitness += (min_day_off_shifts - day_off) * 100  # Penalidade por exceder o número mínimo de folgas

        # Restrição 20: Máximo de folgas
        for emp_id in range(num_employees):
            max_day_off_shifts = self.staff_info['num_dayoff_assignments_max']
            day_off = np.sum(self.schedule_matrix[:, emp_id] == 0)
            if day_off > max_day_off_shifts:
                penalties[emp_id][19] += 1
                fitness += (day_off - max_day_off_shifts) * 100  # Penalidade por exceder o número máximo de folgas

        # Restrição 21: Pedidos de turnos específicos
        for request in shift_on_requests:
            emp_id, day, shift_id, pref = request
            #weight = (1/pref)*100
            weight = (5 - pref) * 25
            if self.schedule_matrix[day, emp_id] != self.shifts[shift_id]:
                penalties[emp_id][20] += 1
                fitness += weight  # Penalidade por não atender o pedido

        # Restrição 22: Pedidos de folga de turnos específicos
        for request in shift_off_requests:
            emp_id, day, pref = request
            #weight = (1/pref)*100
            weight = (5 - pref) * 25
            if self.schedule_matrix[day, emp_id] == -1:
                if weight <= 25:
                    weight = 0
                else:
                    weight = weight
                    penalties[emp_id][21] += 1
                fitness += weight  # Penalidade por não conceder folga

        # Restrição 23: Cobertura de turnos
        for cover in cover_requirements:
            day, shift_id, requirement, weight_under, weight_over = cover
            actual = np.sum(self.schedule_matrix[day] == self.shifts[shift_id])
            if actual < requirement:
                penalties[emp_id][22] += 1
                fitness += (requirement - actual) * weight_under  # Penalidade por falta
            if actual > requirement:
                penalties[emp_id][23] += 1
                fitness += (actual - requirement) * weight_over  # Penalidade por excesso

        # Restrição 24: Proibição de um turno da tarde ser sucedido por um turno da manhã,
        # um turno da noite ser sucedido por um turno da manhã ou por um turno da tarde.
        for emp_id in range(num_employees):
            for day in range(num_days - 1):
                if self.schedule_matrix[day, emp_id] == 1:
                    if self.schedule_matrix[day+1, emp_id] == 0:
                        penalties[emp_id][24] += 1
                        fitness += 1000 # Penalidade por infringir uma restrição rígida
                if self.schedule_matrix[day, emp_id] == 2:
                    if self.schedule_matrix[day+1, emp_id] == 0:
                        penalties[emp_id][25] += 1
                        fitness += 1000 # Penalidade por infringir uma restrição rígida
                if self.schedule_matrix[day, emp_id] == 2:
                    if self.schedule_matrix[day+1, emp_id] == 1:
                        penalties[emp_id][26] += 1
                        fitness += 1000 # Penalidade por infringir uma restrição rígida

        # Soma das preferências
        for request in shift_on_requests:
            emp_id, day, shift_id, pref = request
            if self.schedule_matrix[day, emp_id] == self.shifts[shift_id]:
                total_pref += pref
        for request in shift_off_requests:
            emp_id, day, pref = request
            if self.schedule_matrix[day, emp_id] == -1:
                total_pref += pref

        return fitness, total_pref, penalties

    def __str__(self):
        return f"{self.fitness}, {self.total_pref}, {self.penalties}"

    def __repr__(self):
        return self.__str__()


def improved_select_parents_by_tournament(population, tournament_size=2):
    selected_parents = []
    population = sorted(population, key=lambda x: x[0].fitness)
    tournament_population = population
    # Realiza o torneio para selecionar os pais
    for _ in range(2):  # Dois pais serão selecionados
        # Escolhe aleatoriamente um conjunto de indivíduos para o torneio
        tournament_contestants = random.sample(tournament_population[:len(tournament_population)//2], tournament_size)
        # Retira os competidores selecionados para não serem novamente selecionados
        for competitor in tournament_contestants:
            tournament_population.remove(competitor)
        # Encontra o vencedor do torneio (indivíduo com melhor fitness)
        winner = min(tournament_contestants, key=lambda x: x[0].fitness)
        # Adiciona o vencedor à lista de pais selecionados
        selected_parents.append(winner)

    return selected_parents


def crossover(parent1, parent2):
    crossover_point = random.randint(1, parent1[0].schedule_matrix.shape[0] - 1)
    child1_matrix = np.vstack((parent1[0].schedule_matrix[:crossover_point], parent2[0].schedule_matrix[crossover_point:]))
    child2_matrix = np.vstack((parent2[0].schedule_matrix[:crossover_point], parent1[0].schedule_matrix[crossover_point:]))
    return Schedule(child1_matrix, parent1[0].staff_info, parent1[0].shifts), Schedule(child2_matrix, parent1[0].staff_info, parent1[0].shifts)


def mutate(schedule, mutation_rate=1):
    num_days, num_employees = schedule.schedule_matrix.shape
    for i in range(num_days):
        for j in range(num_employees):
            if random.random() < mutation_rate:
                mutacao = random.choice(list(schedule.shifts.values()) + [-1])
                schedule.schedule_matrix[i][j] = mutacao
    schedule.fitness, schedule.total_pref, schedule.penalties = schedule.evaluate_fitness()


def genetic_algorithm(pop_size, num_generations, mutation_rate):
    # Inicializa a população com indivíduos aleatórios
    population = [[Schedule(np.random.choice(list(shifts.values()) + [-1], size=(num_days, num_employees)), staff_info, shifts)] for _ in range(pop_size)]

    for generation in range(num_generations):
        new_population = []

        while len(new_population) < pop_size:
            parent1, parent2 = improved_select_parents_by_tournament(population)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1, mutation_rate)
            mutate(child2, mutation_rate)
            new_population.extend([[child1], [child2]])

        population = sorted(new_population, key=lambda x: x[0].fitness)[:pop_size]
        best_schedule = population[0]
    return best_schedule


# Cria uma seed de acordo com o horário que o algoritmo é executado
seed = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d%m%Y%H%M%S')
random.seed(seed)
with open(f"results/{seed}.txt", "a") as arquivo:
    arquivo.write(f"semente {seed}\n")

# Criar um txt para armazenar resultados
with open(f"results/{seed}.txt", "a") as arquivo:
    arquivo.write(f"gen,intancia,fitness,total_pref,tempo\n")

# Rodar para n arquivos gen
for gen in [2]:
    file_gen = f'{gen + 1}.gen'
    gen_path = f'gen/{file_gen}'
    print(f'==============================Gen: {file_gen}==============================')

    # Determinando XX% de das 7289 instâncias
    quantidade_selecionada = int(0.3 * 7290)

    # Obtendo uma amostra aleatória de XX% dos números
    amostra = sorted(random.sample(range(7290), quantidade_selecionada))

    # Rodar para n arquivos nsp
    for nsp in amostra:
        nsp_file = f'{nsp + 1}.nsp'
        nsp_path = f'nsp/{nsp_file}'
        print(f'============================Intância: {nsp_file}============================')
        num_employees, num_days, num_turnos, matriz_demanda, matriz_preferencia, matriz_folga = nsp_import(nsp_path)

        # Parâmetros
        num_turnos = num_turnos - 1
        num_days = num_days
        num_employees = num_employees
        shifts = {'M': 0, 'T': 1, 'N': 2}
        shift_on_requests = data_converter(matriz_preferencia, num_employees, num_turnos, num_days, shifts)
        shift_off_requests = data_converter(matriz_folga, num_employees, 1, num_days, {'M':0})
        cover_requirements = data_converter_demanda(matriz_demanda, num_days, shifts)
        staff_info = gen_import(gen_path)

        # Parâmetros do algoritmo genético
        pop_size = 20
        num_generations = 70
        mutation_rate = 0.025

        # Início da contagem de tempo de execução (em segundos)
        start_time = time.time()

        # Resultado
        best_schedule = genetic_algorithm(pop_size, num_generations, mutation_rate)
        checkpoint = (time.time() - start_time)
        print("Best Fitness:", best_schedule[0].fitness)
        print("Best Schedule Matrix (linhas=dias, col=enfermeiros):\n", best_schedule[0].schedule_matrix)

        # Salvar resultados em txt
        with open(f"results/{seed}.txt", "a") as arquivo:
            arquivo.write(f"{gen},{nsp},{best_schedule[0].fitness},{best_schedule[0].total_pref},{checkpoint:.4f}\n")
            for linha in best_schedule[0].penalties:
                arquivo.write(" ".join(map(str, linha)) + "\n")
            arquivo.write("\n")
            for linha in best_schedule[0].schedule_matrix:
                arquivo.write(" ".join(map(str, linha)) + "\n")
            arquivo.write(f"\n")