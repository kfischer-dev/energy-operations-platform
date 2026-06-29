import csv, logging
from src.station import Station

logger = logging.getLogger(__name__)

def read_stations_file(filename):

    try:
        with open(filename, "r") as file:
            
            logger.info(f'File "{filename}" successfully opened.')

            csv_reader = csv.DictReader(file)

            stations = [] # Leere Liste Stations erstellt

            for row in csv_reader:
                
                station = Station.from_csv_row(row)
                logger.debug(f'{station.name} successfully imported from file "{filename}"')
                stations.append(station)

            logger.info(f'Successfully imported {len(stations)} stations from file "{filename}"\n')

        return stations

    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return []
