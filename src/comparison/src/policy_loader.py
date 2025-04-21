import os
import pandas as pd

def load_policies(data_dir="../data"):
    policy_records = []
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.txt'):
            platform_name = filename.replace('.txt', '')
            filepath = os.path.join(data_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as file:
                policy_content = file.read().strip()
            
            policy_records.append({
                "Platform": platform_name,
                "Policy": policy_content
            })
    
    return pd.DataFrame(policy_records)
