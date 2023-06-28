import os
import pandas as pd
import requests


def parse_owner_info(property_info):
    owner_dict = get_owner_name(property_info)
    mailing_dict = get_mailing_address(property_info)

    return owner_dict, mailing_dict


def get_owner_name(property_info):
    if "llc" in property_info["CurrentAccountName1"].lower():
        owner_first_1 = property_info["CurrentAccountName1"]
        owner_last_1 = ""
    else:
        splits = property_info["CurrentAccountName1"].split()
        owner_first_1 = splits[1]
        owner_last_1 = splits[0]
    if (property_info["CurrentAccountName2"] == "") or (property_info["CurrentAccountName2"] == "-"):
        owner_first_2 = ""
        owner_last_2 = ""
    else:
        splits = property_info["CurrentAccountName2"].split()
        owner_first_2 = splits[1]
        owner_last_2 = splits[0]

    data = {
        "Owner_First_1": owner_first_1,
        "Owner_Last_1": owner_last_1,
        "Owner_First_2": owner_first_2,
        "Owner_Last_2": owner_last_2
    }

    return data


def get_mailing_address(property_info):
    splits = property_info["CurrentAccountAddress2"].split()
    try:
        mailing_num = int(splits[0])
        mailing_st = ""
        for subsplit in splits[1:]:
            mailing_st += subsplit + " "
        if property_info["CurrentAccountAddress3"]!="-":
            mailing_st += property_info["CurrentAccountAddress3"]
    except ValueError:
        mailing_num = property_info["CurrentAccountAddress2"]
        mailing_st = ""

    data = {
        "St_Num_Mailing": mailing_num,
        "St_Name_Mailing": mailing_st,
        "City": property_info["CurrentAccountCity"],
        "State": property_info["CurrentAccountState"],
        "Zip": property_info["CurrentAccountZip"]
    }
    return data


def main(single_file, multi_file):
    if not os.path.exists("./total_parcels.csv"):
        single_df = pd.read_csv(single_file, index_col='Unnamed: 0')
        multi_df = pd.read_csv(multi_file, index_col='Unnamed: 0')
        multi_df = multi_df.drop("ST_ADDR_UNITLESS", axis=1)
        total_df = pd.concat([single_df, multi_df])
        total_df.to_csv("./total_parcels.csv")
    else:
        total_df = pd.read_csv("total_parcels.csv", index_col='Unnamed: 0')
    base_url = 'https://property.spatialest.com/nc/brunswick/api/v1/recordcard/'
    bhi_columns = ["St_Num_BHI", "St_Name_BHI", "Owner_First_1", "Owner_Last_1", "Owner_First_1", "Owner_Last_1",
                   "St_Num_Mailing", "St_Name_Mailing",
                   "City", "State", "Zip", "Comments"]
    df_out = pd.DataFrame(columns=bhi_columns)
    for row in range(total_df.shape[0]):
        print(row)
        parcel = total_df.iloc[row]
        if (str(parcel["UNIT_NO"]) == 'nan') or (parcel["UNIT_NO"] == " "):
            st_name = parcel["ST_NAME"]
        else:
            st_name = parcel["ST_NAME"] + " " + parcel["UNIT_NO"]

        if (str(parcel["Parcel"]) == 'nan') or (parcel["Parcel"] == " "):
            data = [parcel["ST_NUMB"], st_name, "", "", "", "", "", "", "", "", "", "Parcel NA"]
            df_out.loc[len(df_out)] = data
            continue
        req = requests.get(base_url + parcel["Parcel"])
        if req.status_code == 200:
            property_info = req.json()["parcel"]["header"]
            owner_dict, mailing_dict = parse_owner_info(property_info)
            data = [parcel["ST_NUMB"], st_name, owner_dict["Owner_First_1"], owner_dict["Owner_Last_1"],
                    owner_dict["Owner_First_2"], owner_dict["Owner_Last_2"],
                    mailing_dict["St_Num_Mailing"], mailing_dict["St_Name_Mailing"],
                    mailing_dict["City"], mailing_dict["State"], mailing_dict["Zip"], ""]
        if req.status_code == 404:
            data = [parcel["ST_NUMB"], st_name, "", "", "", "", "", "", "", "", "", "Parcel NA - Incorrect Parcel"]
            df_out.loc[len(df_out)] = data
            continue
        df_out.loc[len(df_out)] = data
        df_out.to_csv("BHI_parsed_addresses.csv")


if __name__ == "__main__":
    main("./single_unit_compiled.csv", "./multi_unit_compiled.csv")
