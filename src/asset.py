import logging

logger = logging.getLogger(__name__)

class Asset:
    
    LOW_LIMIT = 100 # Load Limit for assets
    HIGH_LIMIT = 150 # Load Limit for assets
    asset_count = 0 # Count of assets

    def __init__(self, name, loads): # Asset object
        self.name = name
        self.loads = loads

        Asset.asset_count += 1

    def __str__(self): # Für die Ausgabe von print(asset)
        return f"{self.name}: {self.loads}"
    
    def __repr__(self):
        return (f"Asset(name='{self.name}', loads={self.loads})")

    def average_load(self): # Calculate average load of asset
        if len(self.loads) < 1:
            return None 
        else:
            return sum(self.loads) / len(self.loads)
    
    def minimum_load(self): # return min. load of asset
        if len(self.loads) < 1:
            return None 
        else:
            return min(self.loads)
    
    def maximum_load(self): # return max. load of asset
        if len(self.loads) < 1:
            return None 
        else:
            return max(self.loads)
    
    def classification(self): # Classify loads in low, normal and high load
        
        amount_low = 0
        amount_normal = 0
        amount_high = 0

        for load in self.loads:
            if load < Asset.LOW_LIMIT:
                amount_low += 1
            elif Asset.LOW_LIMIT <= load <= Asset.HIGH_LIMIT:
                amount_normal += 1
            elif load > Asset.HIGH_LIMIT:
                amount_high += 1

        return amount_low, amount_normal, amount_high 
    
    def report(self): # Create report for defined asset with classification of loads and average, min. and max. load - print error if not enough loads are available
                
        if len(self.loads) >= 1:
            low, normal, high = self.classification()

            print(f"Asset: {self.name}")
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
    def from_csv_row(cls, row): # read name and asset data from csv file 

        name = row["Asset"]
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
    def from_server(cls, name, asset_data): # read name and asset data from server

        loads = asset_data["Loads"]

        return cls(name, loads)
    



