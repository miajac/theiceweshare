import pandas as pd
from datetime import datetime

def generate_citation(file_id, excel_path="~/Documents/nsidc-scraper/Merged_Metadata.xlsx"):
    """
    Generate NSIDC citation based on Digital File ID.
    
    Parameters:
    file_id (str): The Digital File ID to look up
    excel_path (str): Path to the metadata Excel file
    
    Returns:
    str: Formatted citation
    """
    # Expand the ~ to full path
    excel_path = excel_path.replace('~', '/Users/miajacoombs')
    
    # Read the Excel file
    df = pd.read_excel(excel_path)
    
    # Find the row with matching Digital File ID
    row = df[df['Digital File ID'] == file_id]
    
    if row.empty:
        return f"Error: File ID '{file_id}' not found in metadata."
    
    # Extract data from the row
    row = row.iloc[0]  # Get first matching row
    
    photographer = row['Photographer'] if pd.notna(row['Photographer']) else None
    glacier_name = row['Glacier Name'] if pd.notna(row['Glacier Name']) else "Unknown Glacier"
    photo_number = row['Photograph Number'] if pd.notna(row['Photograph Number']) else "Unknown"
    date_taken = row['Date'] if pd.notna(row['Date']) else None
    
    # Clean up photograph number - remove "Photograph Number" or "Photograph number" prefix if present
    if isinstance(photo_number, str):
        # Case-insensitive replacement
        if "photograph number" in photo_number.lower():
            # Remove the phrase regardless of capitalization
            photo_number = photo_number.replace("Photograph number", "").replace("Photograph Number", "").strip()
            # Remove leading colon or space if present
            photo_number = photo_number.lstrip(': ')
    
    # Format the date
    date_str = ""
    if date_taken:
        date_taken_str = str(date_taken)
        # If contains XX, just use the year (first 4 characters)
        if 'XX' in date_taken_str or 'xx' in date_taken_str:
            date_str = date_taken_str[:4] + ". "
        else:
            date_str = date_taken_str + ". "
    
    # Build citation based on whether photographer exists
    if photographer:
        citation = f"{photographer}. {date_str}[{glacier_name}]. National Snow and Ice Data Center. Photograph Number: {photo_number}. https://nsidc.org. Accessed May 2025."
    else:
        citation = f"National Snow and Ice Data Center. {date_str}[{glacier_name}]. Photograph Number: {photo_number}. https://nsidc.org. Accessed May 2025."
    
    return citation


# Example usage:
if __name__ == "__main__":
    # Test with a file ID
    file_id = input("Enter Digital File ID: ")
    citation = generate_citation(file_id)
    print("\n" + citation)