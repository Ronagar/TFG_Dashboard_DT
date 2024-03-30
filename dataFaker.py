from faker import Faker
import random
import time
import string
from influxdb import InfluxDBClient

# Configuración de InfluxDB
host = 'localhost'
port = 8086
user = 'usuario'
password = 'contraseña'
dbname = 'nombre_base_de_datos'

# Conexión a InfluxDB
client = InfluxDBClient(host, port, user, password, dbname)

###############Variables globales:########################
maxPower = random.randint(20, 70) # Potencia maxima del cargador (kWh).
##########################################################

# Genera la matricula del vehiculo que entra a cargar
def generateVehicleID():
    letras = ""
    for _ in range(3):
        letras += random.choice(string.ascii_uppercase)
    return str(random.randint(1000, 9999)) + letras

# Genera los datos que se enviaran a la base de datos
def generateData(car, bateryLevel, bateryCapacity):
    # En la version inicial, todos los coches se quedarán hasta completar la carga. Deberían poder desconectarse antes de completar la carga
    energy = 0
    if (car != None): 
        energy = bateryCapacity - (bateryCapacity * (bateryLevel/100))

    #energy = random.uniform(5,50) # energia consumida en la carga en kWh
    price = random.uniform (0.05, 0.30) # Precio por kWh. Estudiar si merece la pena tratar de que los precios sean reales
    timestamp = int(time.time()) * 1000000000  # Convertir a nanosegundos

    # Estructura del dato para InfluxDB
    data = [
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
    ]
    return data
    
# Calcula el nuevo porcentaje de bateria segun la potencia del cargador (maxPower)
def calculateBateryIncrement(bl, bc):
    velocity = maxPower*3600 #kW por segundo
    actualKW = bc * (bl/100)
    incremented = actualKW + velocity
    if (incremented >= bc):
        return 100
    else:
        return (incremented * 100) / bc # Porcentaje actual
    
def main():
    # Hay un coche cargando?
    isThereAcar = False
    vehicleID = None # Matricula del vehiculo
    bateryLevel = -1 # Nivel de bateria del vehiculo (%)
    bateryCapacity = None # Capacidad total de la bateria del vehiculo en kWh

    while True:
        if (isThereAcar == False):
            data = generateData(None, bateryLevel, bateryCapacity)
            isThereAcar = random.choice([True, False]) # Entra un coche para la siguiente iteracion?
            if(isThereAcar == True):
                vehicleID = generateVehicleID
                bateryLevel = random.uniform(0,99) 
                bateryCapacity = random.randint(40,100)

        else:
            data = generateData(vehicleID, bateryLevel, bateryCapacity)
            #Actualizar los datos del coche y eliminarlo en caso de que llegue al 100%
            if (bateryLevel >= 100):
                isThereAcar = False
                vehicleID = None 
                bateryLevel = -1 
                bateryCapacity = None
                #No se actualiza el siguiente estado de isThereAcar aqui para dejar que haya al menos una iteracion sin coche
            else:
                bateryLevel = calculateBateryIncrement(bateryLevel, bateryCapacity)
            
        
        # Escribir los datos en InfluxDB
        client.write_points(data)

        # Esperar un segundo antes de generar el siguiente dato
        time.sleep(1)

if __name__ == "__main__":
    main()

        
