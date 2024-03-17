from pymodbus.client import ModbusSerialClient
import serial
import keyboard
import time

# Define function to read holding registers
def read_holding_registers(address, count, slave):
    # Initialize Modbus client with slave address
    client = ModbusSerialClient(method='rtu', port='COM4', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

    # Ensure client is connected
    if not client.connect():
        print("Unable to connect to Modbus server")
        return None

    # Read holding registers
    try:
        response = client.read_holding_registers(address, count, unit=slave)
        if response.isError():
            print("Modbus Error: {}".format(response))
            return None
        else:
            return response.registers
    finally:
        client.close()


while True:
    result = read_holding_registers(0x9C7D, 1 ,128)
    if result is not None:
        print("Holding register value:", result[0])
    
    
    if keyboard.is_pressed('q'):
        print("user need to quit the app")
        break

    time.sleep(0.1)
