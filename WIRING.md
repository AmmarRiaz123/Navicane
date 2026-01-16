# Smart Cane Wiring Guide

## GPIO Pin Map

| GPIO Pin | Component        |
|----------|------------------|
| GPIO 0   | LED1 (Status)    |
| GPIO 1   | LED2 (Power)     |
| GPIO 2   | Button (Reset)   |
| GPIO 3   | Buzzer           |
| GPIO 4   | Ultrasonic Trig  |
| GPIO 5   | Ultrasonic Echo  |
| GPIO 6   | Servo Motor      |
| GPIO 7   | I2C SDA (LCD)    |
| GPIO 8   | I2C SCL (LCD)    |
| GPIO 9   | SD Card CS       |
| GPIO 10  | SD Card MOSI     |
| GPIO 11  | SD Card MISO     |
| GPIO 12  | SD Card SCK      |
| GPIO 13  | Bluetooth TX     |
| GPIO 14  | Bluetooth RX     |
| GPIO 15  | GPS RX           |
| GPIO 16  | GPS TX           |
| GPIO 17  | Hall Sensor      |
| GPIO 18  | Temperature Sensor|
| GPIO 19  | Humidity Sensor  |
| GPIO 20  | Vibration Motor  |
| GPIO 21  | LED3 (Error)     |

## Components and Their Connections

1. **LED1 (Status)**: Connect the anode to GPIO 0 and the cathode to the ground through a 220-ohm resistor.
2. **LED2 (Power)**: Connect the anode to GPIO 1 and the cathode to the ground through a 220-ohm resistor.
3. **Button (Reset)**: Connect one terminal to GPIO 2 and the other terminal to the ground.
4. **Buzzer**: Connect the positive terminal to GPIO 3 and the negative terminal to the ground.
5. **Ultrasonic Sensor**: Connect the Trig pin to GPIO 4 and the Echo pin to GPIO 5. Connect the VCC to the 5V pin and GND to the ground.
6. **Servo Motor**: Connect the control wire to GPIO 6. Connect the power wire to the 5V pin and the ground wire to the ground.
7. **I2C LCD**: Connect the SDA pin to GPIO 7 and the SCL pin to GPIO 8. Connect the VCC to the 5V pin and GND to the ground.
8. **SD Card Module**: Connect the CS pin to GPIO 9, MOSI to GPIO 10, MISO to GPIO 11, and SCK to GPIO 12. Connect the VCC to the 5V pin and GND to the ground.
9. **Bluetooth Module**: Connect the TX pin to GPIO 13 and the RX pin to GPIO 14. Connect the VCC to the 5V pin and GND to the ground.
10. **GPS Module**: Connect the RX pin to GPIO 15 and the TX pin to GPIO 16. Connect the VCC to the 5V pin and GND to the ground.
11. **Hall Sensor**: Connect the output pin to GPIO 17 and the other two pins to the VCC and ground.
12. **Temperature and Humidity Sensor**: Connect the data pin to GPIO 18, VCC to the 5V pin, and GND to the ground.
13. **Vibration Motor**: Connect one terminal to GPIO 20 and the other terminal to the ground.

## Power Supply

- The smart cane operates on a 5V power supply. Ensure that the power source can provide sufficient current for all the components.
- It is recommended to use a lithium polymer (LiPo) battery with a suitable capacity (e.g., 2000mAh) for portable use.
- Connect the battery's positive terminal to the VCC rail and the negative terminal to the ground rail on the breadboard.

## Schematic Diagram

![Schematic Diagram](file:///c%3A/Users/Dell/Desktop/Navicane/schematic.png)

## Assembly Instructions

1. **Assemble the Components**: Gather all the components listed in the GPIO Pin Map and Components sections.
2. **Connect the Components**: Using jumper wires, connect the components according to the GPIO Pin Map.
3. **Mount the Components**: Securely mount the components on the cane using zip ties or adhesive mounts.
4. **Route the Wires**: Neatly route the wires along the cane to avoid any obstruction or damage.
5. **Test the Connections**: Before finalizing the assembly, power on the cane and test each component to ensure proper connectivity.

## Troubleshooting Tips

- If a component is not working, double-check the connections against the GPIO Pin Map.
- Ensure that the power supply is adequately charged and providing the correct voltage.
- For intermittent connections, try using shorter jumper wires or repositioning the components.

## Maintenance

- Regularly check the connections and components for any signs of wear or damage.
- Clean the components and connections with a soft, dry brush to remove any dust or debris.
- Store the smart cane in a dry, cool place when not in use to prevent any moisture damage.

## Disclaimer

This wiring guide is provided as a reference only. The actual wiring and components may vary based on the specific requirements and design of the smart cane. Always refer to the manufacturer's datasheets and documentation for each component for the most accurate and detailed information.

