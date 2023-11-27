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
    min_score = _calc_min_score(coefficients, values)
    max_score = _calc_max_score(coefficients, values)
    normalized_score = (score - min_score) / (max_score - min_score)
    number_of_classes = 9
    scaled_score = int(round((normalized_score * number_of_classes) + 1))
    return scaled_score


def _calc_max_score(coefficients, values):
    return _calculate_regression_score(coefficients, [1] * len(values))


def _calc_min_score(coefficients, values):
    return _calculate_regression_score(coefficients, [0] * len(values))


def calculate_normalized_regression_score(coefficients: list, values: list) -> int:
    """
    coefficients: beta_0, beta_1, ..., beta_n
    values: x_1, x_2, ..., x_n
    returns: y_predicted
    """
    score = _calculate_regression_score(coefficients, values)
    normalized_score = _normalize(score, coefficients, values)
    return normalized_score


def calculate_combined_score(s1, s2, w1, w2) -> int:
    combined_score = w1 * s1 + w2 * s2
    return int(round(combined_score))


def build_regression_formula_in_latex(param_names: list, coefficients: list, values: list) -> str:
    string = r"f_\text{scoring}(\cdot) = \beta_0"
    for i, param_name in enumerate(param_names):
        number = str(i + 1)
        string = string + r"+ \beta_{\text{" + number + r"}} * x_{\text{" + param_name + r"}}"
    string += r"\\=" + str(coefficients[0])
    for i, param_name in enumerate(param_names):
        string = string + r"+ " + str(coefficients[i + 1]) + " * " + str(values[i])
    score = str(round(_calculate_regression_score(coefficients, values), 2))
    string += r"\\=" + score

    string += r"\\f_\text{norming}(\cdot) = round((\frac{f_\text{scoring} - min}{max - min} * 9) + 1)"

    min_score = str(_calc_min_score(coefficients, values))
    max_score = str(_calc_max_score(coefficients, values))
    string += r"\\= round((\frac{" + score + "-" + min_score + "}{" + max_score + "-" + min_score + "} * 9) + 1)"

    normalized_score = str(calculate_normalized_regression_score(coefficients, values))
    string += r"\\= " + normalized_score

    return string


def build_combining_formula_in_latex(s1, s2, w1, w2) -> str:
    string = r"f_\text{combining}(\cdot) = round(w_1*s_1 + w_2 * s_2)"
    string += r"\\=round(" + str(round(w1, 2)) + "* " + str(s1) + "+ " + str(round(w2, 2)) + "* " + str(s2) + ")"
    combined_score = str(calculate_combined_score(s1, s2, w1, w2))
    string += r"\\=" + combined_score
    return string
