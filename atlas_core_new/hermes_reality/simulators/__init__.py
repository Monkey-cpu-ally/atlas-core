from .rf_harvest import simulate as sim_rf
from .flagella_swimmer import simulate as sim_flagella

SIM_MAP = {
    "rf_energy": sim_rf,
    "robotics": sim_flagella,
    "biomed": sim_flagella,
}
