from faker import Faker
import random
import time
import string
from influxdb import InfluxDBClient

def generateVehicleID():
    letras = ""
    for _ in range(3):
        letras += random.choice(string.ascii_uppercase)
    return str(random.randint(1000, 9999)) + letras

# Configuración de InfluxDB
host = 'localhost'
port = 8086
user = 'usuario'
password = 'contraseña'
dbname = 'nombre_base_de_datos'

# Conexión a InfluxDB
client = InfluxDBClient(host, port, user, password, dbname)

while True:
    vehicleID = generateVehicleID() # Matricula del vehiculo electrico
    energy = random.uniform(5,50) # energia consumida en la carga en kWh
    bateryLevel = random.uniform(0,100) # Nivel de bateria del vehiculo (%)
    maxPower = random.uniform(20, 350) # Potencia maxima del cargador (kW)
    price = random.uniform (0.05, 0.30) # Precio por kWh. Estudiar si merece la pena tratar de que los precios sean reales
    timestamp = int(time.time()) * 1000000000  # Convertir a nanosegundos

    # Estructura del dato para InfluxDB
    data = [
        {
            "measurement": "sensores",
            "tags": {
                "sensor": "sensor1"
            },
            "time": timestamp,
            "fields": {
                "vehicleID": vehicleID,
                "energy": energy,
                "bateryLevel": bateryLevel,
                "maxPower": maxPower,
                "price": price
            }
        }
    ]

    # Escribir los datos en InfluxDB
    client.write_points(data)

    # Esperar un segundo antes de generar el siguiente dato
    time.sleep(1)
