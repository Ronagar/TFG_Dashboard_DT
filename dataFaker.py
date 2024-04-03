#from faker import Faker
import random
import time
import string
from dataclasses import dataclass
from collections import namedtuple
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

#Clase para crear los datos a enviar a Influx
"""class Charger(namedtuple('Charger', ['name', 'location', 'vehicleID', 'energy', 'bateryLevel', 'maxPower', 'price', 'timestamp'])):
    pass"""
@dataclass
class Charger:
    name: str
    location: str
    vehicleID: str
    energy: float
    bateryLevel: float
    maxPower: int
    price: float
    timestamp: int
    

# Configuración de InfluxDB
myToken = "L_606Pm_n6FtaLVfzADl6oFHTd1llyO7nnYNq8X18D5RQOMzKH_S2gal4_4z8V0j0A4ZHMhZ04JkVXCv3TRZuA=="
org = "pruebaUMA"
url = "http://localhost:8086"
bucket="bucketPrueba3"

# Conexión a InfluxDB
client = influxdb_client.InfluxDBClient(url=url, token=myToken, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

###############Variables globales:########################
maxPower = random.randint(20, 70) # Potencia maxima del cargador (kWh).
##########################################################

# Genera la matricula del vehiculo que entra a cargar
def generateVehicleID():
    letras = ""
    for _ in range(3):
        letras += random.choice(string.ascii_uppercase)
    return str(random.randint(1000, 9999)) + letras
    #return random.randint(100, 99999)

# Genera los datos que se enviaran a la base de datos
def generateData(car, bateryLevel, bateryCapacity):
    # En la version inicial, todos los coches se quedarán hasta completar la carga. Deberían poder desconectarse antes de completar la carga
    energy = 0.0
    if (car != None): 
        energy = float(bateryCapacity - (bateryCapacity * (bateryLevel/100)))

    #energy = random.uniform(5,50) # energia consumida en la carga en kWh
    price = random.uniform (0.05, 0.30) # Precio por kWh. Estudiar si merece la pena tratar de que los precios sean reales
    timestamp = int(time.time()) * 1000000000  # Convertir a nanosegundos

    # Estructura del dato para InfluxDB
    """data = [
        {
            "measurement": "sensores",
            "tags": {
                "Charger": "Charger1"
            },
            "time": timestamp,
            "fields": {
                "vehicleID": car,
                "energy": energy,
                "bateryLevel": bateryLevel,
                "maxPower": maxPower,
                "price": price
            }
        }
    ]"""
    """data = Charger(name = "Charger1", 
                   location = "stationA", 
                   vehicleID = car, 
                   energy = energy, 
                   bateryLevel = bateryLevel, 
                   maxPower = maxPower, 
                   price = price, 
                   timestamp = timestamp)"""
    data = Charger(name = "Charger",
                   location ="stationA", 
                   vehicleID = car, 
                   energy = energy, 
                   bateryLevel = bateryLevel, 
                   maxPower = maxPower, 
                   price = price, 
                   timestamp = timestamp)
    return data
    
# Calcula el nuevo porcentaje de bateria segun la potencia del cargador (maxPower)
def calculateBateryIncrement(bl, bc):
    velocity = maxPower*3600 #kW por segundo
    actualKW = bc * (bl/100)
    incremented = actualKW + velocity
    if (incremented >= bc):
        return float(100)
    else:
        return (incremented * 100) / bc # Porcentaje actual
    
def main():
    # Hay un coche cargando?
    isThereAcar = False
    vehicleID = "-" # Matricula del vehiculo
    bateryLevel = -1.0 # Nivel de bateria del vehiculo (%)
    bateryCapacity = -1 # Capacidad total de la bateria del vehiculo en kWh

    while True:
        if (isThereAcar == False):
            data = generateData(None, bateryLevel, bateryCapacity)
            isThereAcar = random.choice([True, False]) # Entra un coche para la siguiente iteracion?
            if(isThereAcar == True): #Generamos el vehiculo para la siguiente iteracion
                vehicleID = generateVehicleID()
                bateryLevel = float(random.randint(0,99)) 
                bateryCapacity = random.randint(40,100)

        else:
            data = generateData(vehicleID, bateryLevel, bateryCapacity)
            #Actualizar los datos del coche y eliminarlo en caso de que llegue al 100%
            if (bateryLevel >= 100):
                isThereAcar = False
                vehicleID = "-" 
                bateryLevel = -1.0 
                bateryCapacity = -1
                #No se actualiza el siguiente estado de isThereAcar aqui para dejar que haya al menos una iteracion sin coche
            else:
                bateryLevel = calculateBateryIncrement(bateryLevel, float(bateryCapacity))
            
        
        # Escribir los datos en InfluxDB
        #client.write_points(data)
        #write_api.write(bucket=bucket, org=org, record=data)
        write_api.write(bucket = bucket,
                        record = data,
                        record_measurement_key="name",
                        record_time_key = "timestamp",
                        record_tag_keys=["location"],
                        record_field_keys=["vehicleID", "energy", "bateryLevel", "maxPower", "price"])

        # Esperar un segundo antes de generar el siguiente dato
        time.sleep(1)

if __name__ == "__main__":
    main()

        