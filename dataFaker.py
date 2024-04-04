#from faker import Faker
import random
import time
import string
from dataclasses import dataclass
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

"""
    Clase para crear los datos a enviar a InfluxDB.
    Measure Key: name
    Tags: location
    Fields: vehicleID, energy, bateryLevel, maxPower, price
"""
@dataclass
class Charger:
    name: str               # Nombre/ID del cargador
    location: str           # Ubicacion del cargador
    vehicleID: str          # Matricula del vehiculo usuario
    energy: float           # Energia consumida en la carga total en kWh. En la version inicial, todos los coches se quedarán hasta completar la carga. Deberían poder desconectarse antes de completar la carga
    bateryLevel: float      # Nivel de bateria del vehiculo (%)
    maxPower: int           # Potencia maxima del cargador (kWh).
    price: float            # Precio por kWh. TODO Estudiar si merece la pena tratar de que los precios sean reales
    timestamp: int          # Marca temporal de la medicion (ns)
    

# Configuración de InfluxDB
myToken = "myToken"
org = "myOrg"
url = "http://localhost:8086"
bucket = "myBucket"

# Conexión a InfluxDB
client = influxdb_client.InfluxDBClient(url=url, token=myToken, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

###############Variables globales:########################
maxPower = random.randint(20, 70) 
##########################################################

"""
    Genera la matricula del vehiculo que entra a cargar
"""
def generateVehicleID():
    letras = ""
    for _ in range(3):
        letras += random.choice(string.ascii_uppercase)
    return str(random.randint(1000, 9999)) + letras

"""
    Genera los datos que se enviaran a la base de datos
    inputs: 
        car : str (vehicleID)
        bateryLevel : float
        bateryCapacity : int
    output:
        data : Charger
"""
def generateData(car, bateryLevel, bateryCapacity):
    energy = 0.0
    if (car != None): 
        energy = float(bateryCapacity - (bateryCapacity * (bateryLevel/100)))
 
    price = round(random.uniform (0.05, 0.30),2)
    timestamp = int(time.time()) * 1000000000  # Convertir a nanosegundos

    # Estructura del dato para InfluxDB
    data = Charger(name = "Charger",
                   location ="stationA", 
                   vehicleID = car, 
                   energy = energy, 
                   bateryLevel = bateryLevel, 
                   maxPower = maxPower, 
                   price = price, 
                   timestamp = timestamp)
    return data
    
"""
    Calcula el nuevo porcentaje de bateria segun la potencia del cargador (maxPower). Calcula la velocidad de carga por segundo
    del cargador usando la potencia maxima de este, la carga actual de la bateria en kWh segun su porcentaje y realiza los calculos 
    para sumar los kWh y devolver el porcentaje.
    inputs: 
        bl : float (bateryLevel)
        bc : float (bateryCapacity)
    output:
        Porcentaje actual de bateria <= 100.
"""
def calculateBateryIncrement(bl, bc):
    velocity = maxPower/3600 #kW por segundo
    actualKW = bc * (bl/100) #kWh almacenados en la bateria actualmente
    incremented = actualKW + velocity 
    if (incremented >= bc):
        return float(100)
    else:
        return (incremented * 100) / bc # Porcentaje actual
    

def main():
    # Hay un coche cargando?
    isThereAcar = False
    vehicleID = "-" 
    bateryLevel = -1.0 
    bateryCapacity = -1 # Capacidad total de la bateria del vehiculo en kWh

    while True:
        if (isThereAcar == False):
            data = generateData(None, bateryLevel, bateryCapacity)

            # Preparar siguiente iteracion
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

        