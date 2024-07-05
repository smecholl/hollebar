import os
import csv
import re

# Define the root folder and the subfolder containing HTML files
root_folder = '.'
html_folder = os.path.join(root_folder, 'cocktails')
csv_files = ['simplifiedNames_cocktails.csv', 'simplifiedNames_rest.csv']

# Read the replacement strings from the CSV files
replacements = {}
for csv_file in csv_files:
    csv_file_path = os.path.join(root_folder, csv_file)
    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row if there is one
        for row in reader:
            replacements[row[1]] = row[0]  # {string_to_replace: replacement_string}

# Function to replace the first occurrence of each string within <p> tags
def replace_with_link(html_content, replacements):
    def replace_in_paragraph(match):
        paragraph = match.group(0)
        for to_replace, replacement in replacements.items():
            # Replace only the first occurrence of the string within the paragraph
            if to_replace in paragraph:
                link = f'<a href="/cocktails/{replacement}.html">{to_replace}</a>'
                paragraph = paragraph.replace(to_replace, link, 1)
                break
        return paragraph

    # Use regex to find all <p>...</p> blocks and apply the replacement function
    return re.sub(r'<p>.*?</p>', replace_in_paragraph, html_content, flags=re.DOTALL)

# Process each HTML file in the /cocktails subfolder
for filename in os.listdir(html_folder):
    if filename.endswith('.html'):
        html_file_path = os.path.join(html_folder, filename)
        
        # Read the HTML content
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Replace the strings within <p> tags
        updated_content = replace_with_link(html_content, replacements)
        
        # Write the updated content back to the HTML file
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

print("Replacement completed.")
