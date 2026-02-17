"""
atlas_core/bootstrap.py

System bootstrap and demo script.
"""

from atlas_core_new.agents.hermes import Hermes
from atlas_core_new.agents.minerva import Minerva
from atlas_core_new.pipeline.bot_files import ensure_bot_files
from atlas_core_new.bots.profiles import PROFILES


def main():
    hermes = Hermes()
    minerva = Minerva()

    for bot_type in PROFILES.keys():
        ensure_bot_files(bot_type)

    print({"service": "ATLAS CORE", "version": "0.3.1", "bots": list(PROFILES.keys())})

    hermes.enforce("build", {
        "blueprint_exists": True,
        "bot_type": "POSEIDON-BUOY",
        "action": "sense",
        "human_approved": False
    })
    print("POSEIDON-BUOY sense: OK")

    try:
        hermes.enforce("build", {
            "blueprint_exists": True,
            "bot_type": "POSEIDON-BUOY",
            "action": "deploy",
            "human_approved": False
        })
    except Exception as e:
        print("Deploy blocked as expected:", e)

    approved = minerva.approve("software")
    hermes.enforce("modify", {
        "blueprint_exists": True,
        "approved": approved,
        "bot_type": "DEMETER-SCOUT",
        "action": "map",
        "human_approved": False
    })
    print("DEMETER-SCOUT modify(map) approved: OK")


if __name__ == "__main__":
    main()
