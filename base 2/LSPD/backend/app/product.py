import pandas as pd

# Read the CSV file with the correct delimiter and handle malformed rows
try:
    products_df = pd.read_csv('app/SOP-OTP.csv', delimiter=';')

    # Manually rename columns if necessary
    products_df.columns = [col.strip() for col in products_df.columns]
    products_df.rename(columns={
        'COMMERCIAL_CODE  NAME_PRODUCT': 'COMMERCIAL_CODE',
        'Unnamed: 1': 'NAME_PRODUCT'
    }, inplace=True)
    print("First rows of the CSV file:")
    print(products_df.head())
except pd.errors.ParserError as e:
    print("Error reading the CSV file:", e)
    products_df = pd.DataFrame()  # Create an empty DataFrame in case of error


def get_product_details():
    if 'NAME_PRODUCT' in products_df.columns:
        product_details = {}

        for _, row in products_df.iterrows():
            product_name = row['NAME_PRODUCT'].split(' ')[0].strip('"').strip()
            details = {
                'description': ' '.join(
                    row['NAME_PRODUCT'].split(' ')[1:]
                ).strip('"').strip(),
                'commercial_code': str(row['COMMERCIAL_CODE']).strip()
            }

            if product_name in product_details:
                product_details[product_name].append(details)
            else:
                product_details[product_name] = [details]

        return product_details
    else:
        print("The column 'NAME_PRODUCT' does not exist in the CSV file.")
        return {}


def print_product_details():
    product_details = get_product_details()
    for product, details in product_details.items():
        print(f"Product: {product}")
        for detail in details:
            print(
                f"  - Description: {detail['description']}, "
                f"Commercial Code: {detail['commercial_code']}"
            )
