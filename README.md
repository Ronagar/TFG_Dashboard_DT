# TFG_Dashboard_DT

## Resumen
En el ámbito de la creación de las ciudades inteligentes y sostenibles, el uso de medios de transporte no contaminantes es fundamental. Este objetivo está en
producir un auge en la compra de vehículos eléctricos, y esto trae consigo la necesidad de dotar a las ciudades con las infraestructuras necesarias para su carga y
mantenimiento. El tipo de infraestructura más importante para el uso de vehículos eléctricos son las estaciones de carga. Estas estaciones de carga son lo suficientemente complejas como para que merezca la pena la creación de gemelos digitales
de estas infraestructuras. Un gemelo digital cuenta con una funcionalidad muy amplia que abarca desde la monitorización, a la simulación y predicción de comportamientos.

Este trabajo de fin de grado se centra en el desarrollo de una plataforma de monitorización en tiempo real de una estación de carga de vehículos eléctricos,
tratando de priorizar el uso de tecnologías de código abierto y facilitando la incorporación de más estaciones al sistema.

## Objetivo
El objetivo principal del trabajo es crear una herramienta que facilite la monitorización y el estudio del funcionamiento de una estación de
carga de vehículos eléctricos por un técnico o gestor de la misma, sin renunciar a las funciones de automatización. 

El sistema está desarrollado utilizando la tecnología de código abierto ofrecida por Grafana conectada a una base de datos de series temporales InfluxDB en
la que se almacenan todos los datos del gemelo. El lenguaje utilizado para las consultas será Flux. La base de datos se alimenta con datos de prueba creados con un script de Python que simula
el funcionamiento de una estación de carga real.

## Documentación
Toda la documentación del proyecto se encuentra en el pdf de la [memoria](https://github.com/Ronagar/TFG_Dashboard_DT/blob/main/Memoria_TFG.pdf).
