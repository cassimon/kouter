<p align="center">
  <img src="KouTer_Logo_cropped.svg" alt="KouTer logo" width="180">
</p>

<h1 align="center">KouTer Green Solvents</h1>

KouTer Green Solvents is a Streamlit app for finding alternative solvents. You pick a reference solvent, and the app ranks the other solvents by how close their properties are, using weights you can adjust.

## Running the app

```bash
pip install -r requirements.txt
streamlit run solvent_selector_vectorized.py
```

## Note on data usage

This tool processes publicly available chemical information from external databases.
Safety-related fields (including hazard codes) are included only as raw metadata to support internal filtering and classification logic.
Because these values are mined automatically and may contain inaccuracies, the tool does not display or interpret official hazard statements, nor should it be used for safety assessment.
Users remain responsible for consulting authoritative sources such as official Safety Data Sheets (SDS) for laboratory decisions.

## License

See [LICENSE](LICENSE).
