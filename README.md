# Bald Head Island Address Scraper
Make sure to check out the property analysis too!

[Link to Analysis](./property_analysis/README.md)
## Goal:
A company in Bald Head Island wanted to scrape mailing addresses from county records and match them to local parcels in order to send advertisements.  The goal was to determine the proper mailing address for each record in the County tax parcels and place them into an excel file with the following format

```commandline
1. Local street #
2. Local street name
3. Owner's first name
4. Owner's last name
5. Mailing street number
6. Mailing street name
7. comments/questions
```

### Step 1
Get a list of all of the addresses in the County.  Luckily this is available through the county tax assessor in a *.csv.

### Step 2
Separate the single unit addresses from the multi-unit addresses.  This needed to be done because multi-unit addresses have to be associated by their parcel and unit number since the county does not track unit numbers

### Step 3
Use Selenium to input all of the addresses and associate parcel numbers with the addresses. Find the search box, enter the search address.
For single units this is simple as there should only be one parcle.
For multi-units the addresses must be sorted by the unit and then assigned the parcels

### Step 4 Get Property from Parcel

Find the property and grab the mailing address info by pulling the json data from a separate API url

### Step 5 
Parse the name and address info.  If there were only private owners, this would be simple.  Since this is a beach island, there are also companies that own and manager properties.  These properties contain `llc` in the name.  We must find and separate that to make sure that does not get split into First/Last name.
We must also handle PO boxes and mailing addresses to other multi-unit properties