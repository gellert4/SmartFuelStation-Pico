import socket
import fueling

def setup(ip):
    global device_ip
    device_ip = ip

def run():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print(f"🌍 Web server running at http://{device_ip}")

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()

        if 'GET /data' in request:
            send_json(cl)
        elif 'GET /csv' in request:
            send_csv(cl)
        else:
            send_html(cl)
        cl.close()

def send_json(cl):
    labels_list = []
    liters_list = []
    type_list = []
    price_list = []
    for record in fueling.fuel_history[-5:]:
        labels_list.append('"%s"' % record[0])
        liters_list.append('%.2f' % record[1])
        type_list.append('"%s"' % ("Tilt" if record[4] else "Normal"))
        price_list.append('"€%.2f"' % record[2])
    avg_price = (fueling.total_spent / fueling.total_liters) if fueling.total_liters > 0 else 0
    json_data = '{' + \
        f'"status":"{fueling.current_status}",' + \
        f'"totalLiters":{fueling.total_liters:.2f},' + \
        f'"avgPrice":{avg_price:.2f},' + \
        f'"labels":[{",".join(labels_list)}],' + \
        f'"liters":[{",".join(liters_list)}],' + \
        f'"types":[{",".join(type_list)}],' + \
        f'"prices":[{",".join(price_list)}],' + \
        f'"tilt":{fueling.tilt_stops},' + \
        f'"normal":{fueling.normal_stops}' + \
    '}'
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
    cl.sendall(json_data.encode('utf-8'))

def send_csv(cl):
    csv = "Session,Type,Liters,Price\n"
    for record in fueling.fuel_history:
        note = "Tilt" if record[4] else "Normal"
        csv += f"{record[0]},{note},{record[1]:.2f},€{record[2]:.2f}\n"
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/csv\r\nContent-Disposition: attachment; filename=fuel_log.csv\r\n\r\n")
    cl.sendall(csv.encode('utf-8'))

def send_html(cl):
    # your big HTML string here
    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.sendall(HTML_PAGE_STRING.encode('utf-8'))
