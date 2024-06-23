import csv
import os
from datetime import datetime
from collections import defaultdict
import unicodedata
import re

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
    cocktailsAvailable = [cocktail for cocktail in cocktails if cocktail['ingredients_available'] and cocktail.get('appearance_type') != 'versteckt']
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
        <!-- Font Awesome CSS -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <!-- Placeholder for Navbar -->
        <div id="navbar-placeholder"></div>

        <!-- Wrapper for centering content and adding side images -->
        <div class="wrapper">
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
                simplified_name = simplify_string(cocktail['name'])
                photo_path = f"/cocktails/photos/{simplified_name}.png"

                img_src = photo_path if os.path.exists(f"cocktails/photos/{simplified_name}.png") else "assets/empty_glass.png"

                html_content += f"""
                <div class="col-md-6">
                    <div class="row">
                        <h2><a href="/cocktails/{simplified_name}.html">{cocktail['name']}</a></h2>
                        <div class="col-4 d-flex justify-content-center">
                            <a href="/cocktails/{simplified_name}.html">
                                <img src="{img_src}" alt="{cocktail['name']}" class="img-fluid custom-size-small">
                            </a>
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
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
        <script src="navbar.js"></script>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)


def simplify_string(input_string):
    replacements = {
        'ö': 'o', 'ü': 'u', 'ä': 'a', 'ß': 'ss', 'ñ': 'n', 'ç': 'c',
        # Add other replacements as necessary
    }
    for original, replacement in replacements.items():
        input_string = input_string.replace(original, replacement)
    
    normalized_string = unicodedata.normalize('NFD', input_string)
    ascii_string = normalized_string.encode('ascii', 'ignore').decode('utf-8')
    simplified_string = re.sub(r'[^a-z0-9]', '', ascii_string.lower())
    
    return simplified_string

def generate_img_tag(cocktail_name):
    simplified_name = simplify_string(cocktail_name)
    photo_path = f"/cocktails/photos/{simplified_name}.png"
    
    # Check if the file exists
    if os.path.exists(f"cocktails/photos/{simplified_name}.png"):
        img_src = photo_path
    else:
        img_src = "assets/empty_glass.png"
    
    return f'<img src="{img_src}" alt="Leeres Glas" class="img-fluid custom-size-small">'


def create_cocktail(cocktail, output_dir="cocktails"):
    def simplify_string(input_string):
        replacements = {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 'ñ': 'n', 'ç': 'c',
            ' ': '', "'": '', '"': '', '/': '', '\\': '', '&': 'and'
        }
        simplified = input_string.lower()
        for search, replace in replacements.items():
            simplified = simplified.replace(search, replace)
        simplified = ''.join(e for e in simplified if e.isalnum())
        return simplified

    simplified_name = simplify_string(cocktail['name'])
    file_name = f"{simplified_name}.html"
    file_path = os.path.join(output_dir, file_name)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{cocktail['name']}</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
        <!-- Custom CSS -->
        <link href="../styles.css" rel="stylesheet">
        <!-- Font Awesome CSS -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <!-- Placeholder for Navbar -->
        <div id="navbar-placeholder"></div>

        <!-- Wrapper for centering content and adding side images -->
        <div class="wrapper">
            <!-- Page Content -->
            <div class="container mt-5">
                <h1>{cocktail['name']}</h1>
                <h2 class="text-muted">
                    {cocktail['short_description']}
                    {f" von {cocktail['author']}" if cocktail['author'] else ""}
                </h2>
                <div class="row mt-4">
                    <!-- First 6 Columns -->
                    <div class="col-md-6">
                        <div class="row">
                            <div class="col-4 d-flex justify-content-center">
                                <img src="/cocktails/photos/{simplified_name}.png" alt="{cocktail['name']}" class="img-fluid custom-size-big" onerror="this.onerror=null;this.src='/assets/empty_glass.png';">
                            </div>
                            <div class="col-4 text-end">
                                <ul class="list-unstyled">
    """
    for ingredient in cocktail['ingredients']:
        if ingredient['amount']:
            html_content += f"<li>{ingredient['amount']}</li>\n"

    html_content += """
                                </ul>
                            </div>
                            <div class="col-4">
                                <ul class="list-unstyled">
    """
    for ingredient in cocktail['ingredients']:
        if ingredient['name']:
            html_content += f"<li>{ingredient['name']}</li>\n"

    html_content += """
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- Last 6 Columns -->
                    <div class="col-md-6">
                        <div class="row">
                            <div class="col-6 text-end">
                                <ul class="list-unstyled">
                                    <li>Bekanntheit:</li>
                                    <li>Süße:</li>
                                    <li>Fruchtigkeit:</li>
                                    <li>Säure:</li>
                                    <li>Bitterkeit:</li>
                                    <li>Stärke:</li>
                                </ul>
                            </div>
                            <div class="col-6">
                                <ul class="list-unstyled">
    """

    for attribute in ['popularity', 'sweetness', 'fruitiness', 'sourness', 'bitterness', 'alcohol_relative']:
        value = int(cocktail[attribute]) if cocktail[attribute] else 0
        html_content += "<li>\n"
        for i in range(3):
            if i < value:
                html_content += '<i class="fas fa-martini-glass-citrus dark-blue"></i>\n'
            else:
                html_content += '<i class="fas fa-martini-glass light-grey"></i>\n'
        html_content += "</li>\n"

    html_content += f"""
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
    <!-- Subtitle Section -->
    {f"<div class='container mt-5'><h2>{cocktail['subtitle']}</h2></div>" if cocktail['subtitle'] else ""}

            <!-- Subtext Section -->
            {f"<div class='container mt-5'><p>{cocktail['subtext']}</p></div>" if cocktail['subtext'] else ""}

            <!-- History Section -->
            {f"<div class='container mt-5'><h2>Historisches</h2><p>{cocktail['history']}</p></div>" if cocktail['history'] else ""}
        </div>

        <!-- Bootstrap JS and Popper.js -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
        <!-- Include Navbar JS with relative path -->
        <script src="../navbar.js"></script>
    </body>
    </html>
    """


    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)


