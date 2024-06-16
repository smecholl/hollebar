import processDataFromCSV

if __name__ == "__main__":
    cocktails, ingredients = processDataFromCSV.process_csv()

    available_cocktails = processDataFromCSV.filter_available_cocktails(cocktails)

    sorted_cocktails = processDataFromCSV.sort_categories(available_cocktails)

# Process each cocktail
for cocktail in sorted_cocktails.values():
    if isinstance(cocktail, dict):  # Ensure it's a dictionary
        processDataFromCSV.create_cocktail(cocktail)
    else:
        print(f"Unexpected data structure: {cocktail}")
