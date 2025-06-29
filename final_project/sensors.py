from machine import Pin, ADC
import dht
import time

FLOW_RATE = 0.05
PRICE_PER_LITER = 1.85
SURCHARGE_RATE = 1.10
LIGHT_THRESHOLD = 20000
TEMP_THRESHOLD = 28

hall_sensor = Pin(16, Pin.IN, Pin.PULL_UP)
tilt_switch = Pin(17, Pin.IN, Pin.PULL_UP)
photoresistor = ADC(26)
dht_sensor = dht.DHT11(Pin(15))

def magnet_present():
    return hall_sensor.value() == 0

def tilt_triggered():
    return tilt_switch.value() == 1

def compute_fuel(start_time):
    end_time = time.time()
    duration = end_time - start_time
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
    except:
        temp = 25
    adj_flow = FLOW_RATE * 0.9 if temp > TEMP_THRESHOLD else FLOW_RATE
    liters = duration * adj_flow
    light_val = photoresistor.read_u16()
    is_dark = light_val < LIGHT_THRESHOLD
    price_per_liter = PRICE_PER_LITER * SURCHARGE_RATE if is_dark else PRICE_PER_LITER
    price = liters * price_per_liter
    return liters, price, is_dark
