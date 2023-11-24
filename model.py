import numpy as np


def _calculate_regression_score(coefficients: list, values: list):
    constant = coefficients[0]
    weights_array = np.array(coefficients[1:])
    values_array = np.array(values)
    assert len(weights_array) == len(values_array)
    score = constant + np.sum(weights_array * values_array)
    return score


def _normalize(score, coefficients: list, values: list):
    """
    round(((value - min) / (max-min) * 9) + 1)
    """
    min_score = _calculate_regression_score(coefficients, [0] * len(values))
    max_score = _calculate_regression_score(coefficients, [1] * len(values))
    normalized_score = (score - min_score) / (max_score - min_score)
    number_of_classes = 9
    scaled_score = int(round((normalized_score * number_of_classes) + 1))
    return scaled_score


def calculate_normalized_regression_score(coefficients: list, values: list):
    """
    coefficients: beta_0, beta_1, ..., beta_n
    values: x_1, x_2, ..., x_n
    returns: y_predicted
    """
    score = _calculate_regression_score(coefficients, values)
    normalized_score = _normalize(score, coefficients, values)
    return normalized_score
