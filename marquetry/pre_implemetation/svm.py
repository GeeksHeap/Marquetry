import numpy as np


class HardMarginSVM(object):
    def __init__(self, learn_rate=0.001, epoch=1000, random_state=42):
        self.lr = learn_rate
        self.epoch = epoch
        self.random_state = random_state
        self.is_trained = False

        self.num_samples = None
        self.num_features = None

        self.w = None
        self.b = None
        self.alpha = None

    def fit(self, x, t):
        self.num_samples = x.shape[0]
        self.num_features = x.shape[1]

        self.w = np.zeros(self.num_features)
        self.b = 0

        randgen = np.random.RandomState(self.random_state)
        self.alpha = randgen.normal(loc=0., scale=0.01, size=self.num_samples)

        for _ in range(self.epoch):
            self._cycle(x, t)

        indexes_sv = [i for i in range(self.num_samples) if self.alpha[i] != 0]
        for i in indexes_sv:
            self.w += self.alpha[i] * t[i] * x[i]

        for i in indexes_sv:
            self.b += t[i] - (self.w @ x[i])

        self.b /= len(indexes_sv)
        self.is_trained = True

    def _cycle(self, x, t):
        t = t.reshape((-1, 1))
        h = (t @ t.T) * (x @ x.T)
        grad = np.ones(self.num_samples) - h @ self.alpha
        self.alpha += self.lr * grad
        self.alpha = np.where(self.alpha < 0, 0, self.alpha)
