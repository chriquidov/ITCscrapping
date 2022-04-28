import numpy as np
import pandas as pd


class kNNClassifier:
    data = pd.DataFrame()
    labels = pd.DataFrame()

    def __init__(self, n_neighbors):
        self.n_neighbors = n_neighbors

    # calculate the Euclidean distance between two vectors
    def __euclidean_distance(self, row1, row2):
        return ((row1 - row2) ** 2).sum()

    # Locate the most similar neighbors
    def __get_neighbors(self, train, test_row, n_neighbors):
        distances = list()
        for train_row in train:
            dist = self.__euclidean_distance(test_row, train_row)
            distances.append((train_row, dist))
        distances.sort(key=lambda tup: tup[1])
        neighbors = list()
        for i in range(n_neighbors):
            neighbors.append(distances[i][0])
        return neighbors

    # Make a classification prediction with neighbors
    def __predict_classification(self, train, test_row, n_neighbors):
        neighbors = self.__get_neighbors(train, test_row, n_neighbors)
        output_values = [row[-1] for row in neighbors]
        y_pred0 = max(set(output_values), key=output_values.count)
        return y_pred0

    def fit(self, X, y):
        self.data = X
        self.labels = y

    def predict(self, X):
        if self.data.shape == (0, 0):
            print("Please fit your model before predicting")
            return
        else:
            train = pd.concat(self.data, self.labels, axis=1)
            y_pred = []
            for test_row in X:
                y_pred0 = self.__predict_classification(
                    train, test_row, self.n_neighbors)
                y_pred.append(y_pred0)
        return y_pred
