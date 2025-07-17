## CSV logging of sweeps and appending parameters
import csv
from typing import List, Tuple, Dict

class CsvLogger:
    def save(self, path: str, data: List[Tuple[float, float]]):
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['current_A', 'voltage_V'])
            for I, V in data:
                writer.writerow([I, V])

    def append_params(self, path: str, params: Dict[str, float]):
        with open(path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([])
            writer.writerow(['Calculated Parameters'])
            for key, val in params.items():
                writer.writerow([key, val])