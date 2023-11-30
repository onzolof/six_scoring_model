import streamlit as st

from model import calculate_normalized_regression_score, build_regression_formula_in_latex, calculate_combined_score, \
    build_combining_formula_in_latex

st.set_page_config(
    page_title="Score Calculator",
    page_icon="➕",
    layout="wide"
)

variables = {
    "complexity": {
        "event_type_complexity": {
            "label": "Event Type Complexity",
            "coefficient": "0.2",
            "value": "0.2",
            "help": "the different even types (such as DRIP, EXOF or TEND) are associated with different complexities."
        },
        "security_type_complexity": {
            "label": "Security Type Complexity",
            "coefficient": "0.05",
            "value": "0.15",
            "help": "the different security types (such as equity or bonds) are associated with different complexities."
        },
        "text_length": {
            "label": "Text Length",
            "coefficient": "0.1",
            "value": "0.4",
            "help": "Length of the text in the SWIFT message in characters. Values are normalized, thus the value 1 stands for the text length of the longest text ever received, whereas 0 represents the shortest text."
        },
        "market_complexity": {
            "label": "Market Complexity",
            "coefficient": "0.4",
            "value": "0.8"
        },
        "sender_complexity": {
            "label": "Sender Complexity",
            "coefficient": "0.3",
            "value": "0.5",
        },
        "message_from_home_market": {
            "label": "Message from Foreign Market",
            "coefficient": "0.2",
            "type": "dichotomous",
            "value": "False",
            "help": "This flag is true, if the message was sent from a sender which is not located in the securities home market."
        },
    },
    "criticality": {
        "position_sum": {
            "label": "Sum of Positions",
            "coefficient": "0.7",
            "value": "0.6",
            "help": "This value is high, if SIX holds a high position in the underlying security. Because of the normalization, 1 converges towards the highest position SIX every hold historically."
        },
        "security_type_criticality": {
            "label": "Security Type Criticality",
            "coefficient": "0.05",
            "value": "0.3"
        },
        "market_volume_of_security": {
            "label": "Market Volume of Security",
            "coefficient": "0.05",
            "value": "0.3",
            "help": "Important markets are more critical than exotic or niche markets."
        }},
    "combined": {
        "initial_weight_complexity_score": "0.7"
    },
}


def calc_all_scores():
    calculate_complexity_score()
    calculate_criticality_score()
    update_combined_score()


def update_combined_score():
    update_score_weights()
    complexity_score = st.session_state["complexity_score"]
    complexity_score_weight = st.session_state["weight_complexity_score"]
    criticality_score = st.session_state["criticality_score"]
    criticality_score_weight = st.session_state["weight_criticality_score"]
    st.session_state["combined_score"] = calculate_combined_score(complexity_score, criticality_score,
                                                                  complexity_score_weight, criticality_score_weight)
    st.session_state["combining_formula"] = build_combining_formula_in_latex(complexity_score, criticality_score,
                                                                             complexity_score_weight,
                                                                             criticality_score_weight)


def update_score_weights():
    complexity_score_weight = st.session_state["weight_complexity_score"]
    st.session_state["weight_criticality_score"] = 1 - complexity_score_weight


def calculate_complexity_score():
    coefficients, values = get_params("complexity")
    st.session_state["complexity_score"] = calculate_normalized_regression_score(coefficients, values)
    param_names = snake_to_pascal_case(variables["complexity"].keys())
    st.session_state["complexity_formula"] = build_regression_formula_in_latex(param_names, coefficients, values)


def calculate_criticality_score():
    coefficients, values = get_params("criticality")
    st.session_state["criticality_score"] = calculate_normalized_regression_score(coefficients, values)
    param_names = snake_to_pascal_case(variables["criticality"].keys())
    st.session_state["criticality_formula"] = build_regression_formula_in_latex(param_names, coefficients, values)


def snake_to_pascal_case(keys) -> list:
    param_names = []
    for key_name in keys:
        param_names = [*param_names, key_name.replace("_", " ").title().replace(" ", "")]
    return param_names


def get_params(prefix):
    coefficients = [st.session_state[prefix + "_constant"]]
    values = []
    for param_key in variables[prefix].keys():
        coefficients = [*coefficients, st.session_state[prefix + "_coeff_" + param_key]]
        current_value = st.session_state[prefix + "_value_" + param_key]
        if isinstance(current_value, bool):
            current_value = 1. if bool(current_value) else 0.
        values = [*values, current_value]
    return coefficients, values


