import pandas as pd
import requests


def main(single_file):
    single_df = pd.read_csv(single_file, index_col='Unnamed: 0')
    base_url = 'https://property.spatialest.com/nc/brunswick/api/v1/recordcard/'
    property_details_df = pd.DataFrame()
    for row in range(single_df.shape[0]):
        print(row)
        parcel = single_df.iloc[row]
        try:
            req = requests.get(base_url + parcel["Parcel"])
        except TypeError:
            print(f"tried to request row {row}, got parcel {parcel['Parcel']} instead...")

        if req.status_code == 200:
            property_dict = req.json()['parcel']['sections'][0][1][0]
            try:
                building_details = req.json()['parcel']['sections'][1][0][0]
                property_dict.update(building_details)
                try:
                    property_details_df.loc[len(property_details_df)] = property_dict
                except ValueError:
                    property_details_df = pd.DataFrame(columns=list(property_dict.keys()))
                    property_details_df.loc[len(property_details_df)] = property_dict
                property_details_df.to_csv('property_details.csv')
            except:
                print(f"row: {row} seems like an empty plot with value {property_dict['TotalMarketValue']}")

if __name__ == "__main__":
    main(single_file="../async/single_unit_compiled.csv")
