# Multimeter
import pyvisa

class Keithley2000Controller:
    def __init__(self, resource: str, nplc: float = 10, volt_range: float = 10):
        self.rm   = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout           = 5000
        self.inst.write_termination = "\n"
        self.inst.read_termination  = "\n"
        self._initialize(nplc, volt_range)

    def _initialize(self, nplc: float, volt_range: float):
        self.inst.write("*RST")
        self.inst.write("*CLS")
        self.inst.write(":SENS:FUNC 'VOLT:DC'")
        self.inst.write(f":SENS:VOLT:DC:NPLC {nplc}")
        self.inst.write(f":SENS:VOLT:DC:RANG {volt_range}")

    def measure_voltage(self) -> float:
        """Trigger & return a DC‐voltage reading (in volts)."""
        return self.inst.query_ascii_values(":READ?")[0]

