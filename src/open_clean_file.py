import pandas as pd
from pathlib import Path
import streamlit as st
from clrutils import Lith_order
from itertools import combinations
from src import pairings, namemap


def open_clean_file(
    pairings=pairings,
    namemap=namemap,
    plot_df_file="pcadata.csv",
    pca_ldg_df_file="pcadata_ldg.csv",
    expl_var_file="expl_var.csv",
    lithorder=Lith_order,
):
    """
    Opens and cleans a csv file.
    """
    expectedcols = [
        "pc1",
        "pc2",
        "lithology_relog",
        "npr_sizes",
        "primary_alteration",
        "secondary_alteration",
        "npr_labels",
    ]
    plot_df = pd.read_csv(plot_df_file)
    plot_df.columns = (
        plot_df.columns.str.lower()
        .str.replace(r"\(|\)", "", regex=True)
        .str.replace(" ", "_")
    )

    if all([col in plot_df.columns.to_list() for col in expectedcols]):
        pass
    else:
        st.write(
            "Warning: Columns do not match expected columns. Match column names to expected columns."
        )
        colsneedingname = [
            col for col in expectedcols if col not in plot_df.columns.to_list()
        ]
        st.write(f"Please use the form below to rename columns: {colsneedingname}")
        st.write(
            f"Choose from these columns in your dataset: {[c for c in plot_df.columns if c not in expectedcols]}"
        )
        with st.form(key="form"):
            col_to_change = st.multiselect("Matching to", colsneedingname)
            cololdname = st.text_input("Matching seperated by a comma", value="").split(
                ","
            )
            renamedictionary = {
                colold.lstrip().rstrip(): newname
                for colold, newname in zip(cololdname, col_to_change)
            }
            submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            plot_df = plot_df.rename(columns=renamedictionary)

    if not all([col in plot_df.columns.to_list() for col in expectedcols]):
        st.write("Warning: Columns do not match expected columns. Please try again.")
        st.stop()
    with st.form(key="addcol"):
        addcol = st.multiselect(
            "Add columns to plot",
            [col for col in plot_df.columns if col not in expectedcols],
        )
        submit_button_col = st.form_submit_button(label="Submit")
    if submit_button_col:
        for col in addcol:
            expectedcols.append(col)
            pairings.append(col)
            namemap[col] = col

    plot_df = plot_df.loc[:, expectedcols].copy()
    plotlithos = plot_df["lithology_relog"].unique()
    nonmatchinglithos = [lith for lith in plotlithos if lith not in lithorder]
    if len(nonmatchinglithos) > 0:
        print(f"Warning: Lithologies {nonmatchinglithos} not in standard set.")
        treatment = st.text_input("Delete or rename? (d/r): ")
        if treatment.lower() == "d":
            plot_df = plot_df[~plot_df["lithology_relog"].isin(nonmatchinglithos)]
        elif treatment.lower() == "r":
            st.write(
                "Rename the lithologies. Can either rename to standard, or enter current name to have name added to current standard set."
            )
            replacedict = {a: "" for a in nonmatchinglithos}
            st.text(f"Possible lithologies: {lithorder}")
            for lith in replacedict.keys():
                replacedict[lith] = st.text_input(f"New name for {lith}: ")
            plot_df["lithology_relog"].replace(replacedict, inplace=True)
        else:
            raise ValueError("Invalid treatment.")
    newliths = [
        lith for lith in plot_df["lithology_relog"].unique() if lith not in lithorder
    ]
    lithorder = lithorder + newliths
    lithorder = [lth.upper() for lth in lithorder]
    plot_df["npr_sizes"] = plot_df["npr_sizes"].astype(float)
    possiblelabels = [
        "NPR<0.2",
        "0.2<NPR",
        "0.2<NPR<2",
        "0.2<NPR<3",
        "2<NPR<3",
        "NPR>3",
        "3<NPR",
    ]
    plot_df["npr_labels"] = (
        plot_df["npr_labels"]
        .astype(str)
        .str.upper()
        .str.replace("X", "NPR")
        .str.replace(r"(?<!\d)\.", "0.", regex=True)
    )
    possiblelabels = [p for p in possiblelabels if p in plot_df["npr_labels"].unique()]
    if len(possiblelabels) != len(plot_df["npr_labels"].unique()):
        st.write("Warning: Labeling mix up. Defaulting to alphabetical order.")
        st.write(
            [lab for lab in plot_df["npr_labels"].unique() if lab not in possiblelabels]
        )
        possiblelabels = sorted(plot_df["npr_labels"].unique())
    plot_df["npr_labels"] = pd.Categorical(
        plot_df["npr_labels"], categories=possiblelabels, ordered=True
    )
    plot_df.fillna("No Data", inplace=True)
    # replace variations of none and no data with "No Data"
    for col in ["primary_alteration", "secondary_alteration"]:
        plot_df[col] = (
            plot_df[col]
            .str.lower()
            .str.replace(" ", "")
            .str.replace("none", "No Data")
            .str.replace("nodata", "No Data")
        )
    for col in ["lithology_relog", "primary_alteration", "secondary_alteration"]:
        plot_df[col] = plot_df[col].astype(str).str.upper()
    # make new columns of couplets and triplets
    cpltrps = []
    for num in range(2, 4):
        for comb in combinations(
            ["lithology_relog", "primary_alteration", "secondary_alteration"], num
        ):
            cpltrps.append(comb)
            plot_df["_".join(comb)] = plot_df[list(comb)].apply(
                lambda x: "_".join(x.astype(str)), axis=1
            )
    # bring in the pca_ldg_df
    pca_ldg_df = pd.read_csv(pca_ldg_df_file)
    pca_ldg_df.columns = pca_ldg_df.columns.str.lower()
    ldgnames = {}
    for col in ["pc1", "pc2", "metals"]:
        if not col in pca_ldg_df.columns:
            ldgnames[col] = input(f"{col} required, what is its name in your data: ")
    if len(ldgnames) > 0:
        pca_ldg_df.rename(columns=ldgnames, inplace=True)
    pca_ldg_df["metals"] = (
        pca_ldg_df["metals"].str.split("_").str[0].str.replace(" ", "").str.capitalize()
    )
    # bring in the expl_var
    expl_var = pd.read_csv(expl_var_file)
    if expl_var.empty:
        if expl_var.shape[0] > expl_var.shape[1]:
            expl_var = expl_var.reset_index(drop=True)
        else:
            expl_var = expl_var.T.reset_index()
        try:
            expl_var = expl_var.astype(float)
        except:
            st.write("Warning: Explained variance file should contain only numbers.")
            st.stop()
    expl_var_out = expl_var.values.flatten().tolist()[:2]

    return pairings, namemap, plot_df, pca_ldg_df, expl_var_out, lithorder
