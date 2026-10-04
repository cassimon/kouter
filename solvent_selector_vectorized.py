import streamlit as st
import pandas as pd
from io import BytesIO
import os;
import numpy as np;
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment

abs_path = os.path.dirname(os.path.abspath(__file__));


def initApp():    
    #from eval_names import getResults

    version = 1.0;
    tool_name = f"KouTer Green Solvents V{version:.2f}"
    # -----------------------
    # Page config + CSS
    # -----------------------
    st.set_page_config(page_title=tool_name, layout="wide")
    st.markdown("""
    <style>
    /* Base table styling */
    .solvent-table {
        border-collapse: collapse;
        width: 100%;
        table-layout: fixed;
        font-size: 0.9rem;
    }

    /* Table header and cells */
    .solvent-table th, .solvent-table td {
        border: 1px solid #ddd;
        padding: 4px 8px;
        text-align: left;
        vertical-align: middle;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }

    /* Fixed row height */
    .solvent-table tbody tr {
        height: 35px;  /* adjust as needed */
    }

    /* Scrollable body with fixed height */
    .solvent-table tbody {
        display: block;
        height: 400px;  /* fixed height of the table body */
        overflow-y: auto;
    }

    /* Keep header fixed */
    .solvent-table thead, .solvent-table tbody tr {
        display: table;
        width: 100%;
        table-layout: fixed;
    }

    /* Column widths */
    .solvent-table th:nth-child(1), .solvent-table td:nth-child(1) {
        width: 55%;  /* Name column */
    }
    .solvent-table th:nth-child(2), .solvent-table td:nth-child(2) {
        width: 15%;  /* Distance column */
        text-align: right;
    }
    .solvent-table th:nth-child(3), .solvent-table td:nth-child(3) {
        width: 10%;  /* Hazards column */
        white-space: normal;
    }
    .solvent-table th:nth-child(4), .solvent-table td:nth-child(3) {
        width: 10%;  /* Hazards column */
        white-space: normal;
    }
    .solvent-table th:nth-child(5), .solvent-table td:nth-child(3) {
        width: 10%;  /* Hazards column */
        white-space: normal;
    }            
    </style>
    """, unsafe_allow_html=True)


    @st.cache_data
    def load_data():
        # This runs only once unless the file or code block changes
        df = pd.read_pickle(abs_path+'/gathered_data_norm_hashable.pkl')
        #df['dist'] = np.nan
        #print(df.keys())
        return df

    col_logo, col_title = st.columns([1, 12])
    with col_logo:
        st.image(abs_path+'/KouTer_Logo_cropped.svg', width=80)
    with col_title:
        st.title("KouTer Green Solvents V1.0")
    results = load_data();
    ########################Fields;

    #'name', 'dD', 'dD_std',
    #'dP', 'dP_std', 'dH', 'dH_std', 'dn', 'dn_std', 'beta', 'beta_std',
    #      'DC', 'DC_std', 'PubChem ID', 'GHS Codes'

    # known_solvents = results['name']
    
    # color_map = {"H2XX": "orange", "H3XX": "red", "H4XX": "darkgreen"}


    # # -----------------------
    # # Reference Solvent + Weighting Factors
    # # -----------------------
    # col_ref, col_weights = st.columns([1, 2])

    # with col_ref:
    #     st.markdown("### Reference Solvent")
    #     reference_input = st.selectbox(
    #         "Select or search a reference solvent",
    #         options=known_solvents,
    #         index=None,
    #         placeholder="Type to search solvent...",
    #         key="reference_solvent"
    #     )
    #     #st.write(f"Selected: **{reference_input or 'None'}**")
    color_map = {"H2XX": "orange", "H3XX": "red", "H4XX": "darkgreen"}

    display_to_name = {}

    for _, row in results.iterrows():
        main_name = row["name"].strip().lower()
        display_to_name[main_name] = row["name"]  # preserve original casing if needed

        for alt in row["alt_names"]:
            alt_clean = alt.strip().lower()
            if alt_clean != main_name:
                display_to_name[alt_clean] = row["name"]  # map alt -> main name

    # Now the selectbox options are all display names (main + alt)
    all_options = sorted(display_to_name.keys())

    col_ref, col_weights = st.columns([1, 2])

    with col_ref:
        st.markdown("### Reference Solvent")
        selected_display = st.selectbox(
            "Select or search a reference solvent",
            options=all_options,
            index=None,
            placeholder="Type to search solvent...",
            key="reference_solvent"
        )

    # Convert selection to canonical name
    if(not selected_display == None):
        reference_input = display_to_name[selected_display]
    else:
        reference_input = False;




    p_names_norm = {'Kamlet-Taft Alpha':'Kamlet-Taft Alpha [norm. (MAD)]','Kamlet-Taft Beta':'Kamlet-Taft Beta [norm. (MAD)]','Kamlet-Taft Pi*':'Kamlet-Taft pi* [norm. (MAD)]','Gutmann AN':'Gutmann AN [norm. (MAD)]','Gutmann DN':'Gutmann DN [norm. (MAD)]','Dielectric Constant':'Dielectric Constant [norm. (MAD)]','Hansen dD':'Hansen dD [norm. (MAD)]','Hansen dH':'Hansen dH [norm. (MAD)]','Hansen dP':'Hansen dP [norm. (MAD)]'}
    kinds = ['MSE','R2']

    def getColumnNameNorm(parameter,kind,val_std):
        return p_names_norm[parameter]+' - '+kind+' - '+val_std;

    if( "start_values" not in st.session_state):
        st.session_state.start_values = [0.828,0.716,0.746,0.732,0.797,0.842,0.831,0.781,0.672]

    r2_weights = [0.828,0.716,0.746,0.732,0.797,0.842,0.831,0.781,0.672]

    for i, v in enumerate(r2_weights):
        st.session_state.setdefault(f"weight_{i}", v)

    #ef["dD"], ref["dP"], ref["dH"],
    #        ref["dn"], ref["beta"], ref["DC"]
    names = ['Hansen dD','Hansen dP','Hansen dH','Dielectric Constant','Gutmann DN','Gutmann AN','Kamlet-Taft Alpha','Kamlet-Taft Beta','Kamlet-Taft Pi*']
    st.markdown("""
    <style>
    .column-bottom {
        display: flex;
        flex-direction: column;
        justify-content: flex-end
    }
    </style>
    """, unsafe_allow_html=True)



    with col_weights:
        st.markdown("### Weighting Factors")
        weight_cols = st.columns(5)
        with weight_cols[0]:
            st.markdown("<div class='column-bottom'>", unsafe_allow_html=True)
            buttonR2 = st.button('Put R2 weights');
            st.markdown("</div>", unsafe_allow_html=True)
            
        if(buttonR2):
            for i, v in enumerate(r2_weights):
                st.session_state[f"weight_{i}"] = v

        weights_top = [
            wc.number_input(names[i], step=0.1,key=f"weight_{i}")
            for i, wc in enumerate(weight_cols[1:])
        ]
        
        weight_cols = st.columns(5)
        weights_bottom= [
            wc.number_input(names[i+4], step=0.1,key=f"weight_{i+4}")
            for i, wc in enumerate(weight_cols)
        ]
 
    
    weights = weights_top+weights_bottom;
    

    # -----------------------
    # Button + Processing Window
    # -----------------------

    # Create a 3-column row to place the button on the right

    # with col_button:
    #     st.markdown("### Calculation")
    #     st.markdown(
    #     """
    #     <div style="margin-bottom:-10px;">
    #         with reference and weights
    #     </div>
    #     """,
    #     unsafe_allow_html=True
    # )
    #     #st.write("")
    #     calc_button = st.button("Calculate Distances", type="primary")
    @st.cache_data
    def prepareStackedData(res, kind,weights=None, keys=None):
        """
        Precompute and cache the stacked feature and std arrays for all rows.
        Returns X, Xstd, and masks for keys and positive values.
        """

        # default 
        if weights is None:
            weights = np.ones(len(names))

        # stack values
        X = np.column_stack([res[getColumnNameNorm(p,kind,"Value")] for p in names])

        Xstd = np.column_stack([res[getColumnNameNorm(p,kind,"Std_dev")] for p in names])

        # weighted versions (scaled by norm_factors)
        Xw = X * weights
        Xstdw = Xstd * weights

        return Xw, Xstdw


    #@st.cache_data
    def calculateDistances(results,reference_input,kind,dist_fun = "Euclidean", weights=None,precomputed=None):
        if not reference_input:
            results['dist'] = 0.0;
            results['dist_err'] = 0.0;
            return results, False

        matches = results[results['name'] == reference_input]
        if matches.empty:
            results['dist'] = 0.0;
            results['dist_err'] = 0.0;
            return results, False

        ref = matches.iloc[0]

        #Use precomputed arrays if provided
        if precomputed is not None:
            Xw, Xstdw  = precomputed
        else:
            Xw, Xstdw = prepareStackedData(results,kind, weights=weights)
        
        refXw = np.array([ref[getColumnNameNorm(p,kind,"Value")]*weights[i] for i,p in enumerate(names)])
        refXstdw = np.array([ref[getColumnNameNorm(p,kind,"Std_dev")]*weights[i] for i,p in enumerate(names)])

        # Difference vectors
        diff = Xw - refXw

        eps = 1e-12  # stability for divisions/logs

        var_sum = np.maximum(Xstdw**2 + refXstdw**2, eps)

        if dist_fun == "Euclidean":
            # Distance
            dist = np.sqrt(np.sum(diff**2, axis=1))

            # First-order Gaussian propagation
            dist_err = np.sqrt(np.sum(diff**2 * var_sum, axis=1)) / np.maximum(dist, eps)

        elif dist_fun == "Mahalanobis":
            # Distance
            dist = np.sqrt(np.sum(diff**2 / var_sum, axis=1))

            # Propagation not meaningful in this context
            dist_err = np.full_like(dist, np.nan)

        elif dist_fun == "Kullback–Leibler divergence":
            # Diagonal Gaussian KL divergence
            var_p = np.maximum(Xstdw**2, eps)
            var_q = np.maximum(refXstdw**2, eps)

            term1 = np.log(var_q / var_p)
            term2 = var_p / var_q
            term3 = diff**2 / var_q

            dist = 0.5 * np.sum(term1 - 1 + term2 + term3, axis=1)

            # Error propagation not meaningful (already included)
            dist_err = np.full_like(dist, np.nan)

        results["dist"] = dist
        results["dist_err"] = dist_err
        return results, True


    #if "distance_revision" not in st.session_state:
    #    st.session_state.distance_revision = 0

    #next_revision = st.session_state.distance_revision
    if "distance_kind" not in st.session_state:
        st.session_state.distance_kind = "Euclidean"

    if "best_model_kind" not in st.session_state:
        st.session_state.best_model_kind = "R2"

    #next_revision += 1
        
    Xw, Xstdw = prepareStackedData(results,st.session_state.best_model_kind,weights = weights)
    results, state = calculateDistances(
        results,
        reference_input,
        kind=st.session_state.best_model_kind,
        dist_fun=st.session_state.distance_kind,
        weights = weights,
        precomputed=(Xw, Xstdw)
        #,
        #next_revision
    )

    #st.session_state.distance_revision = next_revision;

    # -----------------------
    # Hazard Filters (Coarse Classes)
    # -----------------------
    st.markdown("### Concerning Properties")

    # Define hazard classes and mapping
    hazard_groups = {
        "Physical": "Physical",
        "Health": "Health",
        "Environmental": "Environmental",
    }

    color_map = {
        "Physical": "orange",
        "Health": "red",
        "Environmental": "magenta",
    }

    # Human-readable class names, same order as your hazard_groups keys
    names = ["Physical", "Health", "Environmental"]  # H2XX, H3XX, H4XX

    #new_entry['operational'] = operational;
    #new_entry['environmental'] = environmental;
    #new_entry['health']

    cols = st.columns(3)

    # This will store the final mapping used by filtering logic
    class_filters = {}

    for i, group in enumerate(hazard_groups.keys()):   # groups = ["H2XX", "H3XX", "H4XX"]
        with cols[i]:

            cols_sub1,cols_sub2 = st.columns(2)
            with cols_sub1:
                choice = st.radio(
                    names[i],                     # what user sees
                    ["Allow", "Filter out"],      # choices
                    horizontal=True,
                    key=f"coarse_radio_{group}"   # unique key
                )
            with cols_sub2:    
                st.markdown(
                f"<span style='color:"+color_map[names[i]]+"; font-weight:bold;'>●</span>",
                unsafe_allow_html=True
        )
        # Store the choice in the filter dictionary
        class_filters[group] = choice
            
    #print(class_filters)

    def filter_solvents(df,reference):


        # determine active filters
        disabled_prefixes = []
        for class_name, prefix in hazard_groups.items():
            if class_filters[class_name] == "Filter out":
                disabled_prefixes.append(prefix)

        # --------------------------------------------------------
        # NEW LOGIC:
        # If ANY filter is active → drop entries with NO H symbols
        # --------------------------------------------------------

        # Render colored dots only, no H symbols
        def dot_classes(row):
            #print(row)
            if(not row['hazard_data_exists']):
                return "no data"

            classes = set()
            for h in hazard_groups.values():  # make sure these are column names
                if len(row[h]) != 0:  # check if the list is non-empty
                    classes.add(h)
            
            return " ".join(
                f"<span style='color:{color_map[c]}; font-weight:bold;'>●</span>"
                for c in sorted(classes)
            )
            
        def dot_classes_text(row):
            #print(row)
            if(not row['hazard_data_exists']):
                return "no data"

            classes = set()
            for h in hazard_groups.values():  # make sure these are column names
                if len(row[h]) != 0:  # check if the list is non-empty
                    classes.add(h)
            
            return " ,".join(str(c) for c in sorted(classes))
        

        # Apply function row-wise
        df["Hazard Categories"] = df.apply(dot_classes_text, axis=1)
        df["Hazards"] = df.apply(dot_classes, axis=1)
        #df_reference["Hazards"] = df_reference.apply(dot_classes, axis=1)


        ref_mask = df["name"] == reference
        df_reference = df[ref_mask].copy()
        df_filtered = df[~ref_mask].copy()


        if(len(disabled_prefixes)>0):
            mask = df_filtered.apply(
                lambda row: all(len(row[h]) == 0 for h in disabled_prefixes) and row['hazard_data_exists'],
                axis=1
            )
            # Keep only rows that do  match the mask
            df_filtered = df_filtered[mask]

        df_filtered = df_filtered.sort_values("dist", na_position="last")

        df_filtered = pd.concat([df_reference, df_filtered], ignore_index=True)

        return df_filtered


    filtered_solvents = filter_solvents(results,reference_input)


    # -----------------------
    # Table rendering BEFORE Settings
    # -----------------------
    # Initialize session_state for num_to_show
    # Initialize session state for num_to_show if not present
    if "num_to_show" not in st.session_state:
        st.session_state["num_to_show"] = 10

    # Callback to trigger rerun
    def refresh_table():
        pass


    if "rel_uncert" not in st.session_state:
        st.session_state["rel_uncert"] = 100

    if(st.session_state.distance_kind == "Euclidean"): 
        filtered_solvents = filtered_solvents.loc[filtered_solvents["dist_err"] <= filtered_solvents["dist_err"].quantile(st.session_state.rel_uncert / 100)]

    

    df_to_show = filtered_solvents.head(st.session_state["num_to_show"]+1) #take out reference solvetn


    #_rows = len(df_to_show)
    #f n_rows < st.session_state["num_to_show"]:
    #   for _ in range(st.session_state["num_to_show"] - n_rows):
    #       df_to_show = pd.concat(
    #           [df_to_show],
    #           ignore_index=True
    #       )
    df_to_show['meta'] = "Distance Metric: "+st.session_state.distance_kind+", Weights: "+"(" + ", ".join(f"{w:.2f}" for w in weights) + "), "+"Created by "+tool_name+"(c) Simon Ternes"
    def canonical_compare(s):
        return "".join(s.strip().lower().split())  # trim, lowercase, remove all spaces

    df_to_show["name"] = (
        df_to_show["name"].str.strip().str.lower()
        + df_to_show.apply(
            lambda row: (
                " [" + ", ".join(
                    sorted(set(
                        canonical_compare(alt)
                        for alt in row["alt_names"]
                        if canonical_compare(alt) != canonical_compare(row["name"])
                    ))
                ) + "]"
            ) if any(canonical_compare(alt) != canonical_compare(row["name"]) for alt in row["alt_names"]) else "",
            axis=1
        )
    )
    #print(df_to_show)

    # Specify the columns you want to show
    columns_to_show = ["name","cid", "dist","dist_err", "Hazards"]  # original column names

    columns_to_export = ["name","cid","smiles", "dist","dist_err", "Hazard Categories","meta"]

    df_to_show.loc[df_to_show.index[0], "name"] = (
    "Reference: " + df_to_show.loc[df_to_show.index[0], "name"]
    )

    df_to_show["dist"] = df_to_show["dist"].astype(object)
    df_to_show.loc[df_to_show.index[0], "dist"] = (
        "Reference (Dist 0)"
    )

    # Define the display names for the table header
    display_names = {
        "name": "Compound Name",
        "cid": "Pubchem CID",
        "dist": "Distance",
        "dist_err":"Std. Err. Dist.",
        "Hazards": "Potential Hazards (incomplete, mined data)" 
    }


    export_names = {
        "name": "Compound Name",
        "cid": "Pubchem CID",
        "smiles":"SMILES",
        "dist": "Distance",
        "dist_err":"Std. Err. Dist.",
        "Hazard Categories": "Potential Hazard Categories (incomplete)", 
        "meta":"Meta Info"
    }

    
    # Select only those columns and rename them for display
    df_to_show_selected = df_to_show[columns_to_show].rename(columns=display_names)

    df_to_export_selected = df_to_show[columns_to_export].rename(columns=export_names)

    def make_pubchem_link(cid):
        if pd.isna(cid):
            return ""
        return (
            f'<a href="https://pubchem.ncbi.nlm.nih.gov/compound/{int(cid)}" '
            f'target="_blank">{int(cid)}</a>'
        )
    
    def replace_nan(dist_err):
        if np.isnan(dist_err) or pd.isna(dist_err):
            return " - "
        else:
            return dist_err;

    df_to_show_selected["Pubchem CID"] = df_to_show_selected["Pubchem CID"].apply(make_pubchem_link)
    df_to_show_selected["Std. Err. Dist."] = df_to_show_selected["Std. Err. Dist."].apply(replace_nan)

    st.markdown(
        "<p style='color:red; font-weight:bold; font-size:13px; '>"
        "⚠️ This tool relies on AI-generated data that can contain errors. The tool is intended for informational and research purposes only. Users should not rely on it for laboratory safety decisions. Always consult official Safety Data Sheets (SDS) and follow institutional safety protocols. ⚠️"
        "</p>",
        unsafe_allow_html=True
    )
    table_html = df_to_show_selected.to_html(escape=False, index=False, classes="solvent-table")

    if(state):
        st.markdown(table_html, unsafe_allow_html=True)


    # -----------------------
    # Download Buttons
    # -----------------------

    def dataframe_to_latex_document(df: pd.DataFrame,
                                title: str = "Screened Solvents",
                                meta_column: str = "Meta Info") -> bytes:

        df_latex = df.copy()

        df_latex = df_latex.drop(columns=["SMILES"])
        # Extract Meta Info (assumed constant)
        meta_info = ""
        if meta_column in df_latex.columns:
            meta_info = str(df_latex[meta_column].iloc[0])
            df_latex = df_latex.drop(columns=[meta_column])

        # Create LaTeX table
        latex_table = df_latex.to_latex(
            index=False,
            escape=True,
            caption=f"Screened solvents. {meta_info}",
            label="tab:screened_solvents"
        )

        return latex_table.encode("utf-8")


    st.markdown("### Export Data")

    csv_data = df_to_export_selected.to_csv(index=False).encode("utf-8")
    

    col_csv, col_ltx, col_xlsx = st.columns(3)
    with col_csv:
        st.download_button("📄 Download CSV", csv_data, "screened_solvents.csv", "text/csv",disabled=(not reference_input))

    with col_ltx:
        latex_data = dataframe_to_latex_document( df_to_export_selected)
        st.download_button(
            "📄 Download LaTeX",
            latex_data,
            "screened_solvents.tex",
            "application/x-tex",
            disabled=(not reference_input)
        )



    excel_buffer = BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_to_export_selected.to_excel(
            writer,
            index=False,
            sheet_name="Screened_Solvents"
        )

        worksheet = writer.sheets["Screened_Solvents"]

        # ---- Fixed column width ----
        fixed_width = 35  # adjust as needed
        for idx, c in enumerate(df_to_export_selected.columns, start=1):
            col_letter = get_column_letter(idx)
            if(c=="Meta Info"):
                worksheet.column_dimensions[col_letter].width = fixed_width*10
            else:
                worksheet.column_dimensions[col_letter].width = fixed_width

        # ---- Increase title row height ----
        worksheet.row_dimensions[1].height = 30  # adjust as needed

        # Optional: center-align header text
        for cell in worksheet[1]:
            cell.alignment = Alignment(horizontal="left", vertical="center")

    excel_data = excel_buffer.getvalue()

    with col_xlsx:
        st.download_button(
        "📊 Download Excel",
        excel_data,
        "screened_solvents.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        disabled=(not reference_input)
        )


    # -----------------------
    # Settings AFTER table
    # -----------------------
    st.markdown("### Settings")

    cols = st.columns(3)

    with cols[0]:
        st.number_input(
            "Number of alternative solvents to display",
            min_value=1,
            max_value=100,
            step=1,
            key="num_to_show",
            on_change=refresh_table
        )


    with cols[1]:
        st.selectbox(
        "Distance Metric:",
        ["Euclidean", "Mahalanobis", "Kullback–Leibler divergence"],
        key="distance_kind"
        )

    with cols[2]:
        #st.markdown("App accompanying the Publication 'A customizable green solvent screening tool for emerging materials via transfer learning with Gaussian Processes, Foundational Models and Attention fusion' DOI")
        st.number_input(
            "Show only the top (%) of certainty",
            min_value=0,
            max_value=100,
            step=1,
            key="rel_uncert",
            on_change=refresh_table,
            disabled= not st.session_state.distance_kind == "Euclidean"
        )

# Initialize session state for acknowledgment
if 'acknowledged' not in st.session_state:
    st.session_state.acknowledged = False
if 'declined' not in st.session_state:
    st.session_state.declined = False

# Disclaimer text
disclaimer_text = """

⚠️ This tool relies on AI-generated data that can contain errors. The tool is intended for informational and research purposes only. Users should not rely on it for laboratory safety decisions. Always consult official Safety Data Sheets (SDS) and follow institutional safety protocols. ⚠️

I understand this tool is **not for laboratory use** and I will consult **official Safety Data Sheets (SDS)** 
before using any chemicals.
"""


# If declined, show subtle message
if st.session_state.declined:
    st.info("You have chosen not to acknowledge the disclaimer. The tool is unavailable for use.")


# Show disclaimer with options
if not st.session_state.acknowledged and not st.session_state.declined:
    st.title("⚠️ Safety Disclaimer")
    st.write(disclaimer_text)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("I Acknowledge"):
            st.session_state.acknowledged = True
            st.rerun()  # Immediately rerun script

    with col2:
        if st.button("I Do Not Acknowledge"):
            st.session_state.declined = True
            st.rerun()

# If acknowledged, show main app
if st.session_state.acknowledged:
    initApp();
