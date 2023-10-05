# uses strmlt conda environment
# %%
import streamlit as st
from src.open_clean_file import open_clean_file

# %%
st.set_page_config(layout="wide")
st.title("Data Preparation")
st.header("This page is used to load and prep the data.")

df_path = st.sidebar.file_uploader("Upload the plot data file:", type=["csv"])
ldg_path = st.sidebar.file_uploader("Upload the loadings data file:", type=["csv"])
expl_var_path = st.sidebar.file_uploader(
    "Upload the explained variance data file:", type=["csv"]
)

if all([df_path, ldg_path, expl_var_path]):
    df, ldg, expl_var, lthorder = open_clean_file(
        plot_df_file=df_path,  # type: ignore
        pca_ldg_df_file=ldg_path,  # type: ignore
        expl_var_file=expl_var_path,  # type: ignore
    )

    st.session_state.df = df
    st.session_state.ldg = ldg
    st.session_state.expl_var = expl_var
    st.session_state.lithorder = lthorder
