import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote_plus

base_url = "https://www.kuranmeali.com/Kokler.php"

response = requests.get(base_url)
response.raise_for_status()

soup = BeautifulSoup(response.content, "html.parser")

# Extract letters
fihrist_div = soup.find("div", id="fihrist")
letters = [div.get_text(strip=True) for div in fihrist_div.find_all("div", class_="hurufat")]

# Initialize the list for storing row data
data_rows = []

def extract_row_details(divs, num_columns):
    """Extract details from rows of divs, generalized for any number of columns."""
    all_details = []
    
    for i in range(0, len(divs), num_columns):
        row_divs = divs[i:i+num_columns]  # Get the next 'num_columns' divs to form a row
        
        # Ensure there are enough divs to form a row
        if len(row_divs) >= num_columns:
            # Extract text from each div in the row
            row_data = [div.get_text(strip=True) if div else "" for div in row_divs]
            
            # Append the combined details for this row
            all_details.append(row_data)
    
    return all_details

def fetch_word_details(root, word, letter):
    try:
        root_url = f"https://www.kuranmeali.com/Kokler.php?kok={quote_plus(root)}&harf={quote_plus(letter)}"
        print(f"Fetching details for '{word}' from {root_url}...")
        
        root_response = requests.get(root_url)
        root_response.raise_for_status()
        
        root_soup = BeautifulSoup(root_response.content, "html.parser")
        
        # Navigate to the second level <center> tag and then find all divs
        outer_center_tag = root_soup.find_all("center")
        if len(outer_center_tag) > 1:
            inner_center_tag = outer_center_tag[1]  # Select the second <center> tag
            divs = inner_center_tag.find_all("div", style=True)
        else:
            divs = []

        all_details = []
        
        # Group divs by 7 (or other dynamic column count) to form one row
        num_columns = 8  # Adjust this value as necessary for the number of columns you need
        row_details = extract_row_details(divs, num_columns)
        
        # Add each row of details to the all_details list
        for row in row_details:
            all_details.append(row)
        
        return all_details
    
    except Exception as e:
        print(f"An error occurred while fetching details for '{word}': {e}")
        return []

# Main loop to process each letter
for letter in letters:  # Example: only processing the first letter
    try:
        letter_url = f"{base_url}?harf={letter}"
        print(f"Fetching roots for '{letter}' from {letter_url}...")
        
        letter_response = requests.get(letter_url)
        letter_response.raise_for_status()
        
        letter_soup = BeautifulSoup(letter_response.content, "html.parser")
        
        # Extract roots for the given letter
        roots_divs = letter_soup.find_all("div", style="width:100px;float:right; font-family:Shaikh Hamdullah Mushaf; font-size:22px;")
        
        for div in roots_divs:  # Process the first 3 roots as an example
            root_text = div.get_text(strip=True)
            words = root_text.split(",")  # Split the words by commas
            
            # Fetch details for each word under this root
            for word in words:
                word_details_list = fetch_word_details(root_text, word.strip(), letter)
                
                # Add the details for each word in the list to the data rows
                for word_details in word_details_list:
                    data_rows.append([letter, root_text, word.strip()] + word_details)
        
    except Exception as e:
        print(f"An error occurred while processing letter '{letter}': {e}")

# Create the DataFrame
df = pd.DataFrame(data_rows, columns=["Letter", "Root", "Word"] + [f"c{i}" for i in range(1, 9)])
#remove c1
df = df.drop(columns=["c1"])

print(df.head(10))  # Show the first few rows of the DataFrame

# to csv
df.to_csv("word_details.csv", index=False)
