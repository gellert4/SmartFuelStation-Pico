import network
import time
from machine import Pin, ADC
import dht
import _thread

# -------------------- WIFI SETUP --------------------
ssid = 'Sant Eduard 2-1'
password = 'IneditSantEduard2-1'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("🔌 Connecting to WiFi...")
timeout = 15
while not wlan.isconnected() and timeout > 0:
    print(".", end="")
    time.sleep(1)
    timeout -= 1

print()
if wlan.isconnected():
    ip = wlan.ifconfig()[0]
    print(f"✅ Connected with IP: {ip}")
else:
    print("🚫 Failed to connect.")
    raise SystemExit()

time.sleep(2)

# -------------------- PIN SETUP --------------------
hall_sensor = Pin(16, Pin.IN, Pin.PULL_UP)
dht_sensor = dht.DHT11(Pin(15))
photoresistor = ADC(26)
tilt_switch = Pin(17, Pin.IN, Pin.PULL_UP)

led_yellow = Pin(20, Pin.OUT)
led_green = Pin(19, Pin.OUT)
led_red = Pin(18, Pin.OUT)

# -------------------- CONSTANTS & STATE --------------------
FLOW_RATE = 0.05
PRICE_PER_LITER = 1.85
SURCHARGE_RATE = 1.10
LIGHT_THRESHOLD = 20000
TEMP_THRESHOLD = 28

fueling = False
start_time = 0
fuel_count = 0
fuel_history = []
total_liters = 0
total_spent = 0
tilt_stops = 0
normal_stops = 0
current_status = "⏳ Waiting for magnet..."

led_yellow.on()
led_green.off()
led_red.off()

print("🛠️ Smart Fuel-Up Station Initialized")

# -------------------- LED CELEBRATION --------------------
def led_celebration():
    for _ in range(3):
        led_green.on()
        led_yellow.on()
        time.sleep(0.2)
        led_green.off()
        led_yellow.off()
        time.sleep(0.2)

# -------------------- WEB SERVER --------------------
def start_web_server():
    import socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print(f"🌍 Web server running at http://{ip}")

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024)
        req = request.decode()

        # Handle /data endpoint
        if 'GET /data' in req:
            labels_list = []
            liters_list = []
            type_list = []
            price_list = []
            for record in fuel_history[-5:]:
                labels_list.append('"%s"' % record[0])
                liters_list.append('%.2f' % record[1])
                type_list.append('"%s"' % ("Tilt" if record[4] else "Normal"))
                price_list.append('"€%.2f"' % record[2])

            avg_price = (total_spent / total_liters) if total_liters > 0 else 0

            json_data = '{' + \
                f'"status":"{current_status}",' + \
                f'"totalLiters":{total_liters:.2f},' + \
                f'"avgPrice":{avg_price:.2f},' + \
                f'"labels":[{",".join(labels_list)}],' + \
                f'"liters":[{",".join(liters_list)}],' + \
                f'"types":[{",".join(type_list)}],' + \
                f'"prices":[{",".join(price_list)}],' + \
                f'"tilt":{tilt_stops},' + \
                f'"normal":{normal_stops}' + \
            '}'

            cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\nConnection: close\r\n\r\n")
            cl.sendall(json_data.encode('utf-8'))
            cl.close()
            continue

        # Handle /csv endpoint
        if 'GET /csv' in req:
            csv = "Session,Type,Liters,Price\n"
            for record in fuel_history:
                note = "Tilt" if record[4] else "Normal"
                csv += f"{record[0]},{note},{record[1]:.2f},€{record[2]:.2f}\n"
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/csv; charset=utf-8\r\nContent-Disposition: attachment; filename=fuel_log.csv\r\nConnection: close\r\n\r\n")
            cl.sendall(csv.encode('utf-8'))
            cl.close()
            continue

        # Serve main HTML page
        html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"><title>Smart Fuel Station</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
