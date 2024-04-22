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
    Fields: vehicleID, energyConsumed, bateryLevel, maxPower, price
"""
@dataclass
class Charger:
    name: str               # Nombre/ID del cargador
    location: str           # Ubicacion del cargador
    vehicleID: str          # Matricula del vehiculo usuario
    energyConsumed: float   # Energia consumida en la carga total en kWh. En la version inicial, todos los coches se quedarán hasta completar la carga. Deberían poder desconectarse antes de completar la carga
    bateryLevel: float      # Nivel de bateria del vehiculo (%)
    maxPower: int           # Potencia maxima del cargador (kWh).
    price: float            # Precio por kWh. TODO Estudiar si merece la pena tratar de que los precios sean reales
    timestamp: int          # Marca temporal de la medicion (ns)

"""
    Clase para crear y manejar los datos de los vehiculo.
    Genera un vehiculo con una matricula aleatoria, un nivel y capacidad de bateria aleatorio y la energia que va a gastar en relacion a la bateria. 
    Depende de un booleano (enter) para inicializar el vehiculo con datos (hay un vehiculo) o sin ellos (no hay un vehiculo). 
"""   
class Car:
    vehicleID: str
    bateryLevel: float
    bateryCapacity: int
    energyConsumed: float
    """
        Genera la matricula del vehiculo que entra a cargar
    """
    def generateVehicleID(self):
        letras = ""
        for _ in range(3):
            letras += random.choice(string.ascii_uppercase)
        return str(random.randint(1000, 9999)) + letras
    
    def __init__(self, enter):
        if (enter):
            self.vehicleID = self.generateVehicleID()
            self.bateryLevel = float(random.randint(0,99)) 
            self.bateryCapacity = random.randint(40,100)
            self.energyConsumed = 0.0
        else:
            self.vehicleID = None
            self.bateryLevel = None
            self.bateryCapacity = None
            self.energyConsumed = None

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
    Genera los datos que se enviaran a la base de datos
    inputs: 
        car : Car 
        chargerID : str
        price : float
    output:
        data : Charger
"""
def generateData(car, chargerID, price): 
    timestamp = int(time.time()) * 1000000000  # Convertir a nanosegundos

    # Estructura del dato para InfluxDB
    data = Charger(name = chargerID,
                   location ="stationA", 
                   vehicleID = car.vehicleID, 
                   energyConsumed = car.energyConsumed, 
                   bateryLevel = car.bateryLevel, 
                   maxPower = maxPower, 
                   price = price, 
                   timestamp = timestamp)
    return data
    
"""
    Calcula el nuevo porcentaje de bateria segun la potencia del cargador (maxPower). Calcula la velocidad de carga por segundo
    del cargador usando la potencia maxima de este, la carga actual de la bateria en kWh segun su porcentaje y realiza los calculos 
    para sumar los kWh y devolver el coche con el nuevo porcentaje. Tambien actualiza la energia consumida por el coche.
    inputs: 
        car : Car
    output:
        Porcentaje actual de bateria <= 100.
"""
def calculateBateryIncrement(car):
    velocity = maxPower/3600 #kW por segundo
    actualKW = car.bateryCapacity * (car.bateryLevel/100) #kWh almacenados en la bateria actualmente
    incremented = actualKW + velocity 
    car.energyConsumed += velocity
    if (incremented >= car.bateryCapacity):
        car.bateryLevel = float(100)
    else:
        car.bateryLevel = (incremented * 100) / car.bateryCapacity # Porcentaje actual
    return car
    
"""
    Calcula el estado del coche en la siguiente iteracion. Si el coche esta cargando, se comprueba si ha llegado al 100%. En caso de estar al 100%, se elimina el coche, 
    si no, se actualiza el porcentaje de bateria.
    input:
        car : Car (estado actual)
    output:
        car : Car (estado siguiente)
"""    
def calculateCarState(car):
    # Comprobar si hay un coche cargando     
        if (car.vehicleID == None): #No hay coche       
            # Preparar siguiente iteracion
            isThereAcar = random.choice([True, False]) # Entra un coche para la siguiente iteracion?
            if(isThereAcar == True): #Generamos el vehiculo para la siguiente iteracion
                car = Car(True)
        else:
            #Actualizar los datos del coche y eliminarlo en caso de que llegue al 100%
            if (car.bateryLevel >= 100):
                car = Car(False)
                #No se actualiza el siguiente estado de isThereAcar aqui para dejar que haya al menos una iteracion sin coche
            else:
                car = calculateBateryIncrement(car)
        return car

def main():
    # Inicializar los coches nulos
    car1 = Car(False)
    car2 = Car(False)

    while True:
        price = round(random.uniform (0.05, 0.30),2)
        data = generateData(car1, "Charger1", price) #generateData(car1)
        data2 = generateData(car2, "Charger2", price) #generateData(car2)
        
        # Escribir los datos en InfluxDB
        write_api.write(bucket = bucket,
                        record = data,
                        record_measurement_key="location",
                        record_time_key = "timestamp",
                        record_tag_keys=["name"],
                        record_field_keys=["vehicleID", "energyConsumed", "bateryLevel", "maxPower", "price"])
        write_api.write(bucket = bucket,
                        record = data2,
                        record_measurement_key="location",
                        record_time_key = "timestamp",
                        record_tag_keys=["name"],
                        record_field_keys=["vehicleID", "energyConsumed", "bateryLevel", "maxPower", "price"])
        
        #Actualizar el estado del coche
        car1 = calculateCarState(car1)
        car2 = calculateCarState(car2)

        # Esperar un segundo antes de generar el siguiente dato
        time.sleep(1)

if __name__ == "__main__":
    main()

