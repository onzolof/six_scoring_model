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
            "value": "0.2"
        },
        "security_type_complexity": {
            "label": "Security Type Complexity",
            "coefficient": "0.05",
            "value": "0.15"
        },
        "text_length": {
            "label": "Text Length",
            "coefficient": "0.1",
            "value": "0.4"
        },
        "market_complexity": {
            "label": "Market Complexity",
            "coefficient": "0.4",
            "value": "0.8"
        },
        "number_of_subcustodians": {
            "label": "Number of Subcustodians",
            "coefficient": "0.1",
            "value": "0.5"
        },
    },
    "criticality": {
        "position_sum": {
            "label": "Sum of Positions",
            "coefficient": "0.7",
            "value": "0.6"
        },
        "security_type_criticality": {
            "label": "Security Type Criticality",
            "coefficient": "0.05",
            "value": "0.3"
        },
        "market_volume_of_security": {
            "label": "Market Volume of Security",
            "coefficient": "0.05",
            "value": "0.3"
        }
    }
}


def update_combined_score():
    calculate_criticality_score()
    calculate_combined_score()
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
    param_names = snake_to_pascal_case(variables["complexity"].keys())
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
        values = [*values, st.session_state[prefix + "_value_" + param_key]]
    return coefficients, values


tab_complexity, tab_criticality, tab_prio = st.tabs(["Complexity", "Criticality", "Combined"])

with tab_complexity:
    st.header("Complexity Prediction", divider="gray")
    st.text("Predict the complexity of an SWIFT message.")

    complexity_config = variables["complexity"]

    with st.expander("Coefficients"):
        st.text(
            "Define the weight for each feature. This values can either be defined\nqualitatively (expert model) or learned quantitatively on historical\ndata (statistical model).")

        st.session_state["complexity_constant"] = st.number_input(label="Constant Complexity", disabled=True, value=0.0)

        for key, config in complexity_config.items():
            st.session_state["complexity_coeff_" + key] = st.number_input(label=config["label"], min_value=0.,
                                                                          max_value=1.,
                                                                          value=float(config["coefficient"]), step=0.05)

    with st.expander("Calculation"):
        if "complexity_formula" in st.session_state:
            st.latex(st.session_state["complexity_formula"])

    for key, config in complexity_config.items():
        st.session_state["complexity_value_" + key] = st.slider(label=config["label"], min_value=0., max_value=1.,
                                                                value=float(config["value"]), step=0.05)

    if st.button("Calculate Complexity Score"):
        calculate_complexity_score()

    if "complexity_score" in st.session_state:
        st.success("Complexity Score: " + str(st.session_state["complexity_score"]))

with tab_criticality:
    st.header("Criticality Prediction", divider="gray")
    st.text("Predict the criticality of an event.")

    criticality_config = variables["criticality"]

    with st.expander("Coefficients"):
        st.text(
            "Define the weight for each feature. This values can either be defined\nqualitatively (expert model) or learned quantitatively on historical\ndata (statistical model).", )

        st.session_state["criticality_constant"] = st.number_input(label="Constant Criticality", disabled=True,
                                                                   value=0.0)

        for key, config in criticality_config.items():
            st.session_state["criticality_coeff_" + key] = st.number_input(label=config["label"], min_value=0.,
                                                                           max_value=1.,
                                                                           value=float(config["coefficient"]),
                                                                           step=0.05)

    with st.expander("Calculation"):
        if "criticality_formula" in st.session_state:
            st.latex(st.session_state["criticality_formula"])

    for key, config in criticality_config.items():
        st.session_state["criticality_value_" + key] = st.slider(label=config["label"], min_value=0., max_value=1.,
                                                                 value=float(config["value"]), step=0.05)

    if st.button("Calculate Criticality Score"):
        calculate_criticality_score()

    if "criticality_score" in st.session_state:
        st.success("Criticality Score: " + str(st.session_state["criticality_score"]))

with tab_prio:
    st.header("Calculating Prioritization Score", divider="gray")
    st.text("Combine the complexity and the criticality predictions into a single score.")

    with st.expander("Weights"):
        st.session_state["weight_complexity_score"] = st.number_input(label="Weight Complexity Score", value=0.7,
                                                                      step=0.05)
        if "weight_criticality_score" in st.session_state:
            st.number_input(label="Weight Criticality Score", disabled=True,
                            value=st.session_state["weight_criticality_score"])

    with st.expander("Calculation"):
        if "combining_formula" in st.session_state:
            st.latex(st.session_state["combining_formula"])

    if st.button("Calculate Combined Score"):
        update_combined_score()

    if "combined_score" in st.session_state:
        st.success("Combined Score: " + str(st.session_state["combined_score"]))
