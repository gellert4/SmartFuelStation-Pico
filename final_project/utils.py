import time

def led_celebration(led_green, led_yellow):
    for _ in range(3):
        led_green.on(); led_yellow.on()
        time.sleep(0.2)
        led_green.off(); led_yellow.off()
        time.sleep(0.2)
