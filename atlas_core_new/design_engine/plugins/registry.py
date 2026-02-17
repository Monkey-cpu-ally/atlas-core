from typing import Dict
from .hydracore_power import HydraCorePowerPlugin
from .umoja_armor import UmojaArmorPlugin
from .hermes_pqc import HermesPQCPlugin
from .robot_arm import RobotArmPlugin


def load_plugins() -> Dict[str, object]:
    plugins = [
        HydraCorePowerPlugin(),
        UmojaArmorPlugin(),
        HermesPQCPlugin(),
        RobotArmPlugin()
    ]
    return {p.key: p for p in plugins}
