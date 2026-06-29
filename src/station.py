import logging

logger = logging.getLogger(__name__)

class Station:
    
    LOW_LIMIT = 100 # Load Limit for stations
    HIGH_LIMIT = 150 # Load Limit for stations
    station_count = 0 # Count of stations

    def __init__(self, name, loads): # Station object
        self.name = name
        self.loads = loads

        Station.station_count += 1

    def __str__(self): # Für die Ausgabe von print(station)
        return f"{self.name}: {self.loads}"
    
    def __repr__(self):
        return (f"Station(name='{self.name}', loads={self.loads})")

    def average_load(self): # Calculate average load of station
        if len(self.loads) < 1:
            return None 
        else:
            return sum(self.loads) / len(self.loads)
    
    def minimum_load(self): # return min. load of station
        if len(self.loads) < 1:
            return None 
        else:
            return min(self.loads)
    
    def maximum_load(self): # return max. load of station
        if len(self.loads) < 1:
            return None 
        else:
            return max(self.loads)
    
    def classification(self): # Classify loads in low, normal and high load
        
        amount_low = 0
        amount_normal = 0
        amount_high = 0

        for load in self.loads:
            if load < Station.LOW_LIMIT:
                amount_low += 1
            elif Station.LOW_LIMIT <= load <= Station.HIGH_LIMIT:
                amount_normal += 1
            elif load > Station.HIGH_LIMIT:
                amount_high += 1

        return amount_low, amount_normal, amount_high 
    
    def report(self): # Create report for defined station with classification of loads and average, min. and max. load - print error if not enough loads are available
                
        if len(self.loads) >= 1:
            low, normal, high = self.classification()

            print(f"Station: {self.name}")
            print()
            print("Classification:")
            print(f"LOW: {low}")
            print(f"NORMAL: {normal}")
            print(f"HIGH: {high}")
            print()
            print(f"Average Load: {self.average_load():.1f}")
            print(f"Min. Load: {self.minimum_load()}")
            print(f"Max. Load: {self.maximum_load()}")
            print()
            logger.info(f"Report created for {self.name}.")
            success = True

        else:
            logger.warning(f"Not enough loads available for {self.name} to create report.")
            success = False
        
        return success

    @classmethod
    def from_csv_row(cls, row): # read name and station data from csv file 

        name = row["Station"]
        loads = []

        for key, value in row.items():

            if key.startswith("Load"):

                if value == "" or value is None: # Check if value "Load" is empty
                    logger.warning(f"{name}: Missing value in {key}.")
                    continue # um weitere gültige Werte zu erfassen
                
                try:
                    loads.append(int(value)) # Wandle jeden String Wert in Integer um und füge ihn in die loads Liste ein

                except ValueError: # Falls Umwandlung nicht klappt - Schreibe Fehler aus und dokumentiere für Fehlerdaten
                    logger.warning(f"{name}: Invalid value '{value}' in {key}.")
                    continue # um weitere gültige Werte zu erfassen

        return cls(name, loads)
    
    @classmethod
    def from_server(cls, name, station_data): # read name and station data from server

        loads = station_data["Loads"]

        return cls(name, loads)
    



