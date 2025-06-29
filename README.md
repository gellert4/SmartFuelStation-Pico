# SmartFuelStation-Pico 🚗⛽

This is an IoT project for a **Smart Fuel Station simulation**, built using a Raspberry Pi Pico WH with MicroPython.  
It detects fuel start/stop using a hall effect sensor (magnet), measures fuel flow time, calculates liters and pricing, adjusts costs for environmental conditions (temperature & light), and displays everything on a **dynamic web dashboard**.

---

## 📚 Overview
- **Platform:** Raspberry Pi Pico WH (MicroPython)
- **Dashboard:** Web server hosted on the Pico with live JSON data + HTML page (Chart.js + Confetti)
- **Main Features:**
  - Detects start of fueling with a **hall effect sensor & magnet**
  - Measures fueling time and calculates **liters pumped**
  - Adjusts flow rate based on **temperature (DHT11)**
  - Applies a surcharge if it's **dark (photoresistor)**
  - Detects abnormal stop via **tilt switch**
  - Tracks total liters, average price, stops by type
  - CSV download of fueling history
  - All data displayed on a **live updating web interface with charts & summary**

---

## 🛠️ Hardware used
| Component                 | Function                     |
|----------------------------|-----------------------------|
| Raspberry Pi Pico WH        | Main controller & WiFi      |
| DHT11 sensor                | Measures ambient temperature|
| Photoresistor (CdS)         | Measures light level (to apply surcharge in dark) |
| Hall Effect sensor (TLV49645)| Detects magnet to start fueling |
| Tilt switch                 | Detects sudden tilt to stop fueling |
| LEDs (Green/Yellow/Red)     | Indicate states: waiting, fueling, stop/tilt |
| Resistors                   | For LEDs & sensors |
| Breadboard + jumper wires   | For circuit assembly |

---

## 🌐 Web dashboard
- Hosted directly on the Pico at `http://<pico-ip>`
- Features:
  - Total liters & average price
  - Latest fueling sessions with type, liters, price
  - Bar chart (liters per session)
  - Pie chart (normal vs tilt stops)
  - Download CSV log
  - Confetti animation on successful fueling completion

---

## 🚦 Operating logic
| Event                    | Behavior                                              |
|---------------------------|------------------------------------------------------|
| Magnet detected            | Starts fueling, timer begins, LEDs indicate fueling |
| Magnet removed (normal)    | Calculates liters, adjusts by temp & light, records normal stop |
| Tilt triggered             | Stops fueling immediately, partial fueling recorded as tilt stop |
| Temp > 28°C                | Flow rate reduced by 10% |
| Dark (<20000 ADC)          | Price increased by 10% surcharge |
| All activity logged & shown on website |

---

## 📁 Project structure
| File                  | Description                               |
|------------------------|------------------------------------------|
| `in_one_file.py`       | Complete MicroPython script (runs on Pico) |
| `/final_project/`      | Project folder (with earlier modular attempts) |
| `.gitignore`           | Ignores VS Code, Pico binaries, OS clutter |

---

## 🚀 How to deploy
1. Copy `in_one_file.py` to your Pico (e.g. using Thonny).
2. Ensure your WiFi SSID & password are set at the top of the file.
3. Open the serial console; once it connects, it will print its IP.
4. Open a browser at `http://<pico-ip>`.
5. Fuel with your magnet & see the live dashboard update!

---

## ✅ Future improvements
- Use 7-segment display to show liters directly on the station
- Add physical button to manually stop fueling
- Store data persistently (external flash or SD)
- Integrate MQTT & InfluxDB + Grafana dashboards

---

## 📝 Author
**Gellért Szalai**

---

## 🚀 License
MIT License