def create_cocktail_of_the_day(categorized_cocktails, output_dir="."):
    file_path = os.path.join(output_dir, "cocktailoftheday.html")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cocktail des Tages</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
        <!-- Custom CSS -->
        <link href="../styles.css" rel="stylesheet">
        <!-- Font Awesome CSS -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <!-- Placeholder for Navbar -->
        <div id="navbar-placeholder"></div>

        <!-- Wrapper for centering content and adding side images -->
        <div class="wrapper">
            <!-- Page Content -->
    """

    for cocktail in categorized_cocktails.values():
        if isinstance(cocktail, dict):
            if cocktail.get('appereance_type') == 'Cocktail des Tages':
                simplified_name = simplify_string(cocktail['name'])
                html_content += f"""
                    <div class="container mt-5">
                    <h1><a href="/cocktails/{simplified_name}.html">{cocktail['name']}</a></h1>
                    <h2 class="text-muted">
                        {cocktail['short_description']}
                        {f" von {cocktail['author']}" if cocktail['author'] else ""}
                    </h2>
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="row">
                                <div class="col-4 d-flex justify-content-center">
                                    <a href="/cocktails/{simplified_name}.html">
                                        <img src="/cocktails/photos/{simplified_name}.png" alt="{cocktail['name']}" class="img-fluid custom-size-big" onerror="this.onerror=null;this.src='/assets/empty_glass.png';">
                                    </a>
                                </div>
                                <div class="col-4 text-end">
                                    <ul class="list-unstyled">
                """
                for ingredient in cocktail['ingredients']:
                    if ingredient['amount']:
                        html_content += f"<li>{ingredient['amount']}</li>\n"

                html_content += """
                                    </ul>
                                </div>
                                <div class="col-4">
                                    <ul class="list-unstyled">
                """
                for ingredient in cocktail['ingredients']:
                    if ingredient['name']:
                        html_content += f"<li>{ingredient['name']}</li>\n"

                html_content += """
                                    </ul>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="row">
                                <div class="col-6 text-end">
                                    <ul class="list-unstyled">
                                        <li>Bekanntheit:</li>
                                        <li>Süße:</li>
                                        <li>Fruchtigkeit:</li>
                                        <li>Säure:</li>
                                        <li>Bitterkeit:</li>
                                        <li>Stärke:</li>
                                    </ul>
                                </div>
                                <div class="col-6">
                                    <ul class="list-unstyled">
                """
                for attribute in ['popularity', 'sweetness', 'fruitiness', 'sourness', 'bitterness', 'alcohol_relative']:
                    value = int(cocktail[attribute]) if cocktail[attribute] else 0
                    html_content += "<li>\n"
                    for i in range(3):
                        if i < value:
                            html_content += '<i class="fas fa-martini-glass-citrus dark-blue"></i>\n'
                        else:
                            html_content += '<i class="fas fa-martini-glass light-grey"></i>\n'
                    html_content += "</li>\n"

                html_content += f"""
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """

    html_content += """
        </div>

        <!-- Bootstrap JS and Popper.js -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
        <!-- Include Navbar JS with relative path -->
        <script src="../navbar.js"></script>
    </body>
    </html>
    """

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)


 