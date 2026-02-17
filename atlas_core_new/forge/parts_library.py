from atlas_core_new.forge.blueprint_core import Part, Joint, OrganPack, new_id


def spine_beam(name="Spine Beam", mass_kg=12.0) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["structure", "routing_power", "routing_data", "routing_fluid"],
        description="Primary load path + routing trunk. Designed for torsion + compression.",
        mass_kg=mass_kg,
        service_access="partial",
        notes={"material": "aluminum_box + composite_panels", "access": "removable spine covers"}
    )


def rib_cage(name="Rib Cage", mass_kg=6.0) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["structure", "protection", "service"],
        description="Protects compute/power bay and creates service-ready access panels.",
        mass_kg=mass_kg,
        service_access="reachable",
        notes={"panel_standard": "quarter-turn fasteners"}
    )


def tendon_bundle(name="Tendon Bundle", mass_kg=1.2) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["motion", "routing_power", "service"],
        description="Cable/tendon transmission routing power from torso actuators to joints.",
        mass_kg=mass_kg,
        service_access="reachable",
        notes={"maintenance": "tension check + pulley inspection"}
    )


def cooling_loop(name="Cooling Loop", mass_kg=1.0, power_w=15.0) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["cooling", "routing_fluid", "safety"],
        description="Closed-loop cooling for motors/compute with leak detection.",
        mass_kg=mass_kg,
        power_w=power_w,
        service_access="partial",
        notes={"coolant": "non-conductive", "sensor": "leak + temp"}
    )


def compute_core(name="Compute Core", mass_kg=0.8, power_w=45.0) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["routing_data", "safety"],
        description="Onboard compute for gait control, perception, and fleet messaging.",
        mass_kg=mass_kg,
        power_w=power_w,
        service_access="reachable",
        notes={"example": "Jetson/NUC-class", "redundancy": "watchdog + safe-stop"}
    )


def sensor_mast(name="Sensor Mast", mass_kg=1.4, power_w=8.0) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["sensor", "structure", "service"],
        description="Stabilized sensor mount for cameras/lidar/environment sensors.",
        mass_kg=mass_kg,
        power_w=power_w,
        service_access="reachable",
        notes={"mount": "pan-tilt + isolation"}
    )


def eco_sensor_pack(name="Eco Sensor Pack", mass_kg=0.6, power_w=6.0) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["sensor", "service"],
        description="Air/soil/water-ready sensor interface (swap modules as needed).",
        mass_kg=mass_kg,
        power_w=power_w,
        service_access="reachable",
        notes={"modules": ["PM2.5", "VOC", "CO2", "soil_moisture", "conductivity"]}
    )


def pickup_tool(name="Pickup Tool", mass_kg=2.2, power_w=20.0) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["tooling", "service", "safety"],
        description="Non-weapon manipulator for pickup/sorting: gripper + small cutter for packaging only.",
        mass_kg=mass_kg,
        power_w=power_w,
        service_access="reachable",
        notes={"safety": "guarded cutter, torque limits", "use": "collection + sorting"}
    )


def sort_bin(name="Feedstock Bin", mass_kg=3.0) -> Part:
    return Part(
        part_id=new_id("part"),
        name=name,
        roles=["metabolism", "service", "protection"],
        description="Separated compartments for plastics/metals/organics; crush-safe with latch.",
        mass_kg=mass_kg,
        service_access="reachable",
        notes={"compartments": 3, "liner": "replaceable"}
    )


def joint_J1(name="Hip/Shoulder", compliance="series_elastic") -> Joint:
    return Joint(
        joint_id=new_id("joint"),
        name=name,
        dof=3,
        joint_family="J1",
        compliance=compliance,
        range_deg=(-45, 45),
        description="Multi-axis joint for limb root; energy protection via compliance."
    )


def joint_J2(name="Knee/Elbow", compliance="series_elastic") -> Joint:
    return Joint(
        joint_id=new_id("joint"),
        name=name,
        dof=1,
        joint_family="J2",
        compliance=compliance,
        range_deg=(0, 120),
        description="Primary hinge for stepping; compliance stores and releases energy."
    )


def joint_J3(name="Ankle/Wrist", compliance="flexure") -> Joint:
    return Joint(
        joint_id=new_id("joint"),
        name=name,
        dof=2,
        joint_family="J3",
        compliance=compliance,
        range_deg=(-20, 20),
        description="Small-range stability joint for terrain adaptation."
    )


def joint_J4(name="Spine Segment", compliance="variable_stiffness") -> Joint:
    return Joint(
        joint_id=new_id("joint"),
        name=name,
        dof=2,
        joint_family="J4",
        compliance=compliance,
        range_deg=(-15, 15),
        description="Controlled flex for balance + energy smoothing; stiffness changes per gait."
    )


def joint_J5(name="Neck Mast", compliance="series_elastic") -> Joint:
    return Joint(
        joint_id=new_id("joint"),
        name=name,
        dof=2,
        joint_family="J5",
        compliance=compliance,
        range_deg=(-60, 60),
        description="Pan/tilt sensor mast with shock isolation."
    )


def power_pack_kwh(kwh=1.5, mass_kg=9.0) -> OrganPack:
    return OrganPack(
        pack_id=new_id("pack"),
        name=f"Power Pack {kwh}kWh",
        roles=["routing_power", "safety"],
        description="Swappable battery organ. Quick release; thermal monitoring; fuse protection.",
        capacity={"kWh": kwh},
        mass_kg=mass_kg,
        notes={"swap_time_min": 2, "bms": True}
    )


def metabolism_pack_liters(liters=15, mass_kg=4.0) -> OrganPack:
    return OrganPack(
        pack_id=new_id("pack"),
        name=f"Metabolism Pack {liters}L",
        roles=["metabolism", "service", "safety"],
        description="Swappable bin pack for sorted feedstock bricks (robot pre-digestion).",
        capacity={"L": liters},
        mass_kg=mass_kg,
        notes={"containment": "sealed lid + odor filter", "safety": "no active chemistry onboard"}
    )


def sensor_pack(name="Sensor Pack", mass_kg=1.0) -> OrganPack:
    return OrganPack(
        pack_id=new_id("pack"),
        name=name,
        roles=["sensor", "service"],
        description="Swappable sensor organ: water sampler OR soil probe OR advanced air suite.",
        capacity={},
        mass_kg=mass_kg,
        notes={"interfaces": ["I2C", "UART", "CAN", "USB"], "mount": "quick-lock rail"}
    )


STANDARD_PARTS = {
    "spine_beam": spine_beam,
    "rib_cage": rib_cage,
    "tendon_bundle": tendon_bundle,
    "cooling_loop": cooling_loop,
    "compute_core": compute_core,
    "sensor_mast": sensor_mast,
    "eco_sensor_pack": eco_sensor_pack,
    "pickup_tool": pickup_tool,
    "sort_bin": sort_bin,
}

JOINT_FAMILIES = {
    "J1": joint_J1,
    "J2": joint_J2,
    "J3": joint_J3,
    "J4": joint_J4,
    "J5": joint_J5,
}

ORGAN_PACKS = {
    "power": power_pack_kwh,
    "metabolism": metabolism_pack_liters,
    "sensor": sensor_pack,
}
