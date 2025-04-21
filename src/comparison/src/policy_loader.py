import os
import pandas as pd
import requests

def find_privacy_db_csv():
    """Find the privacy_db.csv file in the project."""
    possible_paths = [
        os.path.join("src", "summary", "privacy_db.csv"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "summary", "privacy_db.csv")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError("Could not find privacy_db.csv file. Please make sure it exists in src/summary/.")

def load_policies(data_dir=None):
    """
    Load policies from privacy_db.csv and fetch their content.
    
    Parameters:
    data_dir: Ignored parameter, kept for backward compatibility.
    
    Returns:
    DataFrame with Platform and Policy columns.
    """
    csv_path = find_privacy_db_csv()
    df = pd.read_csv(csv_path)
    
    # Keep only the Platform and Privacy Policy Txt columns
    policy_records = []
    
    for _, row in df.iterrows():
        platform_name = row["Platform"]
        policy_url = row["Privacy Policy Txt"]
        
        try:
            # Fetch the policy content
            response = requests.get(policy_url)
            response.raise_for_status()
            policy_content = response.text.strip()
            
            policy_records.append({
                "Platform": platform_name,
                "Policy": policy_content
            })
            print(f"✅ Loaded policy for {platform_name}")
        except Exception as e:
            print(f"⚠️ Failed to load policy for {platform_name}: {str(e)}")
    
    return pd.DataFrame(policy_records)
