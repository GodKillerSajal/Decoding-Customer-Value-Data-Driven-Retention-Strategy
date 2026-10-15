"""Copy local source and engineered CSVs into the PBIP report's Data folder.

Run from the project root after feature engineering:
    python powerbi/prepare_data.py
"""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "powerbi" / "Data"
SOURCES = {
    ROOT / "Dataset.csv": DATA_DIR / "Dataset.csv",
    ROOT / "project_output" / "python" / "customer_features.csv": DATA_DIR / "customer_features.csv",
}


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for source, destination in SOURCES.items():
        if not source.exists():
            raise FileNotFoundError(f"Missing {source}. Run feature engineering and download Dataset.csv first.")
        shutil.copy2(source, destination)
        print(f"Prepared {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
