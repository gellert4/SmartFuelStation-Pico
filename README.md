# ⛽ Smart Fuel Station with Dynamic Pricing

Gellért Szalai (gs223xt)

---

## Introduction

This project is a **smart fuel station simulator** that automatically detects when a vehicle starts fueling, measures the duration to estimate liters pumped, and dynamically adjusts the fuel price based on **ambient temperature and light** conditions. 

It uses a Raspberry Pi Pico WH running MicroPython, several sensors (Hall effect, DHT11, photoresistor, tilt switch), and sends data to a **Dockerized TIG stack (Telegraf, InfluxDB, Grafana)** on a Windows laptop. This allows for live dashboards of fueling activity and environmental influences.

For someone familiar with IoT and Docker, building this project (including all sensor wiring, Docker config, MicroPython code, and Grafana dashboards) might take around **10–12 hours**, factoring in debugging and coffee breaks.

---

## Objective

The idea originated from exploring how environmental factors (like heat or sunlight) can impact fuel volatility, safety margins, or even pricing models. 

The goals of the project were:

- **Detect and measure fueling activity automatically** (no manual input required).
- Adjust the **price per liter dynamically** based on temperature and light intensity.
- Simulate a tilt-based anomaly detection to shut down fueling for safety.
- Store all data in InfluxDB and visualize in Grafana dashboards for insights.

Insights I hoped to gain:

- How environmental metrics change during typical operation.
- How often anomalies (like excessive tilt) would occur.
- What a scalable local IoT fuel station might look like.

---

## Material

Here’s a list of the materials used:

| Component                     | Purpose                               | Source / Cost           |
|--------------------------------|--------------------------------------|-------------------------|
| Raspberry Pi Pico WH           | Main controller + WiFi               | Electrokit (~10€)       |
| Breadboard + jumper wires      | Connect components                   | Starter kit             |
| TLV49645 Hall effect sensor    | Detect magnet (car present)          | ~3€                     |
| Magnet                         | Trigger hall sensor                  | Recycled (free)         |
| DHT11                          | Read temperature & humidity          | Starter kit included    |
| Photoresistor + 10kΩ resistor  | Measure light level                  | Starter kit included    |
| Tilt switch                    | Detect abnormal orientation          | Starter kit included    |
| Red, Yellow, Green LEDs + 330Ω | Visual fueling status indicator      | Starter kit included    |
| Windows laptop                 | Run Docker TIG stack                 | Already owned           |
| Micro-USB cable                | Connect Pico to PC                   | ~5€                     |

---

## Computer Setup

For this project I used **Thonny** as my IDE. It’s particularly convenient for MicroPython development, letting me:

- Flash firmware (if needed)
- Upload libraries (though I mostly run live)
- Run scripts directly on the Pico without copying to flash

### My workflow:

- **IDE:** Thonny (select `MicroPython (Raspberry Pi Pico)`)
- **Execution:** Just click *Run current script* in Thonny — the Pico executes over USB.
- **Docker Desktop:** Used to spin up the TIG stack with a `docker-compose.yml`.

### Docker stack includes:

- **Telegraf:** HTTP listener plugin to receive data from Pico.
- **InfluxDB:** Stores time-series data.
- **Grafana:** Builds beautiful dashboards.

No cloud services — everything runs on my Windows machine.

---

## Putting everything together

### Wiring summary

- **Hall effect sensor:**  
    - `VCC` → 3.3V  
    - `GND` → GND  
    - `OUT` → `GP16`

- **Tilt switch:**  
    - `One side` → `GP17`  
    - `Other side` → GND (internal pull-up in code)

- **DHT11:**  
    - `Data` → `GP15` (with pull-up)
    - `VCC` → 3.3V  
    - `GND` → GND

- **Photoresistor:**  
    - Between 3.3V and `GP26`
    - `GP26` to GND through 10kΩ resistor

- **LEDs:**  
    - Red → `GP18`, Yellow → `GP19`, Green → `GP20` with 330Ω resistors to GND

### Simple voltage divider for photoresistor:

```
3.3V
 |
[PhotoR]
 |
 |----> GP26 (ADC)
 |
[10kΩ]
 |
GND
```

This is purely a breadboard prototype. In production, I’d design a small PCB or at least use solid header connectors.

---

## Platform

Everything runs **locally on my laptop** for privacy and independence.

- **Telegraf** collects JSON payloads from the Pico via HTTP POST.
- **InfluxDB** stores the data with retention policy ~30 days.
- **Grafana** queries InfluxDB for real-time dashboards.

This stack can scale by either:

- Using MQTT + local Mosquitto for multiple pumps.
- Or migrating InfluxDB + Grafana to a cloud VM if remote access needed.

For now, it’s fully offline and simple.

---

## The code

No single “algorithm,” but rather how parts work together in the main loop.

### 🚗 Car detected (magnet triggers hall sensor)
```python
if hall_sensor.value() == 0 and not fueling:
    start_time = time.time()
    fueling = True
    print("🚗 Car detected! Starting fueling...")
```

### ⏳ Measuring fueling
```python
elapsed = time.time() - start_time
liters = elapsed * 0.1  # approx 0.1 L/s for simulation
price_per_liter = 1.5 + (temp / 100) + (light / 100)
total_price = liters * price_per_liter
```

### 🚦 Safety / tilt detection
```python
if tilt_sensor.value() == 0:
    print("⚠️ Abnormal tilt! Stopping fueling.")
    red_led.on()
    fueling = False
```

### 🌐 Send to Telegraf
```python
payload = json.dumps({
    "liters": liters,
    "price": total_price,
    "temp": temp,
    "light": light,
    "tilt": tilt_sensor.value()
})
urequests.post("http://192.168.1.10:5000/telegraf", data=payload)
```

### 🚥 LED indicator
- **Green:** fueling normal (<5L)
- **Yellow:** fueling >5L
- **Red:** tilt detected

---

## Transmitting the data / connectivity

- **Primary connection:** No WiFi (runs over USB network to laptop)
- **Transport:** HTTP POST
- **Payload:** JSON like:

```json
{
  "liters": 1.4,
  "price": 2.07,
  "temp": 26,
  "light": 150,
  "tilt": 0
}
```

- **Frequency:** ~once per second, only if fueling or important state changes.

This could easily switch to MQTT for multi-pump coordination or Mosquitto + Node-RED pipelines.

---

## Presenting the data

The dashboard is in Grafana, pulling directly from InfluxDB.

- One panel shows liters over time.
- Another overlays price vs temp and light.
- Alerts highlight any abnormal tilt events.

### Retention & database:
- InfluxDB stores for 30 days (default config).
- Each fuel event is logged as raw data for future analysis.

---

## Finalizing the design

### 🎉 Project outcome
Solid breadboard prototype that reliably triggers, calculates liters, adjusts price dynamically, and logs to Grafana.

Extremely fun to watch the dashboard react in real-time as I wave a light or heat the DHT11.

### 🔧 Improvements if scaling:
- Use a real flow sensor for actual liters.
- Use relay + pump motor for a complete simulator.
- Try WiFi hotspot mode to avoid USB cable.

### 📸 Pictures & demo
(Insert pictures of breadboard + Grafana screenshots once available.)

---

## ✅ Advanced level (T2)

- ✅ Multiple sensors integrated (Hall, DHT11, photoresistor, tilt).
- ✅ Local TIG stack for database & dashboard.
- ✅ Dynamic computations for real-time pricing.
- ✅ Written as a full tutorial (HackMD/GitHub README style).
- ✅ Public on GitHub.

---

## Links

- **GitHub repo:** https://github.com/gellert4/smart-fuel-station-iot
- **Docker TIG compose:** in the repo
- **License:** Creative Commons Attribution-NonCommercial (course standard)

---

## Thanks!

Part of 📚 **1DT305 - Applied IoT** (LNU Summer 2025)  
**Instructors:** Oxana Sachenkova, Arslan Musaddiq, Daniel Lundberg.

Happy fueling — responsibly! 🛢️