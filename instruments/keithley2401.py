# Sourcemeter
import pyvisa

class Keithley2401Controller:
    def __init__(self, resource: str):
        self.rm   = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout           = 5000
        self.inst.write_termination = "\n"
        self.inst.read_termination  = "\n"
        self._initialize()

    def _initialize(self):
        self.inst.write("*RST")
        self.inst.write("*CLS")
        self.inst.write(":SYST:RSEN ON")
        self.inst.write(":SOUR:FUNC CURR")
        self.inst.write(":SOUR:CURR:MODE FIXED")
        self.inst.write(":SENS:FUNC 'VOLT'")
        self.inst.write(":OUTP ON")

    def set_compliance(self, comp: float) -> None:
        self.inst.write(f":SENS:VOLT:PROT {comp}")

    def source_current(self, current: float) -> None:
        self.inst.write(f":SOUR:CURR {current}")

    def read(self) -> tuple[float, float]:
        """Return (I_source, V_measured)."""
        raw = self.inst.query(":READ?")
        v, i = map(float, raw.strip().split(',')[:2])
        return i, v

    def output_on(self) -> None:
        self.inst.write(":OUTP ON")

    def output_off(self) -> None:
        self.inst.write(":OUTP OFF")

    def close(self) -> None:
        try:
            self.output_off()
        except:
            pass
        self.inst.close()