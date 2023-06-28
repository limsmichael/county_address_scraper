import asyncio
import file_helpers


class Getter:
    def __init__(self, filepath):
        self.file = filepath
        self.single_unit_df, self.multi_unit_df = file_helpers.csv_to_df("../Addresses.csv")
        self.baseurl = "https://property.spatialest.com/nc/brunswick#/property/220JB011"
        self.curr_val = 0

    async def get_next_parcel(self, queue: asyncio.Queue):
        for value in range(self.single_unit_df.shape[0]):
            parcel = self.single_unit_df.iloc[value]
            index = self.single_unit_df.index[value]
            await queue.put((parcel, index))
            self.curr_val=value

        multi_unit_unique = self.multi_unit_df["ST_ADDR_UNITLESS"].unique()
        for value in range(multi_unit_unique.shape[0]):
            parcel = multi_unit_unique[value]
            index = value
            await queue.put((parcel, value))
            self.curr_val = value

    async def run(self, queue: asyncio.Queue):
        await self.get_next_parcel(queue)
        # await queue.join()

