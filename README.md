# Projeto de Algoritmo Genético para Solução do Problema de Escalonamento de Enfermeiros (PEE) utilizando NSPLib

[![Badge de Licença](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Badge de Status do Projeto](https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue.svg)](https://github.com/seu-usuario/seu-projeto)

Este projeto foi desenvolvido para mostrar de forma simples a utilização de um algoritmo genético para solucionar o problema de escalonamento de enfermeiros utilizando as instâncias disponibilizadas pela biblioteca de instâncias para esse problema, o NSPLib (Nurse Scheduling Problem Library). A solução busca utilizar conceitos básicos do algoritmo genético, como por exemplo métoo de seleção de pais, crossover, mutação, entre outras propriedades próprias dessa heurística.

## Índice

1. [Estrutura do Projeto](#estrutura-do-projeto)
2. [Instalação](#instalação)
    - [Pré-requisitos](#pré-requisitos)
    - [Passos para Instalação](#passos-para-instalação)
4. [Estrutura dos Arquivos NSPLib](##estrutura-dos-arquivos-nsplib)
5. [Parâmetros do Algoritmo Genético](#parâmetros-do-algoritmo-genético)
6. [Restrições](#restrições)
7. [Licença](#licença)

## Estrutura do Projeto

- **Pastas**:
  - `.idea/`
  - `gen/` (contém oito arquivos com configurações de restrições diferentes)
  - `results/` (contém os resultados das execuções do algoritmo)
  - `nsp/` (contém as intâncias de 25 enfermeiros)

- **Arquivos**:
  - `LICENSE`
  - `main.py` (arquivo principal do projeto)
  - `ReadResult.py` (arquivo para ler e processar resultados)
  - `MANIFEST.in`
  - `pyproject.toml`
  - `README.md`
  - `requirements.txt` (lista de bibliotecas necessárias)


## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Passos para Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/Grogenski/GAforNSPLib
   cd GAforNSPLib
   ```

2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   ```

3. Ative o ambiente virtual:

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. Instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```

## Estrutura dos Arquivos NSPLib

A NSPLib é composta de um conjunto de arquivos de instanciações do PEE. Na biblioteca existem dois tipos de arquivos, que são utilizados de forma conjunta para definir de forma completa todas as características do problema. O primeiro deles contém a demanda para cada dia da escala a ser elaborada e o valor da preferência de cada enfermeiro para cada turno em todo o período. Os valores das preferências dos enfermeiros são números inteiros de 1 a 4. O segundo tipo de arquivo, também chamado de caso de aplicação, define as restrições flexíveis do problema. No total são 16 casos, sendo os casos de 1 a 8 para as escalas de 7 dias e os casos de 9 a 16 para as escalas de 28 dias.

Os arquivos que contêm os dados referentes à demanda do problema permitem a geração de escalas semanais ou mensais. Para as escalas de 7 dias, o problema de escalonamento envolve quatro quantidades diferentes de enfermeiros, sendo elas 25, 50, 75 e 100. Para cada uma dessas quantidades de enfermeiros existem 7.290 arquivos. Cada um desses arquivos pode ser aplicado aos 8 tipos de casos de aplicação existentes para as escalas de 7 dias. Portanto, tem-se um total de 233.280 diferentes combinações para o problema envolvendo a criação de escalas de trabalho semanais.
Para as escalas de 28 dias, o problema de escalonamento envolve apenas duas quantidades de enfermeiros, 30 e 60. Cada uma dessas quantidades de enfermeiros dispõem de 960 arquivos diferentes que também podem ser aplicados a cada um dos 8 casos de aplicação existentes. Conclui-se que existem um total de 15.360 combinações para o problema de escala mensal. De modo geral, a biblioteca NSPLib consta com um total de 248.640 combinações diferentes para resolução do problema de escalonamento de enfermerios.

### Parâmetros do Algoritmo Genético

Os parâmetros do algoritmo genético foram escolhidos empiricamente com base em experimentos preliminares para garantir um equilíbrio entre a diversidade da população e a exploração do espaço de busca. Os parâmetros utilizados foram:

- Tamanho da população: Este parâmetro controla o número de soluções candidatas (escalas de enfermagem) mantidas e evoluídas em cada geração do algoritmo.
- Número de gerações: Define o número total de iterações que o algoritmo executa para melhorar as soluções ao longo do tempo.
- Taxa de mutação: Determina a probabilidade de um gene (turno de um enfermeiro em um determinado dia) ser modificado aleatoriamente durante a geração de novos indivíduos, introduzindo diversidade na população.

Esses parâmetros foram ajustados para equilibrar a intensidade computacional do algoritmo com a capacidade de explorar soluções de qualidade para o Problema de Escalonamento de Enfermeiros, levando em consideração a complexidade das instâncias utilizadas e as restrições do problema.

## Restrições
 
As restrições flexíveis são divididas em três categorias: regras ou regime interno do local de trabalho, preferências dos enfermeiros pelos turnos e exigência de cobertura mínima (para satisfazer a demanda de carga de trabalho de cada dia). As regras ou regime interno do local de trabalho compreendem 20 restrições, a saber: 
- Imposição de um mínimo de dias trabalhados no período (RF1); 
- Imposição de um máximo de dias trabalhados no período (RF2); 
- Imposição de um mínimo de atribuições consecutivas (RF3); 
- Imposição de um máximo de atribuições consecutivas (RF4); 
- Imposição de um mínimo de atribuições de um mesmo tipo de turno, sendo elas manhã, tarde, noite e folga (RF5, RF6, RF7 e RF8, respectivamente); 
- Imposição de um máximo de atribuições de um mesmo tipo de turno, sendo elas manhã, tarde, noite e folga (RF9, RF10, RF11 e RF12, respectivamente); 
- Imposição de um mínimo de atribuições consecutivas de um mesmo tipo de turno, sendo elas manhã, tarde, noite e folga (RF13, RF14, RF15 e RF16, respectivamente); 
- Imposição de um máximo de atribuições consecutivas de um mesmo tipo de turno, sendo elas manhã, tarde, noite e folga (RF17, RF18, RF19 e RF20, respectivamente); 

As restrições de preferências dos enfermeiros são: 
- Consideração da preferência de um enfermeiro por trabalhar em um determinado turno em um dia específico (RF21); 
- Consideração da preferência de um enfermeiro por folgar em um determinado dia (RF22).

As restrições de cobertura, RF23 e RF24, garantem a demanda mínima de enfermeiros necessária para cada turno, evitando a alocação excessiva.
As restrições rígidas são definidas por legislações trabalhistas, a saber: 
- Proibição de um turno da tarde ser seguido por um turno da manhã (RR1); 
- Proibição de um turno da noite ser seguido por um turno da manhã (RR2); 
- Proibição de um turno da noite ser seguido por um turno da tarde (RR3).

## Licença

Este projeto está licenciado sob os termos da licença MIT. Para mais detalhes, veja o arquivo `LICENSE`.

---

Para quaisquer dúvidas ou problemas, por favor, entre em contato com lucas.grogenskimeloca@gmail.com.
