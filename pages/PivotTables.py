import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re
import math


# OPTIONS: REDESIGN TO RUN ON MULTI INDEXING WITH THAT MULTIPLE UNSTACK
# AND REINDEX SOLUTION YOU FOUND (I.E. TEMP.UNSTACK(LEVEL=LITH).UNSTACK()) ALTHOUGH
# THIS MIGHT HAVE ISSUES WITH THE NUMBER OF LEVELS TO UNSTACK
# AND WOULD HAVE TO BE DONE EITHER WITH A LOOP OR MANUALLY
# OR MANUALLY MAKE A NEW INDEXER BY CONCATENATING 'LITH_ORDER' WITH THE
# OTHER INDEXER (I.E. [A + B FOR A IN LITH_ORDER FOR B IN OTHER_INDEXER])
# OF COURSE THAT LIST GETS TO BE LONG AF BUT ITS JUST A LIST SO IT SHOULD BE FINE
def roundup(x):
    return math.ceil(x / 10.0) * 10


st.set_page_config(layout="wide")
st.title("Pivot tables of PCA data")
st.write("This page shows pivot tables of data.")
namemap = {
    "Lithology": "lithology_relog",
    "Primary alteration": "primary_alteration",
    "Secondary alteration": "secondary_alteration",
    "NPR bins": "npr_labels",
}

if all(
    [
        "df" in st.session_state,
        "ldg" in st.session_state,
        "expl_var" in st.session_state,
    ]
):
    lithorder = st.session_state.lithorder
    df = st.session_state.df
    ldg = st.session_state.ldg
    expl_var = st.session_state.expl_var

    df.sort_values(
        by="lithology_relog",
        key=lambda column: column.map(lambda e: lithorder.index(e)),
        inplace=True,
    )

    yaxis = st.sidebar.multiselect(
        "Rows in cross tab (max 2)",
        list(namemap.keys()),
    )

    xaxis = st.sidebar.multiselect(
        "Columns in cross tab (max 2)",
        list(namemap.keys()),
    )

    if len(yaxis) > 2 or len(xaxis) > 2:
        st.sidebar.write("Please select a maximum of 2 options for each axis")
        st.stop()

    yinput = [namemap[ech] for ech in yaxis]
    xinput = [namemap[ech] for ech in xaxis]

    if len(xinput) > 1:
        if xinput[0] + "_" + xinput[1] not in df.columns:
            df[xinput[0] + "_" + xinput[1]] = df[xinput[0]] + "_" + df[xinput[1]]
        xinput = [xinput[0] + "_" + xinput[1]]

    exld = st.sidebar.multiselect(
        "Exlude no data",
        ["Lithology", "Primary alteration", "Secondary alteration"],
    )

    temp = df.copy()
    for ech in exld:
        temp = temp[temp[namemap[ech]] != "NO DATA"]

    lithgrptoshow = st.sidebar.text_input(
        f"Enter lithologies to show seperated by a space, to reset enter an empty list:\noptions are: {[lth for lth in lithorder if lth in temp.lithology_relog.unique().tolist()]}",
        "",
    )
    if len(lithgrptoshow) > 0:
        lithgrptoshow = re.sub(r"[^\w\s\d]", "", lithgrptoshow).split(" ")
        lithgrptoshow = [ech.upper() for ech in lithgrptoshow]

        temp = temp[temp["lithology_relog"].str.upper().isin(lithgrptoshow)]

    normalized = st.sidebar.checkbox("Normalize the values", False)
    fmt = ".0f"
    vmin = None
    vmax = None
    if normalized:
        temp = (
            temp.groupby(yinput)[xinput].value_counts(normalize=True).mul(100).round(2)
        )
        fmt = ".2f"
        vmin = 0
        vmax = 100
    else:
        temp = temp.groupby(yinput)[xinput].value_counts()

    temp.replace(0, np.nan, inplace=True)

    if "Lithology" in yaxis:
        temp = temp.reindex(lithorder, level=yaxis.index("Lithology"))

    if "Lithology" in xaxis and len(xaxis) == 1:
        st.write(temp.index.names)
        temp = temp.reindex(lithorder, level=1)

    droprows = st.sidebar.checkbox("Drop rows with no data", False)
    temp = temp.unstack()
    if droprows:
        temp = temp.dropna(axis=0, how="all")

    figsize = st.sidebar.number_input(
        "Enter the size of the plot", min_value=10, max_value=15, value=10, step=1
    )

    figx, axx = plt.subplots(figsize=(figsize, figsize))
    plot = sns.heatmap(
        temp,
        cmap="Blues",
        annot=True,
        ax=axx,
        linewidths=0.01,  # type: ignore
        linecolor="lightgray",
        fmt=fmt,
        vmin=vmin,
        vmax=vmax,
    )
    if normalized:
        for t in plot.texts:
            t.set_text(t.get_text() + "%")
        cbar = axx.collections[0].colorbar
        cbar.set_ticks([0, 25, 50, 75, 100])
        cbar.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])

    ttl = st.sidebar.text_input(
        "Enter the title for the plot, use '--' for newline:", "Pivot Table"
    ).replace("--", "\n")

    axx.set_title(ttl)
    axx.set_xlabel(f"{', '.join(xaxis)}")
    axx.set_ylabel(f"{', '.join(yaxis)}")
    st.pyplot(figx)
