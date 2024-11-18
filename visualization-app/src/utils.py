import pandas as pd

def validate_data(df):
    """Validate the uploaded data"""
    if df.empty:
        return False
    if len(df.columns) < 2:
        return False
    return True

def process_data(df):
    """Process and clean the data"""
    # Remove any completely empty rows or columns
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    
    # Convert numeric columns to appropriate types
    for col in df.select_dtypes(include=['object']).columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass
            
    return df