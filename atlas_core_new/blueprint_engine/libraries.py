from __future__ import annotations
from typing import Dict

MATERIALS_DB: Dict[str, dict] = {
    "Ti-6Al-4V (Grade 5 Titanium)": {"category": "metal", "density_g_cm3": 4.43, "notes": "High strength-to-weight, corrosion resistant"},
    "7075-T6 Aluminum": {"category": "metal", "density_g_cm3": 2.81, "notes": "High strength aluminum alloy, common aerospace"},
    "6061-T6 Aluminum": {"category": "metal", "density_g_cm3": 2.70, "notes": "Good machinability, corrosion resistant"},
    "CFRP (Carbon Fiber Reinforced Polymer)": {"category": "composite", "density_g_cm3": 1.6, "notes": "Lightweight, stiff, needs careful layup"},
    "GFRP (Glass Fiber Reinforced Polymer)": {"category": "composite", "density_g_cm3": 1.9, "notes": "Cheaper composite, good durability"},
    "Silicone Elastomer (Shore A 20-50)": {"category": "polymer", "density_g_cm3": 1.1, "notes": "Flexible synthetic skin / soft-touch"},
    "TPU (Thermoplastic Polyurethane)": {"category": "polymer", "density_g_cm3": 1.2, "notes": "Flexible, abrasion resistant"},
    "Stainless Steel 304": {"category": "metal", "density_g_cm3": 8.0, "notes": "Corrosion resistant general purpose"},
    "Copper (C110)": {"category": "metal", "density_g_cm3": 8.96, "notes": "Bus bars, wiring, heat spreaders"},
    "Kevlar Fabric": {"category": "fiber", "density_g_cm3": 1.44, "notes": "Impact resistance, protective layers"},
    "LiFePO4 Battery Cells": {"category": "energy", "density_g_cm3": None, "notes": "Safe-ish chemistry, long cycle life"},
    "PEM Fuel Cell Stack": {"category": "energy", "density_g_cm3": None, "notes": "Hydrogen + oxygen -> electricity + water"},
}

COMPONENTS_DB: Dict[str, dict] = {
    "BLDC Motor": {"domain": "actuation", "notes": "Efficient electric motor, needs controller"},
    "Motor Controller (ESC/FOC)": {"domain": "actuation", "notes": "Controls BLDC motors; FOC for smooth torque"},
    "Hydraulic Actuator": {"domain": "actuation", "notes": "High force, heavier, needs pumps/lines"},
    "Linear Actuator": {"domain": "actuation", "notes": "Simpler motion, slower than BLDC joint drive"},
    "IMU (9-axis)": {"domain": "sensing", "notes": "Orientation + acceleration for stabilization"},
    "LiDAR": {"domain": "sensing", "notes": "3D scanning for navigation/avoidance"},
    "RGB Camera": {"domain": "sensing", "notes": "Vision-based object recognition"},
    "Thermal Camera": {"domain": "sensing", "notes": "Heat maps, wildlife / machine monitoring"},
    "Soil pH Sensor": {"domain": "sensing", "notes": "Soil chemistry measurement"},
    "Soil Moisture Sensor": {"domain": "sensing", "notes": "Water availability measurement"},
    "Seed Dispersal Hopper": {"domain": "tooling", "notes": "Controlled distribution of seeds"},
    "Soil Aerator Drill": {"domain": "tooling", "notes": "Breaks compact soil to improve oxygen/water"},
    "Crusher/Grinder": {"domain": "tooling", "notes": "Mineral processing (simulation-first)"},
    "Microcontroller (STM32/ESP32)": {"domain": "control", "notes": "Embedded control + sensor fusion"},
    "SBC (Jetson/RPi)": {"domain": "compute", "notes": "Onboard compute for perception/planning"},
}

TOOLS_DB: Dict[str, dict] = {
    "3D Printer (FDM)": {"notes": "Rapid plastic prototyping"},
    "3D Printer (SLA)": {"notes": "High detail resin parts"},
    "CNC Mill": {"notes": "Precision metal machining"},
    "Laser Cutter": {"notes": "Sheet cutting for chassis plates"},
    "TIG Welder": {"notes": "Metal frame welding"},
    "Vacuum Bagging Kit": {"notes": "Composite layup for CFRP/GFRP"},
    "Soldering Station": {"notes": "Electronics assembly"},
    "Multimeter + Oscilloscope": {"notes": "Electronics debugging"},
    "Torque Wrench Set": {"notes": "Assembly with correct bolt torque"},
    "Calipers/Micrometer": {"notes": "Dimensional verification"},
}
