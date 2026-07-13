# ATLAS Electronics and PCB Engineering Bible

**Primary AI:** Hermes  
**Supporting AIs:** Minerva, Ajani, ATLAS Council

## Mission
Design reliable, repairable, modular, safe, efficient, and manufacturable electronic systems for ATLAS robots, laboratories, sensors, and future products.

## Core Domains
- Electrical fundamentals: voltage, current, resistance, power, AC/DC, impedance, grounding, noise, EMI, and ESD.
- Components: passives, semiconductors, relays, optocouplers, oscillators, connectors, sensors, fuses, and switches.
- Power systems: 3.3 V, 5 V, 12 V, and 24 V rails; battery interfaces; DC-DC conversion; sequencing; current monitoring; and emergency shutdown.
- Embedded computing: STM32, RP2040, ESP32, AVR, ARM Cortex-M, and RISC-V controllers.
- Communications: I2C, SPI, UART, CAN, CAN FD, USB, Ethernet, RS-485, Modbus, EtherCAT, and MQTT where appropriate.
- PCB design: stack-up, trace width, current capacity, differential pairs, ground and power planes, return paths, thermal vias, test points, mounting, and keep-outs.
- Reliability: thermal analysis, signal integrity, power integrity, EMC, vibration, moisture, connector durability, and serviceability.

## Manufacturing Lifecycle
1. Requirements
2. Schematic
3. Electrical rule check
4. PCB layout
5. Design rule check
6. Fabrication outputs
7. Assembly outputs
8. Prototype assembly
9. Bring-up
10. Functional testing
11. Validation
12. Digital Twin registration

## Digital Twin Record
Every board records hardware revision, firmware version, manufacturing date, component lot data when available, calibration, self-test results, failure history, and maintenance actions.

## Minimum Acceptance Criteria
- Schematic and layout reviews completed
- Power and ground integrity checked
- Protection circuits documented
- Test points included
- Firmware and hardware versions linked
- Manufacturing outputs reproducible
- Bench tests and fault tests documented

## Laboratory Program
Design an LED controller, motor driver, sensor hub, CAN interface, battery-management interface, vision carrier board, and Weaver diagnostics board.

## Hermes Rules
- **PCB-1:** Every board must be testable and serviceable.
- **PCB-2:** Protection and grounding are designed, not improvised.
- **PCB-3:** Datasheet limits are never treated as recommended operating points.
- **PCB-4:** Every revision preserves traceability.
