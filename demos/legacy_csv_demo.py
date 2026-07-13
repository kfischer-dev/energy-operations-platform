import logging
logging.basicConfig(filename="app.log", level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s")

from src.read_documents import read_assets_file
from src.server import new_assets
from src.asset import Asset

# =============================================================
# Import Asset Data from CSV
# =============================================================

doc_name = "data/assets.csv" # csv document with assets
logging.info(f'Asset import from csv file "{doc_name}" started.')

assets = read_assets_file(doc_name) # Read csv file with assets

# =============================================================
# Import Additional Assets from Server
# =============================================================

logging.info('Asset import from Server "192.168.178.1" started.')
server_asset_count = 0 # Amount of Assets from server

for name, asset_data in new_assets.items(): # Import additional Assets from Server
    asset = Asset.from_server(name, asset_data)
    logging.debug(f'{asset.name} successfully imported from Server "192.168.178.1"')
    assets.append(asset)
    server_asset_count += 1

logging.info(f'Successfully imported {server_asset_count} assets from Server "192.168.178.1"\n')

# =============================================================
# Generate Asset Reports
# =============================================================

logging.info("Asset report creation started.")

report = 0
no_report = 0

for asset in assets: # Create Report for all assets
    status = asset.report()
    if status is True:
        report +=1
    else:
        no_report += 1

logging.info(f"Successfully created report for {report} assets.")
logging.info(f"Report creation for {no_report} assets failed.\n")