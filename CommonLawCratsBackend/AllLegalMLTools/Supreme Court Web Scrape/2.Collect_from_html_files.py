import os
import csv
from bs4 import BeautifulSoup
from shutil import copyfile

input_dir = "data_supreme_court"
output_file = "cases_supreme_final.csv"
missed_dir = "data_missed"

os.makedirs(missed_dir, exist_ok=True)

# Define the CSV header
header = ["Title", "Judge", "Description", "Decision Date", "Case No", "Disposal Nature","case_html_main","case_html"]

cases_data = []

processed_count = 0
missed_count = 0

def process_first_type(soup):
    global missed_count
    try:
        title = soup.find('button').get('aria-label').replace(' pdf', '')
        judge = soup.find('strong').text.replace('Judge : ', '')
        description = soup.find('strong').find_next_sibling(string=True).strip()
        decision_date = soup.find('font', color='green').text
        case_no = soup.find_all('font', color='green')[1].text
        green_fonts = soup.find_all('font', {'color': 'green'})
        disposal_nature = green_fonts[2].text if len(green_fonts) > 2 else ""
        case_html_main = row.find('span', class_='ncDisplay').text
        case_html = row.find('span', class_='escrText').text
        
        return [title, judge, description, decision_date, case_no, disposal_nature,case_html_main,case_html]
    except Exception as e:
        print(f"Error processing first type in file: {input_file}. Error: {e}")
        copyfile(input_file, os.path.join(missed_dir, os.path.basename(input_file)))
        missed_count += 1
        return None

def process_second_type(row):
    global missed_count
    try:
        title = row.find('button', {'role': 'link'}).get_text(strip=True).split(' - ')[0]
        judges = row.find('strong').get_text(strip=True).replace('Judge : ', '')
        description = row.find('strong').find_next_sibling(string=True).strip()
        decision_date = row.find('font', {'color': 'green'}).get_text(strip=True)
        case_no = row.find_all('font', {'color': 'green'})[1].get_text(strip=True)
        green_fonts = row.find_all('font', {'color': 'green'})
        disposal_nature = green_fonts[2].get_text(strip=True) if len(green_fonts) > 2 else ""
        case_html_main = row.find('span', class_='ncDisplay').text
        case_html = row.find('span', class_='escrText').text
        return [title, judges, description, decision_date, case_no, disposal_nature,case_html_main,case_html]
    except Exception as e:
        print(f"Error processing second type in file: {input_file}. Error: {e}")
        copyfile(input_file, os.path.join(missed_dir, os.path.basename(input_file)))
        missed_count += 1
        return None

for filename in os.listdir(input_dir):
    if filename.endswith(".html"):
        input_file = os.path.join(input_dir, filename)
        print(f"Processing file ({processed_count + 1} of {processed_count + missed_count + 1}): {filename}")
        
        with open(input_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            rows = soup.find_all('tr', {'role': 'row'})

            for row in rows:
                if row.find('div', {'class': 'modal fade'}):
                    case_data = process_second_type(row)
                else:
                    case_data = process_first_type(soup)

                if case_data:
                    cases_data.append(case_data)
                    processed_count += 1

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    writer.writerows(cases_data)

print(f"Data from HTML files in {input_dir} has been written to {output_file}.")
print(f"Files processed: {processed_count}")
print(f"Files missed due to errors: {missed_count}")
