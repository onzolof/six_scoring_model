import collections

import streamlit as st

from model import calculate_normalized_regression_score

st.set_page_config(
    page_title="Score Calculator",
    page_icon="➕",
)

variables = {
    "effort": {
        "event_type_complexity": {
            "label": "Event Type Complexity",
            "coefficient": "0.2",
            "value": "0.2"
        },
        "security_type_complexity": {
            "label": "Security Type Complexity",
            "coefficient": "0.05",
            "value": "0.15"
        }
    },
    "criticality": {

    }
}
default_values = dict(
    coeff=dict(
        event_type_complexity=0.2,
        security_type_complexity=0.1,
    )
)


def calculate_effort_score():
    coefficients, values = get_params("effort")
    st.session_state["effort_score"] = calculate_normalized_regression_score(coefficients, values)


def get_params(prefix):
    coefficients = [st.session_state[prefix + "_constant"]]
    values = []
    for param_key in variables[prefix].keys():
        coefficients = [*coefficients, st.session_state[prefix + "_coeff_" + param_key]]
        values = [*values, st.session_state[prefix + "_value_" + param_key]]
    return coefficients, values


tab_effort, tab_criticality, tab_prio = st.tabs(["Effort", "Criticality", "Combined"])

with tab_effort:
    st.header("Effort Prediction", divider="gray")
    st.text("Predict the effort of an SWIFT message.")

    effort_config = variables["effort"]

    with st.expander("Coefficients"):
        st.text(
            "Define the weight for each feature.This values can either be defined\nqualitatively or learned quantitatively on historical data.",)

        st.session_state["effort_constant"] = st.number_input(label="Constant", disabled=True, value=0.0)

        for key, config in effort_config.items():
            st.session_state["effort_coeff_" + key] = st.number_input(label=config["label"], min_value=0., max_value=1.,
                                                                      value=float(config["coefficient"]), step=0.05,
                                                                      on_change=calculate_effort_score)

    with st.expander("Calculation"):
        st.latex("Define the weight for each feature.")

    for key, config in effort_config.items():
        st.session_state["effort_value_" + key] = st.slider(label=config["label"], min_value=0., max_value=1.,
                                                            value=float(config["value"]), step=0.05,
                                                            on_change=calculate_effort_score)

    calculate_effort_score()

    st.success("Effort Score: " + str(st.session_state["effort_score"]))

with tab_criticality:
    st.header("Criticality Prediction")
    st.text("Predict the criticality of an event.")

with tab_prio:
    st.header("Calculating Prioritization Score")
    st.text("Combine the effort and the criticality predictions into a single score.")