<style>
body { font-family: Arial; background:#f4f4f4; color:#333; padding:20px; max-width:800px; margin:auto; }
h1 { text-align:center; }
.summary, .status { background:#fff; padding:15px; margin-bottom:20px; box-shadow:0 2px 5px rgba(0,0,0,0.1); border-radius:8px; }
table { width:100%; border-collapse:collapse; background:#fff; margin-top:20px; }
th, td { padding:12px; text-align:center; border-bottom:1px solid #eee; }
th { background:#3498db; color:white; }
canvas { margin-top:20px; background:#fff; border-radius:8px; }
button { padding:10px 15px; background:#3498db; color:white; border:none; border-radius:5px; margin-top:15px; }
</style>
</head>
<body>
<h1>⛽ Smart Fuel-Up Station</h1>
<div class="summary" id="summary"></div>
<div class="status" id="status"></div>
<table id="table"><tr><th>#</th><th>Type</th><th>Liters</th><th>Price</th></tr></table>
<canvas id="barChart"></canvas>
<canvas id="pieChart"></canvas>
<button onclick="window.location='/csv'">⬇️ Download CSV</button>
<script>
var barChart, pieChart;
function update() {
    fetch('/data').then(res=>res.json()).then(data=>{
        document.getElementById("summary").innerHTML = "🚀 <b>Total:</b> "+data.totalLiters+" L<br>💶 <b>Avg price:</b> €"+data.avgPrice;
        document.getElementById("status").innerHTML = "<b>Status:</b> "+data.status;
        let rows = "<tr><th>#</th><th>Type</th><th>Liters</th><th>Price</th></tr>";
        for(let i=0;i<data.labels.length;i++)
            rows += `<tr><td>${data.labels[i]}</td><td>${data.types[i]}</td><td>${data.liters[i]} L</td><td>${data.prices[i]}</td></tr>`;
        document.getElementById("table").innerHTML = rows;
        if(barChart) barChart.destroy();
        barChart = new Chart(document.getElementById('barChart').getContext('2d'), {
            type:'bar',
            data:{labels:data.labels,datasets:[{label:'Liters',data:data.liters,backgroundColor:'#3498db'}]},
            options:{scales:{y:{beginAtZero:true}}}
        });
        if(pieChart) pieChart.destroy();
        pieChart = new Chart(document.getElementById('pieChart').getContext('2d'), {
            type:'pie',
            data:{labels:['Normal','Tilt'],datasets:[{data:[data.normal,data.tilt],backgroundColor:['#2ecc71','#e74c3c']}]}
        });
        if(data.status.includes("🎉")) confetti({particleCount:100,spread:70});
    });
}
setInterval(update,3000); update();
</script>
</body>
</html>"""
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n")
        cl.sendall(html.encode('utf-8'))
        cl.close()

# -------------------- START WEB SERVER THREAD --------------------
_thread.start_new_thread(start_web_server, ())

# -------------------- MAIN LOOP --------------------
while True:
    if fueling and tilt_switch.value() == 1:
        end_time = time.time()
        duration = end_time - start_time
        try: dht_sensor.measure(); temp=dht_sensor.temperature()
        except: temp=25
        adj_flow = FLOW_RATE*0.9 if temp>TEMP_THRESHOLD else FLOW_RATE
        liters = duration*adj_flow
        light_val = photoresistor.read_u16()
        is_dark = light_val < LIGHT_THRESHOLD
        price_per_liter = PRICE_PER_LITER*SURCHARGE_RATE if is_dark else PRICE_PER_LITER
        price = liters*price_per_liter
        fuel_count+=1
        fuel_history.append((f"#{fuel_count}",liters,price,is_dark,True))
        total_liters+=liters; total_spent+=price; tilt_stops+=1
        fueling=False; led_green.off(); led_red.on()
        current_status="⚠️ TILT STOPPED — recorded partial fueling"
        print(current_status)
        time.sleep(3); led_red.off(); led_yellow.on()
        current_status="⏳ Waiting for magnet..."
        continue

    if hall_sensor.value()==0 and not fueling:
        fueling=True; start_time=time.time()
        led_yellow.off(); led_green.on()
        current_status="🧲 Magnet detected — Fueling in progress."
        print(current_status)

    elif hall_sensor.value()==1 and fueling:
        end_time=time.time()
        duration=end_time-start_time
        try: dht_sensor.measure(); temp=dht_sensor.temperature()
        except: temp=25
        adj_flow=FLOW_RATE*0.9 if temp>TEMP_THRESHOLD else FLOW_RATE
        liters=duration*adj_flow
        light_val=photoresistor.read_u16()
        is_dark=light_val<LIGHT_THRESHOLD
        price_per_liter=PRICE_PER_LITER*SURCHARGE_RATE if is_dark else PRICE_PER_LITER
        price=liters*price_per_liter
        fuel_count+=1
        fuel_history.append((f"#{fuel_count}",liters,price,is_dark,False))
        total_liters+=liters; total_spent+=price; normal_stops+=1
        fueling=False; led_green.off(); led_red.on()
        current_status="🎉 Fueling complete. Nice job!"
        led_celebration()
        print(f"🛑 Stopped: {duration:.1f}s, {liters:.2f}L, €{price:.2f}")
        time.sleep(2); led_red.off(); led_yellow.on()
        current_status="⏳ Waiting for magnet..."

    time.sleep(0.2)
