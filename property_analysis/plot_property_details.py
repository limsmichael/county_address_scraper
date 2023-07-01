import matplotlib.pyplot as plt
import pandas as pd

property_details_df = pd.read_csv("./property_details.csv")

plt.figure()
property_details_df = property_details_df.loc[property_details_df["BedroomCountTotal"]>0]
plt.scatter(property_details_df["BedroomCountTotal"],property_details_df["TotalMarketValue"])
plt.title("Total Market Value vs # Bedrooms")

plt.figure()
property_details_df["TotalBaths"] = property_details_df['BathCountTotal']+ 0.5*property_details_df['HalfBathCountTotal']
plt.scatter(property_details_df["BedroomCountTotal"],property_details_df["TotalBaths"])
plt.title("Beds vs Baths")

plt.figure()
plt.hist(property_details_df["TotalMarketValue"], bins=100)
plt.title("Property Value Population")

plt.figure()
plt.hist(property_details_df["BedroomCountTotal"], bins=100)
plt.title("Bedroom Population")

plt.show()