tab_complexity, tab_criticality, tab_prio = st.tabs(["Complexity", "Criticality", "Combined"])

with tab_complexity:
    st.header("Complexity Prediction", divider="gray")
    st.text("Predict the complexity of an SWIFT message.")

    complexity_config = variables["complexity"]

    with st.expander("Coefficients"):
        st.text(
            "Define the weight for each feature. This values can either be defined\nqualitatively (expert model) or learned quantitatively on historical\ndata (statistical model).")

        st.number_input(key="complexity_constant", label="Constant Complexity", disabled=True, value=0)

        for key, config in complexity_config.items():
            st.number_input(key=("complexity_coeff_" + key), label=config["label"], min_value=0., max_value=1.,
                            value=float(config["coefficient"]), step=0.05, on_change=calc_all_scores)

    with st.expander("Calculation"):
        st.latex(st.session_state["complexity_formula"] if "complexity_formula" in st.session_state.keys() else "")

    for key, config in complexity_config.items():
        help_caption = config["help"] if "help" in config.keys() else None
        if "type" in config.keys() and config["type"] == "dichotomous":
            st.toggle(key=("complexity_value_" + key), label=config["label"], value=bool(config["value"]),
                      help=help_caption, on_change=calc_all_scores)
        else:
            st.slider(key=("complexity_value_" + key), label=config["label"], min_value=0., max_value=1.,
                      value=float(config["value"]), step=0.05, help=help_caption, on_change=calc_all_scores)

    if "complexity_score" in st.session_state:
        st.success("Complexity Score: " + str(st.session_state["complexity_score"]))

with tab_criticality:
    st.header("Criticality Prediction", divider="gray")
    st.text("Predict the criticality of an event.")

    criticality_config = variables["criticality"]

    with st.expander("Coefficients"):
        st.text(
            "Define the weight for each feature. This values can either be defined\nqualitatively (expert model) or learned quantitatively on historical\ndata (statistical model).")

        st.number_input(key="criticality_constant", label="Constant Criticality", disabled=True, value=0)

        for key, config in criticality_config.items():
            st.number_input(key=("criticality_coeff_" + key), label=config["label"], min_value=0., max_value=1.,
                            value=float(config["coefficient"]), step=0.05, on_change=calc_all_scores)

    with st.expander("Calculation"):
        st.latex(st.session_state["criticality_formula"] if "criticality_formula" in st.session_state.keys() else "")

    for key, config in criticality_config.items():
        if "type" in config.keys() and config["type"] == "dichotomous":
            st.toggle(key=("criticality_value_" + key), label=config["label"], value=bool(config["value"]),
                      help=help_caption, on_change=calc_all_scores)
        else:
            help_caption = config["help"] if "help" in config.keys() else None
            st.slider(key=("criticality_value_" + key), label=config["label"], min_value=0., max_value=1.,
                      value=float(config["value"]), step=0.05, help=help_caption, on_change=calc_all_scores)

    if "criticality_score" in st.session_state:
        st.success("Criticality Score: " + str(st.session_state["criticality_score"]))

with tab_prio:
    st.header("Calculating Prioritization Score", divider="gray")
    st.text("Combine the complexity and the criticality predictions into a single score.")

    combined_config = variables["combined"]

    with st.expander("Weights"):
        complexity_score_weight = st.session_state[
            "weight_complexity_score"] if "weight_complexity_score" in st.session_state.keys() else float(
            combined_config["initial_weight_complexity_score"])
        st.number_input(key="weight_complexity_score", label="Weight Complexity Score", value=complexity_score_weight,
                        step=0.05, on_change=calc_all_scores, min_value=0., max_value=1.)
        st.number_input(key="weight_criticality_score", label="Weight Criticality Score", disabled=True,
                        value=float(1 - st.session_state["weight_complexity_score"]), on_change=calc_all_scores)

    with st.expander("Calculation"):
        st.latex(st.session_state["combining_formula"] if "combining_formula" in st.session_state.keys() else "")

    if "combined_score" in st.session_state:
        st.success("Combined Score: " + str(st.session_state["combined_score"]))
