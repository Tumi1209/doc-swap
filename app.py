import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(
    page_title="DocSwap",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🔄",
)


about_tab, details_tab, stats_tab = st.tabs(["ℹ️ About", "📝 Details", "📈 Stats"])

with about_tab:
    st.header("Welecome to DocSwap")

    st.markdown(
        """
                ### What is it?
                    SwapDoc uses an optimisation algorithim to find the best multi-party swaps. 
                """
    )

    st.markdown(
        """
                ### Disclaimer
                1. I am not recieving any monetary incentive to do this, I am just a guy that knows how to code and thought I could help.
                2. I cannot guarantee a valid swap for everyone.
                3. I only ask for information that is essential for determining valid swaps.
                4. I will not sell this information and I will not use it for anything other than finding viable swapping partners for the users of this app.
                """
    )

with details_tab:
    st.button("test")


with stats_tab:
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

    st.bar_chart(chart_data)
