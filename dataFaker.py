import random
import time
import string
from dataclasses import dataclass
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from collections import deque

"""
    Clase para crear los datos de los cargadores a enviar a InfluxDB.
    Measure Key: location
    Tags: name
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
    energyBill: float       # Coste total de la carga
    timestamp: int          # Marca temporal de la medicion (ns)

"""
    Clase para crear los datos de la cola de espera a enviar a InfluxDB.
    Measure Key: location
    Tags: None
    Fields: vehicle1, vehicle2, vehicle3, vehicle4, vehicle5
"""
@dataclass
class dataQueue:
    location: str           # Ubicacion del cargador
    vehicle1: str           # Matricula del vehiculo usuario 1
    vehicle2: str           # Matricula del vehiculo usuario 2
    vehicle3: str           # Matricula del vehiculo usuario 3
    vehicle4: str           # Matricula del vehiculo usuario 4
    vehicle5: str           # Matricula del vehiculo usuario 5
    timestamp: int          # Marca temporal de la medicion (ns)

"""
    Clase para crear y manejar los datos de los vehiculos.
    Genera un vehiculo con una matricula aleatoria, un nivel y capacidad de bateria aleatorio, la energia que gasta en relacion a la bateria y el coste de la carga. 
    Depende de un booleano (enter) para inicializar el vehiculo con datos (hay un vehiculo) o sin ellos (no hay un vehiculo). 
"""   
class Car:
    vehicleID: str
    bateryLevel: float
    bateryCapacity: int
    energyConsumed: float
    energyBill: float
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
            self.energyBill = 0.0
        else:
            self.vehicleID = None
            self.bateryLevel = None
            self.bateryCapacity = None
            self.energyConsumed = None
            self.energyBill = None

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
maxCarsInQueue = 5
waitingQueue = deque([Car(False) for _ in range(maxCarsInQueue)], maxCarsInQueue) #Cola de espera de coches
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
                   energyBill = car.energyBill,
                   timestamp = timestamp)
    return data

"""
    Genera los datos de la cola que se enviaran a la base de datos
    inputs: 
        -
    output:
        data : dataQueue
"""
def generateDataQueue(): 
    timestamp = int(time.time()) * 1000000000  # Convertir a nanosegundos

    # Estructura del dato para InfluxDB
    data = dataQueue(location ="stationAQueue", 
                    vehicle1 = waitingQueue[0].vehicleID, 
                    vehicle2 = waitingQueue[1].vehicleID,
                    vehicle3 = waitingQueue[2].vehicleID,
                    vehicle4 = waitingQueue[3].vehicleID,
                    vehicle5 = waitingQueue[4].vehicleID,
                    timestamp = timestamp)
    return data
    
"""
    Calcula el nuevo porcentaje de bateria segun la potencia del cargador (maxPower). Calcula la velocidad de carga por segundo
    del cargador usando la potencia maxima de este, la carga actual de la bateria en kWh segun su porcentaje y realiza los calculos 
    para sumar los kWh y devolver el coche con el nuevo porcentaje. Tambien actualiza la energia consumida por el coche y el coste de la carga.
    inputs: 
        car : Car
        price : float
    output:
        Car con el nuevo Porcentaje actual de bateria <= 100 y consumos.
"""
def calculateBateryIncrement(car, price):
    velocity = maxPower/3600 #kW por segundo
    actualKW = car.bateryCapacity * (car.bateryLevel/100) #kWh almacenados en la bateria actualmente
    incremented = actualKW + velocity 
    car.energyConsumed += velocity
    car.energyBill += price * velocity
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
        price : float (precio del kWh)
    output:
        car : Car (estado siguiente)
"""    
def calculateCarState(car, price):
    waitingQueue
    # Comprobar si hay un coche cargando     
    if (car.vehicleID == None): #No hay coche       
        # Preparar siguiente iteracion
        """isThereAcar = random.choice([True, False]) # Entra un coche para la siguiente iteracion?
        if(isThereAcar == True): #Generamos el vehiculo para la siguiente iteracion
            car = Car(True)"""
        if(waitingQueue[0].vehicleID != None): #Si hay coches en la cola, entra el primero a cargar
            car = waitingQueue.popleft()
            waitingQueue.append(Car(False))
    else:
        #Actualizar los datos del coche y eliminarlo en caso de que llegue al 100%
        if (car.bateryLevel >= 100):
            car = Car(False)
            #No se actualiza el siguiente estado de isThereAcar aqui para dejar que haya al menos una iteracion sin coche
        else:
            car = calculateBateryIncrement(car, price)
    return car

def main():
    waitingQueue 
    waitingQueue[0] = Car(True) #Añadir un coche a la cola
    waitingQueue[1] = Car(True) #Añadir un coche a la cola

    # Inicializar los coches nulos para los cargadores
    car1 = Car(False)
    car2 = Car(False)
    # Crear coche auxiliar para la cola
    carAux = Car(False)

    nextCar = random.randint(20, 30) #Tiempo en minutos que tarda el siguiente coche en entrar
    nextCounter = 0 #Contador para saber cuando entra el siguiente coche

    while True:
        price = round(random.uniform (0.15, 0.75),2)
        data = generateData(car1, "Charger1", price) #generateData(car1)
        data2 = generateData(car2, "Charger2", price) #generateData(car2)
        dataQueue = generateDataQueue()
        
        # Escribir los datos en InfluxDB
        write_api.write(bucket = bucket,
                        record = data,
                        record_measurement_key="location",
                        record_time_key = "timestamp",
                        record_tag_keys=["name"],
                        record_field_keys=["vehicleID", "energyConsumed", "bateryLevel", "maxPower", "price", "energyBill"])
        write_api.write(bucket = bucket,
                        record = data2,
                        record_measurement_key="location",
                        record_time_key = "timestamp",
                        record_tag_keys=["name"],
                        record_field_keys=["vehicleID", "energyConsumed", "bateryLevel", "maxPower", "price", "energyBill"])
        #Enviar los Datos de la cola (dataQueue) a InfluxDB
        write_api.write(bucket = bucket,
                        record = dataQueue,
                        record_measurement_key="location",
                        record_time_key = "timestamp",
                        record_tag_keys=[],
                        record_field_keys=["vehicle1", "vehicle2", "vehicle3", "vehicle4", "vehicle5"])
        
        #Actualizar el estado del coche
        car1 = calculateCarState(car1, price)
        car2 = calculateCarState(car2, price)

        #Actualizar el estado de la cola
        nextCounter = nextCounter + 1
        #if(nextCounter == nextCar*60 and len(queue) < maxCarsInQueue): #Comprobar si el ultimo elemento es matricula none
        if(nextCounter == nextCar*60): #El contador ha llegado al tiempo de llegada
            if(waitingQueue[maxCarsInQueue-1].vehicleID == None): #Comprobar si hay una posición vacia en la cola
                #queue.append(Car(True))
                #Añadir un coche a la cola en la primera posicion vacia
                waitingQueue[maxCarsInQueue - waitingQueue.count(carAux)] = Car(True)
            #Nuevo tiempo de llegada para el siguiente coche
            nextCar = random.randint(20, 30)
            nextCounter = 0

        # Esperar un segundo antes de generar el siguiente dato
        time.sleep(1)

if __name__ == "__main__":
    main()

