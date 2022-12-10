import matplotlib.pyplot as plt
import numpy as np

from CellularAutomata import CellularAutomata
from Color import Color
from Grid2D import Grid2D_Periodic
from GUI import GUILoop

VISUAL_MODE = True
MAX_ROUNTS = 100
STRATEGIES = [
  'random',
  'tit-for-tat',
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

  STRATEGY_SELECTION = 'tit-for-tat'

  assert STRATEGY_SELECTION in STRATEGIES, "Strategy must be one of {}".format(STRATEGIES)

  def __init__(self):
    self.m_TimeStep = 0
    self.hist_C = []
    self.hist_D = []
    self.mean_score_C = 0
    self.mean_score_D = 0
    self.hist_rounds = []
    self.rounds = 0
    self.round_results = Grid2D_Periodic(w, h)

  def initCond(self):
    random_strategies = np.random.randint(2, size=(self.m_Grid2D.getHeight(), self.m_Grid2D.getWidth()))
    # random_strategies = [[0, 1], [0, 0]]

    for j in range(0, self.m_Grid2D.getHeight()):
      for i in range(0, self.m_Grid2D.getWidth()):
        self.m_Grid2D.initCond(j, i, random_strategies[j][i])
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
        strategy = self.m_Grid2D.getState(x,y)

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
        for i in range(x-1, x+2):
          for j in range (y-1, y+2):
            # Do not play against itself
            if i == x and j == y:
              continue

            # Play with neighbour
            neighbor_strategy = self.m_Grid2D.getState(i,j)
            score += self.play(strategy, neighbor_strategy)

        self.round_results.setState(x, y, score)
      
    self.round_results.swap()

  def tit_for_tat_non_discriminative(self, x, y):
    neighbors_played_C = 0
    neighbors_played_D = 0
    
    for i in range(x-1, x+2):
      for j in range (y-1, y+2):

        if i == x and j == y:
          continue

        neighbor_strategy = CA.m_Grid2D.getState(i,j)
        if (neighbor_strategy == self.COOPERATE):
          neighbors_played_C += 1
        else:
          neighbors_played_D += 1
        
    neighbors_count = neighbors_played_C + neighbors_played_D
    
    if (neighbors_played_D / neighbors_count > 0.5):
      return self.DEFECT
    
    return self.COOPERATE

  def get_new_strategy(self, x, y):
    if (self.STRATEGY_SELECTION == 'random'):
      return np.random.randint(2)

    if (self.STRATEGY_SELECTION == 'tit-for-tat'):
      return self.tit_for_tat_non_discriminative(x, y)

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
    sum_score_C = 0
    sum_score_D = 0

    for x in range(0, self.m_Grid2D.getHeight()):
      for y in range(0, self.m_Grid2D.getWidth()):
        strategy = self.m_Grid2D.getState(x,y)
        if strategy == self.COOPERATE:
            count_C = count_C + 1
            sum_score_C += self.round_results.getState(x, y)
        elif strategy == self.DEFECT:
            count_D = count_D + 1
            sum_score_D += self.round_results.getState(x, y)

    self.mean_score_C = ((sum_score_C / count_C if count_C else 0) + self.mean_score_C * self.rounds - 1) / self.rounds
    self.mean_score_D = ((sum_score_D / count_D if count_D else 0) + self.mean_score_D * self.rounds - 1) / self.rounds

    self.hist_C.append(count_C)
    self.hist_D.append(count_D)
    self.hist_rounds.append(self.rounds)

  def finalCond(self):
    print('Media de pontos de jogadores que colaboraram: {}'.format(self.mean_score_C))
    print('Media de pontos de jogadores que traíram: {}'.format(self.mean_score_D))

    if VISUAL_MODE:
      strategy_distribution_chart = plt.figure()
      ax = strategy_distribution_chart.add_subplot()
      ax.bar(self.hist_rounds, self.hist_C, label="C", color='blue')
      ax.bar(self.hist_rounds, self.hist_D, label="D", color='red', bottom=self.hist_C)
      ax.legend(['C', 'D'])

      points_chart = plt.figure()
      bx = points_chart.add_subplot()
      bx.bar(['C', 'D'], [self.mean_score_C, self.mean_score_D])

      plt.show()

if __name__ == '__main__':
    boundary = 'periodic'
    w = 100
    h = 100
    palettes = []
    palettes.append(Color(0, 102, 204)) # Blue for C
    palettes.append(Color(204, 0, 0)) # Red for D

    grid = Grid2D_Periodic(w, h)

    CA = PrisionersDilemma()
    CA.setGrid(grid)
    CA.initCond()

    if (VISUAL_MODE):
      gui = GUILoop(CA)
      gui.setPalette(palettes)
      gui.setCellularAutomata(CA)
      gui.init()
      gui.loop()
    
    else:
      for i in range(0, MAX_ROUNTS):
        print('Round: ', i)
        CA.update()
    
    CA.finalCond()