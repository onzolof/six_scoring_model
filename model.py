import numpy as np

def calculate_regression_score(coefficients: list, values: list):
    """
    coefficients: beta_0, beta_1, ..., beta_n
    values: x_1, x_2, ..., x_n
    returns: y_predicted
    """
    constant = coefficients[0]
    weights = np.array(coefficients[1:])
    values = np.array(values)
    assert len(weights) == len(values)
    return constant + np.sum(weights * values)
