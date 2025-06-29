from machine import Pin
import time
import sensors
import utils

# Pins and state
led_yellow = Pin(20, Pin.OUT)
led_green = Pin(19, Pin.OUT)
led_red = Pin(18, Pin.OUT)

fueling = False
start_time = 0
fuel_count = 0
fuel_history = []
total_liters = 0
total_spent = 0
tilt_stops = 0
normal_stops = 0
current_status = "⏳ Waiting for magnet..."

def setup():
    led_yellow.on()
    led_green.off()
    led_red.off()
    print("🛠️ Smart Fuel-Up Initialized")

def loop():
    global fueling, start_time, fuel_count, total_liters, total_spent, tilt_stops, normal_stops, current_status

    if fueling and sensors.tilt_triggered():
        liters, price, is_dark = sensors.compute_fuel(start_time)
        record_fueling(liters, price, is_dark, True)
        led_green.off(); led_red.on()
        current_status = "⚠️ TILT STOPPED — partial fueling"
        print(current_status)
        time.sleep(3); led_red.off(); led_yellow.on()
        current_status = "⏳ Waiting for magnet..."
        fueling = False

    elif sensors.magnet_present() and not fueling:
        fueling = True
        start_time = time.time()
        led_yellow.off(); led_green.on()
        current_status = "🧲 Magnet detected — Fueling in progress."
        print(current_status)

    elif not sensors.magnet_present() and fueling:
        liters, price, is_dark = sensors.compute_fuel(start_time)
        record_fueling(liters, price, is_dark, False)
        led_green.off(); led_red.on()
        current_status = "🎉 Fueling complete. Nice job!"
        print(current_status)
        utils.led_celebration(led_green, led_yellow)
        time.sleep(2); led_red.off(); led_yellow.on()
        current_status = "⏳ Waiting for magnet..."
        fueling = False

def record_fueling(liters, price, is_dark, tilt):
    global fuel_count, total_liters, total_spent, tilt_stops, normal_stops, fuel_history
    fuel_count += 1
    fuel_history.append((f"#{fuel_count}", liters, price, is_dark, tilt))
    total_liters += liters
    total_spent += price
    if tilt: tilt_stops += 1
    else: normal_stops += 1
