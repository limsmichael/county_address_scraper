import pandas as pd

def main(property_file):
    property_details_df = pd.read_csv(property_file, index_col='Unnamed: 0')
    for column in property_details_df.columns:
        if type(property_details_df[column][0]) is not str:
            pass
        elif "$" in property_details_df[column][0]:
            property_details_df[column] = property_details_df[column].str.replace("$", "")
            property_details_df[column] = property_details_df[column].str.replace(",", "")
            property_details_df[column] = pd.to_numeric(property_details_df[column])
        elif "sqft" in property_details_df[column][0]:
            property_details_df["HeatedAreaCard"] = property_details_df["HeatedAreaCard"].str.replace(' sqft', '')
            property_details_df["HeatedAreaCard"] = property_details_df["HeatedAreaCard"].str.replace(',', '')
            property_details_df["HeatedAreaCard"] = pd.to_numeric(property_details_df["HeatedAreaCard"])

    property_details_df.to_csv(property_file)

if __name__ == "__main__":
    main(property_file= "./property_details.csv")