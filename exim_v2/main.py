import asyncio
import argparse

from src.controller import BpsExim

async def main(**kwargs):
    await BpsExim(**kwargs).run_process()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="arguments for bps-exim engine")

    parser.add_argument("-l", "--headless", help="Headless mode", action="store_true", default=False)
    parser.add_argument("-ei", "--exim", help="Choose export[e] or import[i]", required=True, choices=["e", "ekspor", "export", "i", "impor" ,"import"], type=str)
    parser.add_argument("-a", "--agregasi", help="Choose Agregasi", required=True, choices=["hs_full", "hs_digit", "negara", "pelabuhan"], type=str)
    parser.add_argument("-b", "--batch", help="Size of Batch", type=int)
    parser.add_argument("-t", "--attempt", help="number of attempts to try again", type=int)

    args = parser.parse_args()  
    kwargs = vars(args)
    asyncio.run(main(**kwargs))