import csv, logging
from src.asset import Asset

logger = logging.getLogger(__name__)

def read_assets_file(filename):

    try:
        with open(filename, "r") as file:
            
            logger.info(f'File "{filename}" successfully opened.')

            csv_reader = csv.DictReader(file)

            assets = [] # Leere Liste Assets erstellt

            for row in csv_reader:
                
                asset = Asset.from_csv_row(row)
                logger.debug(f'{asset.name} successfully imported from file "{filename}"')
                assets.append(asset)

            logger.info(f'Successfully imported {len(assets)} assets from file "{filename}"\n')

        return assets

    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return []
