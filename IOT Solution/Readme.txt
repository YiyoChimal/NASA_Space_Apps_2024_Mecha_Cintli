# IOT Solution
## Information of the file
In this file you can find the C code of the microcontrollers use at the prototypes, the electrical and pcb design that was mede using KiCad and the Cad design that can give you the over view of how can be the product .

## General Description:
We design two prototypes to obtain real time information about the conditions of the crop and send it to a server via internet, where all the information can be analise to give the user by his app advises or the harsh data. All this is achive by using varios mudules of sensor that have to be located all over the crop field that send the infomation to a main unit. All the information is transmited using a LoRa Protocol that have a wide range of data tranmision. 

## Sensor Module
General specifications:
Devise that obtain information about the conditions of the crop like thanks to it sensor. The variables that can meassure are: Soil moisture, atmospheric humidity, atmospheric temperature, atmospheric pressure, PH and nutrients. And send the information to the Resiver-Tranmiter Module using a LoRa protocol every 1h but it can be configure on the Resiver-Tranmiter Module.

## Resiver-Tranmiter Module
General specifications:
This module it is used to configure the sesnoses modules, it sends the indication for them to send the information using the LoRa Comunication, and it sends the data obtained from all the sensors to a server via the Internet where it is processed for analysis.
It is connected to internet via an Ethernet port
