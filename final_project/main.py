import network
import time
import _thread
from machine import Pin, ADC

import webserver
import fueling
import sensors
import utils

# WiFi setup
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Sant Eduard 2-1", "IneditSantEduard2-1")
print("🔌 Connecting to WiFi...")
timeout = 15
while not wlan.isconnected() and timeout > 0:
    print(".", end="")
    time.sleep(1)
    timeout -= 1
if wlan.isconnected():
    ip = wlan.ifconfig()[0]
    print(f"✅ Connected with IP: {ip}")
else:
    print("🚫 Failed to connect.")
    raise SystemExit()

# Init modules
fueling.setup()
webserver.setup(ip)

# Start web server in a separate thread
_thread.start_new_thread(webserver.run, ())

# Main loop
while True:
    fueling.loop()
    time.sleep(0.2)
