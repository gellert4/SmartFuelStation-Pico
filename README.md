# ⛽ Smart Fuel Station with Dynamic Pricing

Gellért Szalai (gs223xt)

---

## Introduction

This project is a **smart fuel station simulator** that automatically detects when a vehicle starts fueling, measures the duration to estimate liters pumped, and dynamically adjusts the fuel price based on **ambient temperature and light** conditions. 

It uses a Raspberry Pi Pico WH running MicroPython with several sensors (Hall effect, DHT11, photoresistor, tilt switch), and serves a **real-time web dashboard** directly from the Pico. The built-in web server provides live charts, statistics, and CSV export functionality accessible from any device on the network.

For someone familiar with IoT and MicroPython, building this project (including all sensor wiring, web interface code, and dashboard features) might take around **8–10 hours**, factoring in debugging and testing.

---

## Objective

The idea originated from exploring how environmental factors (like heat or sunlight) can impact fuel volatility, safety margins, or even pricing models. 

The goals of the project were:

- **Detect and measure fueling activity automatically** (no manual input required).
- Adjust the **price per liter dynamically** based on temperature and light intensity.
- Simulate a tilt-based anomaly detection to shut down fueling for safety.
- Provide a **self-contained web dashboard** for real-time monitoring and data export.

Insights I hoped to gain:

- How environmental metrics change during typical operation.
- How often anomalies (like excessive tilt) would occur.
- What a simple, standalone IoT fuel station interface might look like.

---

Everything runs **directly on the Raspberry Pi Pico** with a built-in web server.

- **Web server:** Runs on the Pico itself, accessible via WiFi
- **Data storage:** In-memory storage of fuel history (last 5 sessions displayed)
- **Dashboard:** Real-time HTML interface with interactive charts
- **Data export:** CSV download functionality for fuel logs

This approach is:
- **Self-contained:** No external databases or services needed
- **Portable:** Works anywhere with WiFi
- **Simple:** Just connect to the Pico's web interface

The web dashboard updates every 3 seconds and includes celebration animations when fueling completes!lator** that automatically detects when a vehicle starts fueling, measures the duration to estimate liters pumped, and dynamically adjusts the fuel price based on **ambient temperature and light** conditions. 

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

| Component                     | Purpose                               |
|--------------------------------|---------------------------------------|
| Raspberry Pi Pico WH           | Main controller + WiFi               |
| Breadboard + jumper wires      | Connect components                   |
| TLV49645 Hall effect sensor    | Detect magnet (car present)          |
| Magnet                         | Trigger hall sensor                  |
| DHT11                          | Read temperature & humidity          |
| Photoresistor + 10kΩ resistor  | Measure light level                  |
| Tilt switch                    | Detect abnormal orientation          |
| Red, Yellow, Green LEDs + 330Ω | Visual fueling status indicator      |
| Windows laptop                 | Run web browser to view dashboard    |
| Micro-USB cable                | Connect Pico to PC                   |

---

## Computer Setup

For this project I used **Thonny** as my IDE. It’s particularly convenient for MicroPython development, letting me:

- Flash firmware (if needed)
- Upload libraries (though I mostly run live)
- Run scripts directly on the Pico without copying to flash

### My workflow:

- **IDE:** Thonny for MicroPython development
- **Execution:** Just click *Run current script* in Thonny — the Pico executes over USB.
- **Web Interface:** Built-in web server serves a dashboard at the Pico's IP address.

### Built-in web server includes:

- **Real-time dashboard:** Shows fueling status, charts, and statistics
- **Data API:** JSON endpoint for live data updates  
- **CSV export:** Download fueling history as spreadsheet
- **Interactive charts:** Bar charts and pie charts with Chart.js

No external services needed — everything runs on the Pico itself with a simple web interface.

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
duration = end_time - start_time
# Adjust flow rate based on temperature  
adj_flow = FLOW_RATE * 0.9 if temp > TEMP_THRESHOLD else FLOW_RATE
liters = duration * adj_flow
```

### 💰 Dynamic pricing
```python
light_val = photoresistor.read_u16()
is_dark = light_val < LIGHT_THRESHOLD
# Apply surcharge in dark conditions
price_per_liter = PRICE_PER_LITER * SURCHARGE_RATE if is_dark else PRICE_PER_LITER
price = liters * price_per_liter
```

### 🚦 Safety / tilt detection
```python
if fueling and tilt_switch.value() == 1:  # Tilt detected during fueling
    # Record partial fueling session
    fuel_history.append((f"#{fuel_count}", liters, price, is_dark, True))
    current_status = "⚠️ TILT STOPPED — recorded partial fueling"
    led_red.on()
    fueling = False
```

### 🌐 Web Dashboard
```python
# Built-in web server serves real-time dashboard
json_data = '{' + \
    f'"status":"{current_status}",' + \
    f'"totalLiters":{total_liters:.2f},' + \
    f'"avgPrice":{avg_price:.2f},' + \
    f'"labels":[{",".join(labels_list)}],' + \
    f'"liters":[{",".join(liters_list)}]' + \
'}'
```

### 🚥 LED indicator
- **Yellow:** Waiting for magnet (standby)
- **Green:** Fueling in progress  
- **Red:** Tilt detected or fueling complete
- **Celebration:** Green/Yellow blinking when fueling completes normally

---

## Web Interface & Connectivity

- **Connection:** WiFi network connection
- **Web Server:** Built-in HTTP server on port 80
- **Dashboard:** Real-time HTML interface with interactive charts
- **Data Format:** JSON API for live updates

```json
{
  "status": "🎉 Fueling complete. Nice job!",
  "totalLiters": 2.45,
  "avgPrice": 1.95,
  "labels": ["#1", "#2", "#3"],
  "liters": [1.2, 0.8, 0.45],
  "types": ["Normal", "Normal", "Tilt"],
  "prices": ["€2.22", "€1.48", "€0.83"]
}
```

- **Features:** Live charts, CSV export, confetti celebrations
- **Updates:** Dashboard refreshes every 3 seconds automatically

The web interface includes Chart.js for beautiful bar charts and pie charts, plus canvas-confetti for celebrations when fueling completes!

---

## Presenting the data

The dashboard runs directly on the Pico's web server, accessible via any web browser.

**Dashboard features:**
- **Real-time status:** Current fueling state and progress
- **Session history:** Last 5 fueling sessions with charts
- **Statistics:** Total liters pumped and average price
- **Interactive charts:** Bar chart (liters) and pie chart (normal vs tilt stops)
- **CSV export:** Download complete fueling history
- **Celebrations:** Confetti animation when fueling completes successfully

**Data storage:**
- **In-memory:** Fuel history stored in Python list
- **Persistent:** Data persists during session (lost on restart)
- **Export:** CSV download for permanent records

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