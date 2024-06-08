import processDataFromCSV

if __name__ == "__main__":

    cocktails, ingredients = processDataFromCSV.process_csv()

    available_cocktails = processDataFromCSV.filter_available_cocktails(cocktails)

    sorted_cocktails = processDataFromCSV.sort_categories(available_cocktails)

    processDataFromCSV.write_index(sorted_cocktails)
