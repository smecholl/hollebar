import csv
import os
from datetime import datetime
from collections import defaultdict

def process_csv():
    csv_folder = 'csv_handover'
    file_path = None
    for file_name in os.listdir(csv_folder):
        if file_name.startswith('cocktails') and file_name.endswith('.csv'):
            file_path = os.path.join(csv_folder, file_name)
            break

    if file_path is None:
        print("No 'cocktails' CSV file found in the 'csv_handover' subfolder.")
        return [], []

    cocktails = []
    ingredients = []
    ingredient_availability = {} 
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='|')
        lines = list(reader)

        # Skip the header
        idx = 1
        
        # Find the separator line (====) and process ingredients first
        while idx < len(lines) and lines[idx][0] != '=====':
            idx += 1
        
        # Skip the separator line (====)
        idx += 1
        
        # Process ingredients
        while idx < len(lines):
            row = lines[idx]
            ingredient = {
                'name': row[0],
                'available': int(row[1])  # Directly use the value as 0 or 1
            }
            ingredients.append(ingredient)
            ingredient_availability[row[0]] = ingredient['available']
            idx += 1
              
        # Process cocktails
        idx = 1  # Skip the header
        while idx < len(lines) and lines[idx][0] != '=====':
            row = lines[idx]
            cocktail = {
                'name': row[0],
                'glass': row[3],
                'alternative_glass': row[4],
                'category': row[1],
                'alternative_category': row[2],
                'ingredients': [
                    {'name': row[6], 'amount': row[5]},
                    {'name': row[8], 'amount': row[7]},
                    {'name': row[10], 'amount': row[9]},
                    {'name': row[12], 'amount': row[11]},
                    {'name': row[14], 'amount': row[13]},
                    {'name': row[16], 'amount': row[15]},
                    {'name': row[18], 'amount': row[17]},
                    {'name': row[20], 'amount': row[19]},
                    {'name': row[22], 'amount': row[21]},
                    {'name': row[24], 'amount': row[23]}
                ],
                'popularity': row[25],
                'sweetness': row[26],
                'fruitiness': row[27],
                'sourness': row[28],
                'alcohol_relative': row[29],
                'alcohol_absolute': row[30],
                'bitterness': row[31],
                'recipe': row[32],
                'appereance_type': row[33],
                'short_description': row[34],
                'author': row[35],
                'subtitle': row[36],
                'subtext': row[37],
                'history': row[38],
                'ingredients_available': False
            }

            # Check if all ingredients are available
            for ingredient in cocktail['ingredients']:
                if ingredient['name']:
                    availability = ingredient_availability.get(ingredient['name'], 0)
            cocktail['ingredients_available'] = all(ingredient_availability.get(ingredient['name'], 0) == 1 for ingredient in cocktail['ingredients'] if ingredient['name'])


            cocktails.append(cocktail)
            idx += 1

    return cocktails, ingredients


def filter_available_cocktails(cocktails):
    cocktailsAvailable = [cocktail for cocktail in cocktails if cocktail['ingredients_available']]
    return cocktailsAvailable


def sort_categories(available_cocktails):
    # Convert the list of cocktails into a dictionary
    categorized_cocktails = {i: cocktail for i, cocktail in enumerate(available_cocktails)}

    for _ in range(5):
        # Count the number of cocktails in each category and alternative category
        category_counts = defaultdict(int)
        alternative_category_counts = defaultdict(int)
        for cocktail in categorized_cocktails.values():
            category_counts[cocktail['category']] += 1
            if cocktail['alternative_category']:
                alternative_category_counts[cocktail['alternative_category']] += 1

        # Switch category and alternative category if condition is met
        for cocktail in categorized_cocktails.values():
            if (category_counts[cocktail['category']] + 1) < alternative_category_counts[cocktail['alternative_category']]:
                cocktail['category'], cocktail['alternative_category'] = cocktail['alternative_category'], cocktail['category']

    # Recount categories after possible switches
    category_counts = defaultdict(int)
    for cocktail in categorized_cocktails.values():
        category_counts[cocktail['category']] += 1

    # Move cocktails in categories with one or two cocktails to 'Sonstige'
    for cocktail in categorized_cocktails.values():
        if category_counts[cocktail['category']] <= 2:
            cocktail['category'] = 'Sonstige'

    return categorized_cocktails


def write_index(categorized_cocktails):
    html_content = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <title>Hollebar</title>
        <link href="styles.css" rel="stylesheet">
    </head>
    <body>

        <nav class="navbar">
            <div class="navbar-container">
                <a class="navbar-brand" href="#">
                    <img src="assets/heidelberger.png" alt="Brand Logo" width="70" height="70">
                </a>
                <h1>Hollebar</h1>
                <div></div> <!-- Placeholder div to ensure centering of h1 -->
            </div>
        </nav>

        <div class="accordion" id="accordionExample">
    """

    # Group cocktails by category
    grouped_cocktails = defaultdict(list)
    for cocktail in categorized_cocktails.values():
        grouped_cocktails[cocktail['category']].append(cocktail)

    # Generate HTML content for each category and its cocktails
    for category, cocktails in grouped_cocktails.items():
        html_content += f"""
        <div class="accordion-item">
            <h2 class="accordion-header" id="heading{category}">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{category}" aria-expanded="false" aria-controls="collapse{category}">
                    {category}
                </button>
            </h2>
            <div id="collapse{category}" class="accordion-collapse collapse" aria-labelledby="heading{category}" data-bs-parent="#accordionExample">
                <div class="accordion-body">
                    <div class="container">
                        <div class="row">
        """

        for cocktail in cocktails:
            if isinstance(cocktail, dict):
                ingredients = ", ".join([ingredient['name'] for ingredient in cocktail['ingredients'] if ingredient['name']])
                html_content += f"""
                <div class="col-md-6">
                    <div class="row">
                        <h2>{cocktail['name']}</h2>
                        <div class="col-4 text-end">
                            <img src="assets/heidelberger.png" alt="Heidelberger" class="img-fluid">
                        </div>
                        <div class="col-8">
                            <p>{ingredients}</p>
                        </div>
                    </div>
                </div>
                """
            else:
                print(f"Unexpected data structure for cocktail: {cocktail}")

        html_content += """
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

    html_content += """
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)
