class Grid2D_Fixed:
    def get_zero_matriz(self, w, h):
        matrix = []
        for _ in range(w):
            matrix.append([])

        for x in range(w):
            for _ in range(h):
                matrix[x].append([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

        return matrix

    def __init__(self, w, h):
        self.m_Width = w
        self.m_Height = h
        self.m_buff0 = self.get_zero_matriz(w, h)
        self.m_buff1 = self.get_zero_matriz(w, h)
        self.m_buff2 = self.get_zero_matriz(w, h)
        self.m_const = 0

    #In initial condition, both buffers should be set with the same state
    #in order to guarantee the correct state  render
    def initCond(self, l, c, s):
        self.m_buff2[l][c] = s
        self.m_buff1[l][c] = s
        self.m_buff0[l][c] = s

    def setConstant(self, c):
        self.m_const = c

    def setState(self, l, c, s):
        self.m_buff1[l][c] = s


    def getState(self, l, c):
        if l >= 0 and l < self.m_Height and c >= 0 and c < self.m_Width:
            return self.m_buff0[l][c]
        else:
            return self.m_const

    def getWidth (self):
        return self.m_Width

    def getHeight (self):
        return self.m_Height

    def swap(self):
        aux = self.m_buff1
        self.m_buff1 = self.m_buff0
        self.m_buff0 = aux


class Grid2D_Periodic(Grid2D_Fixed):
    pass

    def initCond(self, l, c, s, level = 0):
        if level == 0:
            self.m_buff2[l][c] = s
            self.m_buff1[l][c] = s

        else:
            self.m_buff0[l][c] = s

    def swap(self):
        aux = self.m_buff2
        self.m_buff2 = self.m_buff0
        self.m_buff0 = self.m_buff1
        self.m_buff1 = aux

    def setState(self, l, c, s):
        self.m_buff2[l][c] = s

    def getState(self, l, c, level = 0):
        l1 = l
        c1 = c

        if l1 < 0:
            l1 = self.m_Height + l1

        if l1 >= self.m_Height:
            l1 = l1 % self.m_Height


        if c1 < 0:
            c1 = self.m_Width + c1

        if c1 >= self.m_Width:
            c1 = c1 % self.m_Width
        
        if level == 0:
            return self.m_buff1[l1][c1]
        if level == 1:
            return self.m_buff0[l1][c1]

class Grid2D_Reflective(Grid2D_Fixed):
    pass
    def getState(self, l, c):
        l1 = l
        c1 = c

        if l1 < 0:
            l1 = (l1 * -1)

        if l1 >= self.m_Height:
            l1 = self.m_Height - (l1 % self.m_Height) - 1

        if c1 < 0:
            c1 = (c1 * -1)

        if c1 == self.m_Width:
            c1 = self.m_Width - (c1 % self.m_Width) - 1

        return self.m_buff0[l1][c1]
