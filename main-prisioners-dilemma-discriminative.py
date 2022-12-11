import matplotlib.pyplot as plt
import numpy as np

from CellularAutomata import CellularAutomata
from Grid2DDiscriminative import Grid2D_Periodic as Grid2D_PeriodicDiscriminative
from Grid2D import Grid2D_Periodic
from GUIDiscriminative import GUILoop

MAX_ROUNDS = 20
STRATEGIES = [
  'tit-for-tat',
  'tit-for-two-tat',
]

class PrisionersDilemma(CellularAutomata):
  COOPERATE = 0
  DEFECT = 1

  '''
  +---------------+---------------+---------------+
  |     A / B     | COOPERATE (C) |   DEFECT (D)  |
  |---------------+---------------+---------------+            
  | COOPERATE (C) |     R / R     |     P / T     |
  |---------------+---------------+---------------+
  |   DEFECT (D)  |     T / P     |     C / C     |
  +---------------+---------------+---------------+

  '''
  # PONTUAÇÕES:
  T = 5 # Se você delata (confessa) enquanto o outro colabora (fica em silêncio), você ganha pontuação máxima
  R = 3 # Se ambos colaboram (ficam em silêncio), a pena é baixa para os dois e ambos ganham alguns pontos
  C = 1 # Se os dois delatam (confessam), ambos ganham uma pena mais dura e poucos pontos 
  P = 0 # Se você colabora (fica em silêncio) mas o outro delata (confessa), você ganha a pena mais dura e, por isso, nenhum ponto

  assert T > R > C > P, "Payoff values must follow the rule: T > R > C > P"

  STRATEGY_SELECTION = 'tit-for-two-tat'

  assert STRATEGY_SELECTION in STRATEGIES, "Strategy must be one of {}".format(STRATEGIES)

  def __init__(self):
    self.m_TimeStep = 0
    self.hist_C = []
    self.hist_D = []
    self.hist_score_C = []
    self.hist_score_D = []
    self.hist_score = []
    self.hist_rounds = []
    self.rounds = 0
    self.round_results = Grid2D_Periodic(w, h)

  def initCond(self):
    for j in range(0, self.m_Grid2D.getHeight()):
      for i in range(0, self.m_Grid2D.getWidth()):
        first_row = [np.random.randint(2), np.random.randint(2), np.random.randint(2)]
        second_row = [np.random.randint(2), 0, np.random.randint(2)]
        third_row = [np.random.randint(2), np.random.randint(2), np.random.randint(2)]

        historical_first_row = [np.random.randint(2), np.random.randint(2), np.random.randint(2)]
        historical_second_row = [np.random.randint(2), 0, np.random.randint(2)]
        historical_third_row = [np.random.randint(2), np.random.randint(2), np.random.randint(2)]

        # first_row = [1, 1 , 1]
        # second_row = [0, 0, 0]
        # third_row = [0, 0, 0]
        random_strategies = [first_row, second_row, third_row]
        historical_random_strategies = [historical_first_row, historical_second_row, historical_third_row]
        self.m_Grid2D.initCond(j, i, random_strategies)
        self.m_Grid2D.initCond(j, i, historical_random_strategies, level=1)

        self.round_results.initCond(j, i, 0)

  def play(self, a, b):
    if (a == self.COOPERATE and b == self.COOPERATE):
      return self.R
    if (a == self.COOPERATE and b == self.DEFECT): 
      return  self.P
    if (a == self.DEFECT and b == self.COOPERATE):
      return self.T
    if (a == self.DEFECT and b == self.DEFECT):
      return self.C

  def compute_payoffs(self):
    for x in range(0, self.m_Grid2D.getHeight()):
      for y in range(0, self.m_Grid2D.getWidth()):
        strategies = self.m_Grid2D.getState(x,y)
        score = 0

        '''
        Using (x, y) as reference (current player), we want
        to play against all its neighbours

        (x-1, y+1)  |  (x, y+1)  | (x+1, y+1)
        ------------**************------------
        (x-1, y)    *   (x, y)   * (x+1, y)
        ------------**************------------
        (x-1, y-1)  |  (x, y-1)  | (x+1, y-1)

        '''
        for i in range(3):
          for j in range(3):
            if i == 1 and j == 1:
              continue

            neighbor_strategies = CA.m_Grid2D.getState(x-1+i, y-1+j)
            neighbor_strategy_against_me = neighbor_strategies[2-i][2-j]
            my_strategy_against_neighbor = strategies[i][j]
            score += self.play(my_strategy_against_neighbor, neighbor_strategy_against_me)

        self.round_results.setState(x, y, score)

    self.round_results.swap()

  def tit_for_tat_discriminative(self, x, y):
    new_strategies = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    for i in range(3):
      for j in range(3):
        if i == 1 and j == 1:
          continue

        neighbor_strategies = CA.m_Grid2D.getState(x-1+i, y-1+j)
        neighbor_strategy_against_me = neighbor_strategies[2-i][2-j]
        new_strategies[i][j] = neighbor_strategy_against_me

    return new_strategies

  def tit_for_two_tat_discriminative(self, x, y):
    new_strategies = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    for i in range(3):
      for j in range(3):
        if i == 1 and j == 1:
          continue

        neighbor_strategies = CA.m_Grid2D.getState(x-1+i, y-1+j)
        prev_neighbor_strategies = CA.m_Grid2D.getState(x-1+i, y-1+j, 1)
        neighbor_strategy_against_me = neighbor_strategies[2-i][2-j]
        prev_neighbor_strategy_against_me = prev_neighbor_strategies[2-i][2-j]

        if (neighbor_strategy_against_me == self.DEFECT and prev_neighbor_strategy_against_me == self.DEFECT):
          new_strategies[i][j] = self.DEFECT 
        else:
          new_strategies[i][j] = self.COOPERATE

    return new_strategies

  def get_new_strategy(self, x, y):
    if (self.STRATEGY_SELECTION == 'tit-for-tat'):
      return self.tit_for_tat_discriminative(x, y)

    if (self.STRATEGY_SELECTION == 'tit-for-two-tat'):
      return self.tit_for_two_tat_discriminative(x, y)

    else:
      raise NotImplementedError('Strategy not implemented')

  def update(self):
    self.rounds = self.rounds + 1

    self.compute_payoffs()
    self.statistic()

    for x in range(0, self.m_Grid2D.getHeight()):
      for y in range(0, self.m_Grid2D.getWidth()):
        new_strategy = self.get_new_strategy(x, y)

        self.m_Grid2D.setState(x, y, new_strategy)

    CellularAutomata.update(self)

  def statistic(self):
    count_C = 0
    count_D = 0
    sum_scores = 0

    for x in range(0, self.m_Grid2D.getHeight()):
      for y in range(0, self.m_Grid2D.getWidth()):
        strategies = self.m_Grid2D.getState(x, y)
        score = self.round_results.getState(x, y)

        sum_scores += score

        for i in range(3):
          for j in range(3):
            if i == 1 and j == 1:
              continue
            strategy = strategies[i][j]
            if strategy == self.COOPERATE:
              count_C += 1
            elif strategy == self.DEFECT:
              count_D += 1

    self.hist_C.append(count_C)
    self.hist_D.append(count_D)
    self.hist_rounds.append(self.rounds)
    self.hist_score.append(sum_scores / (count_C + count_D))

  def finalCond(self):
    strategy_distribution_chart = plt.figure()
    X = np.array(self.hist_rounds)

    ax = strategy_distribution_chart.add_subplot()
    ax.bar(self.hist_rounds, self.hist_C, label="C", color='blue')
    ax.bar(self.hist_rounds, self.hist_D, label="D", color='red', bottom=self.hist_C)
    plt.xticks(X)

    results_chart = plt.figure()
    bx = results_chart.add_subplot()
    bx.bar(X, self.hist_score, 0.5, label = 'Mean score')
    bx.legend()

    plt.xticks(X)

    plt.show()

if __name__ == '__main__':
    boundary = 'periodic'
    w = 100
    h = 100

    grid = Grid2D_PeriodicDiscriminative(w, h)

    CA = PrisionersDilemma()
    CA.setGrid(grid)
    CA.initCond()

    gui = GUILoop(CA)
    gui.setCellularAutomata(CA)
    gui.init()
    gui.loop()
  
    CA.finalCond()