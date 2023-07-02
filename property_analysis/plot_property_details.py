import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as scipy

property_details_df = pd.read_csv("./property_details.csv")
property_details_df["TotalBaths"] = property_details_df['BathCountTotal']+ 0.5*property_details_df['HalfBathCountTotal']

plt.figure()
property_details_df = property_details_df.loc[property_details_df["BedroomCountTotal"]>0]
plt.scatter(property_details_df["BedroomCountTotal"],property_details_df["TotalMarketValue"])
plt.title("Total Market Value vs # Bedrooms")

plt.figure()
sorted = property_details_df.sort_values(by=['HeatedAreaCard'])
property_details_df = property_details_df.loc[property_details_df["BedroomCountTotal"]>0]
plt.scatter(sorted["HeatedAreaCard"], sorted["TotalMarketValue"])
plt.title("Total Market Value vs Sq ft")

plt.figure()
plt.scatter(property_details_df["TotalMarketValue"], property_details_df["BuildingValue"])
plt.scatter(property_details_df["TotalMarketValue"], property_details_df["LandValue"], alpha=0.6)
plt.legend(["Total v Building", "Total v Land"])
plt.title("Value")

plt.figure()
plt.scatter(property_details_df["TotalMarketValue"], property_details_df["BedroomCountTotal"])
plt.scatter(property_details_df["TotalMarketValue"], property_details_df["TotalBaths"], alpha=0.6)
plt.legend(["Total v Bedrooms", "Total v Baths"])
plt.title("Value Bed/Bath")

plt.figure()
plt.scatter(property_details_df["BedroomCountTotal"],property_details_df["TotalBaths"])
plt.title("Beds vs Baths")

plt.figure()
plt.scatter(property_details_df["BedroomCountTotal"]/property_details_df["TotalBaths"], property_details_df["TotalMarketValue"])
plt.title("Bed Bath Ratio vs Market Value")

plt.figure()
plt.hist(property_details_df["BedroomCountTotal"]/property_details_df["TotalBaths"], bins=50)
plt.title("Bed to Bath Ratio Population")

plt.figure()
sorted = property_details_df.sort_values(by=['ActualYearBuilt'])
plt.scatter(sorted["ActualYearBuilt"], sorted["TotalMarketValue"])
plt.title("Year Built vs Market Value")

plt.figure()
plt.hist(sorted["ActualYearBuilt"], bins=100)
plt.title("Year Built Population")

plt.figure()
counts, bins, _ = plt.hist(property_details_df["TotalMarketValue"], bins=100)
std_dev = np.std(property_details_df["TotalMarketValue"])
plt.vlines(x=np.median(property_details_df["TotalMarketValue"]), ymin=0, ymax=70, color='r', linestyles='--')
plt.vlines(x=np.mean(property_details_df["TotalMarketValue"]), ymin=0, ymax=70, color='g', linestyles='--')
bin_mode = bins[np.where(counts==max(counts))[0]][0]
plt.vlines(x=bin_mode, ymin=0, ymax=70, color='purple', linestyles='--')
plt.legend(["Median Value", "Mean Value", "Histogram Max Value", "Property Tax Values"])
plt.title("Property Value Population")

print(f'Median home value:{np.median(property_details_df["TotalMarketValue"])}')
print(f'Average home value:{np.mean(property_details_df["TotalMarketValue"])}')

print(f'Median home value:{np.median(property_details_df["BedroomCountTotal"])}')
print(f'Average home value:{np.mean(property_details_df["BedroomCountTotal"])}')

print(f'Median sqft:{np.median(property_details_df["HeatedAreaCard"])}')
print(f'Average sqft:{np.mean(property_details_df["HeatedAreaCard"])}')


plt.show()