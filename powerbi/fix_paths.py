"""
fix_paths.py ? Run this ONCE if the dashboard shows "Could not find a part of the path" errors.

HOW TO USE:
  1. Open a terminal / command prompt in this folder (powerbi/)
  2. Run:  python fix_paths.py
  3. Re-open dashboard.pbip in Power BI Desktop and click Refresh
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "Data")
DATASET_CSV = os.path.join(DATA_DIR, "Dataset.csv")
FEATURES_CSV = os.path.join(DATA_DIR, "customer_features.csv")
DATASET_TMDL = os.path.join(HERE, "dashboard.SemanticModel", "definition", "tables", "Dataset.tmdl")
FEATURES_TMDL = os.path.join(HERE, "dashboard.SemanticModel", "definition", "tables", "CustomerFeatures.tmdl")

def update_tmdl(tmdl_path, new_path):
    if not os.path.exists(tmdl_path):
        return False
    with open(tmdl_path, encoding="utf-8") as f:
        content = f.read()
    csv_filename = os.path.basename(new_path)
    safe_replacement = f'File.Contents("{new_path}")'.replace("\\", "\\\\")
    new_content = re.sub(r'File\.Contents\("([^"]*' + re.escape(csv_filename) + r')"\)', safe_replacement, content)
    if new_content != content:
        with open(tmdl_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

def main():
    print("=" * 60)
    print("  Power BI Dashboard ? Data Path Fix Utility")
    print("=" * 60)
    if not os.path.exists(DATASET_CSV) or not os.path.exists(FEATURES_CSV):
        print("ERROR: CSV files missing in Data/ folder.")
        sys.exit(1)
    
    ch1 = update_tmdl(DATASET_TMDL, DATASET_CSV)
    ch2 = update_tmdl(FEATURES_TMDL, FEATURES_CSV)
    print(f"Dataset.tmdl         : {'UPDATED' if ch1 else 'already pointing to local path'}")
    print(f"CustomerFeatures.tmdl: {'UPDATED' if ch2 else 'already pointing to local path'}")
    print("\nReady! You can now open dashboard.pbip in Power BI Desktop.")

if __name__ == "__main__":
    main()
