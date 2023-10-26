# %%
import streamlit as st
from clrutils.pca_plots import pca_plot
import re

# from src import pairings, namemap


# %%
st.set_page_config(layout="wide")
st.title("Bi-plot of PCA data")
st.write("This page shows the PCA biplots of data.")

if all(
    [
        "pairings" in st.session_state,
        "namemap" in st.session_state,
        "df" in st.session_state,
        "ldg" in st.session_state,
        "expl_var" in st.session_state,
    ]
):
    pairings = st.session_state.pairings
    namemap = st.session_state.namemap
    lithorder = st.session_state.lithorder
    df = st.session_state.df
    ldg = st.session_state.ldg
    expl_var = st.session_state.expl_var

    lithgrps = {}
    for k, v in namemap.items():
        if k == "Lithology":
            lithgrps[k] = lithorder
        else:
            lithgrps[k] = sorted(df[v].unique().tolist())

    exld = st.sidebar.multiselect(
        "Exlude no data",
        ["Lithology", "Primary alteration", "Secondary alteration"],
    )
    temp = df.copy()
    if len(exld) > 0:
        for ech in exld:
            temp = temp[temp[namemap[ech]] != "NO DATA"].copy()

    lithgrptoshow = st.sidebar.text_input(
        f"Enter lithologies to show seperated by a space, to reset enter an empty list:\noptions are: {[lth for lth in lithorder if lth in temp.lithology_relog.unique().tolist()]}",
        "",
    )

    if len(lithgrptoshow) > 0:
        ndprez = len(re.findall(r"no\s*data", lithgrptoshow, re.IGNORECASE)) > 0
        lithgrptoshow = re.sub(r"[^\w\s\d]", "", lithgrptoshow).split(" ")
        lithgrptoshow = [ech.upper() for ech in lithgrptoshow]
        if ndprez:
            lithgrptoshow.append("NO DATA")

        temp = temp[temp["lithology_relog"].str.upper().isin(lithgrptoshow)]

    alphas = st.sidebar.number_input(
        "Enter the alpha value for the biplot:", 0.0, 1.0, 0.5, 0.1
    )

    choice = st.sidebar.selectbox(
        "Color by:",
        pairings,
        index=0,
    )

    ttl = st.sidebar.text_input(
        "Enter the title for the plot, use '--' for newline:", "PCA biplot"
    ).replace("--", "\n")

    figsize = st.sidebar.number_input(
        "Enter the figure size for the plot:", 10, 15, 10, 1
    )

    bbxy = st.sidebar.number_input(
        label="Move bottom legend down if needed:",
        min_value=-0.06,
        max_value=0.0,
        value=0.0,
        step=0.01,
    )

    figx, axx = pca_plot(
        temp,
        ldg,
        expl_var,
        lith=namemap[choice],  # type: ignore
        lith_order_in=[l for l in lithgrps[choice] if l in temp[namemap[choice]].unique()],  # type: ignore
        pca1="pc1",
        pca2="pc2",
        pca1a="pc1",
        pca2a="pc2",
        npr_size="npr_sizes",
        btmldglbls=temp["npr_labels"].cat.categories,
        bold=True,
        alpha_sct=alphas,
        topledgettl=choice.replace("-", "\n").replace("_", " "),  # type: ignore
        title=ttl,
        tpbbx=0.99,
        btbby=bbxy,
    )

    # st.pyplot(figx, use_container_width=False, figsize=(figsize, figsize))
    figx.set_size_inches(figsize, figsize)

    with st.sidebar.form(key="zoom"):
        standardzoom = st.form_submit_button(
            "Set zoom to full extent (i.e. when all data is shown)"
        )
    if standardzoom:
        if "stdzoom" not in st.session_state:
            fignoshow, axnoshow = pca_plot(
                df,
                None,
                expl_var,
                lith="lithology_relog",  # type: ignore
                lith_order_in=lithorder,  # type: ignore
                pca1="pc1",
                pca2="pc2",
                pca1a="pc1",
                pca2a="pc2",
                plot_npr=False,
                npr_size="npr_sizes",
                loading_lines=False,
            )
            st.session_state["stdzoom"] = [axnoshow.get_xlim(), axnoshow.get_ylim()]
        axx.set_xlim(st.session_state["stdzoom"][0])
        axx.set_ylim(st.session_state["stdzoom"][1])
    st.pyplot(figx, use_container_width=False)


else:
    st.spinner("Loading data...")

# %%
