import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load file IDs
df = pd.read_excel("SampleMetadata_AKGlaciersProj.xlsx")
file_ids = df["File ID"].dropna().astype(str).unique().tolist()

# Batch configuration
BATCH_SIZE = 20
batches = [file_ids[i:i+BATCH_SIZE] for i in range(0, len(file_ids), BATCH_SIZE)]

# Initialize driver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://nsidc.org/data/glacier_photo/search/")

print("\n🌐 Navigating to NSIDC search page...")
input("\n🧝‍♀️ Please manually check the checkbox labeled 'Search by Digital File ID or GLIMS ID'.\n✅ Press Enter here after you've done that...\n")

all_results = []
scraped_ids = set()

for i, batch in enumerate(batches):
    print(f"\n🔍 Processing batch {i+1} ({len(batch)} IDs)")

    try:
        # Open "Define Your Search" dropdown only if not the first batch
        if i > 0:
            dropdown_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="search_arrow"]'))
            )
            dropdown_button.click()
            time.sleep(1)  # Let dropdown expand

        # Find and clear the file ID input
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "digital_file_id_field"))
        )
        search_input.clear()
        search_input.send_keys("\n".join(batch))

        # Click Search
        search_button = driver.find_element(By.XPATH, '//*[@id="searchButtons"]/input[1]')
        search_button.click()

        # Wait for results to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//tr[contains(@id,"_row")]'))
        )
        time.sleep(2)  # Allow full render

        # Scrape rows
        rows = driver.find_elements(By.XPATH, '//tr[contains(@id,"_row")]')
        for row in rows:
            try:
                glacier_name = row.find_element(By.XPATH, './td[3]').text.strip()
                photographer = row.find_element(By.XPATH, './td[4]').text.strip()
                date = row.find_element(By.XPATH, './td[5]').text.strip()
                spatial = row.find_element(By.XPATH, './td[6]').text.strip()
                file_info = row.find_element(By.XPATH, './td[7]').text.strip()

                parts = file_info.split("\n")
                digital_file_id = parts[0].strip() if len(parts) > 0 else ""
                photograph_number = parts[1].strip() if len(parts) > 1 else ""
                glims_id = parts[2].strip() if len(parts) > 2 else ""

                # Avoid duplicates
                if digital_file_id not in scraped_ids:
                    all_results.append({
                        "Digital File ID": digital_file_id,
                        "Photograph Number": photograph_number,
                        "GLIMS Glacier ID": glims_id,
                        "Glacier Name": glacier_name,
                        "Photographer": photographer,
                        "Date": date,
                        "Spatial Coverage": spatial,
                    })
                    scraped_ids.add(digital_file_id)

            except Exception as e:
                print("⚠️ Failed to parse a row:", e)

    except Exception as e:
        print(f"❌ Error during batch {i+1}:", e)

# Save results
if all_results:
    pd.DataFrame(all_results).to_excel("Updated_Metadata.xlsx", index=False)
    print("\n✅ Metadata successfully written to Updated_Metadata.xlsx")
else:
    print("\n❌ No metadata retrieved.")

# Check for missing IDs
updated_df = pd.read_excel("Updated_Metadata.xlsx")
updated_ids = updated_df["Digital File ID"].astype(str).unique().tolist()
missing_ids = sorted(set(file_ids) - set(updated_ids))

if missing_ids:
    print("\n⚠️ The following File IDs were not found in the updated metadata:")
    for mid in missing_ids:
        print(mid)
else:
    print("\n✅ All File IDs accounted for.")

# Close browser
driver.quit()
