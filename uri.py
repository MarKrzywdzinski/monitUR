import sys
import array
import struct
import time
import json
import math
import serial.tools.list_ports
import sqlite3
from sqlite3 import Error
from datetime import datetime
from serial import Serial, SerialException

class PICmeBot_AmperWorks_SensorBoard():
    def __init__(self, port, baudrate=57600, timeout=5.0):
        self.last_read = datetime.now()
        self.timeout = timeout
        self.port = port
        self.baudrate = baudrate
        self.db_path = 'C:\\Users\\markr\\Desktop\\Programy\\rpi_latest\\raspberry\\SENSORS.db'

        while True:
            try:
                self.mySerialPort = Serial(self.port, self.baudrate, timeout=self.timeout, write_timeout=self.timeout)
                break
            except SerialException as e:
                print("Serial open error: %s", e)
                time.sleep(3)
        time.sleep(1)

        self.lastsync = datetime.now()
        self.lastsync_lost = self.lastsync

    def ReceiveNewData(self):              
        read_step = None
        while True:
            if (datetime.now() - self.lastsync).total_seconds() > (self.timeout * 3) and (self.lastsync_lost < self.lastsync):
                print("Synchronization lost!")
                self.lastsync_lost = datetime.now() 

            try:
                if self.mySerialPort.inWaiting() < 1:
                    time.sleep(0.001)
                    continue

                read_step = 'header'
                rec_header = self.mySerialPort.read(1)
                if (rec_header != b'\xAA'):
                    continue
                rec_header = self.mySerialPort.read(1)
                if (rec_header != b'\x55'):
                    continue

                read_step = 'current_sensors'
                current_sensor_1_bytes = self.mySerialPort.read(2)
                current_sensor_2_bytes = self.mySerialPort.read(2)
                current_sensor_3_bytes = self.mySerialPort.read(2)
                current_sensor_4_bytes = self.mySerialPort.read(2)
                current_sensor_5_bytes = self.mySerialPort.read(2)
                current_sensor_6_bytes = self.mySerialPort.read(2)
                read_step = 'temperature_sensors'
                temperature_sensor_1_bytes = self.mySerialPort.read(2)
                temperature_sensor_2_bytes = self.mySerialPort.read(2)
                read_step = 'inputs_and_outputs'
                inputs_output_byte = self.mySerialPort.read(1)                
                read_step = 'checksum'
                rec_checksum = self.mySerialPort.read(1)

                checksum = sum(array.array('B', current_sensor_1_bytes + current_sensor_2_bytes + current_sensor_3_bytes + current_sensor_4_bytes + current_sensor_5_bytes + current_sensor_6_bytes + temperature_sensor_1_bytes + temperature_sensor_2_bytes + inputs_output_byte)) % 256
                if checksum != int.from_bytes(rec_checksum,'little'):
                    print("Checksum incorrect")
                    continue
               
                self.lastsync = datetime.now() 
              
                read_step = 'interpret_received_data'
                scale_temperature = 0.25
                Vref = 3.3
                ACrange = 20
                # wartosc skuteczna; napiecie pomiaru; skalowanie do czujnika 1V=ACrange A; podziel na 2 bo mierzymy peak2peak
                scale_current = (math.sqrt(2.0)/2.0) * (Vref / 4096) * ACrange / 2.0
                current_sensor_1 = scale_current * int.from_bytes(current_sensor_1_bytes, "little") 
                current_sensor_2 = scale_current * int.from_bytes(current_sensor_2_bytes, "little")
                current_sensor_3 = scale_current * int.from_bytes(current_sensor_3_bytes, "little")
                current_sensor_4 = scale_current * int.from_bytes(current_sensor_4_bytes, "little")
                current_sensor_5 = scale_current * int.from_bytes(current_sensor_5_bytes, "little")
                current_sensor_6 = scale_current * int.from_bytes(current_sensor_6_bytes, "little")
                temperature_sensor_1 = scale_temperature * int.from_bytes(temperature_sensor_1_bytes, "little")
                temperature_sensor_2 = scale_temperature * int.from_bytes(temperature_sensor_2_bytes, "little")
                inputs_output = int.from_bytes(inputs_output_byte, "little")
    
                
                receivedData = {
                    "update time": self.lastsync.strftime("%d/%m/%Y, %H:%M:%S.%f"),
                    "current_sensor_1": current_sensor_1 if current_sensor_1 >0.38 else 0,
                    "current_sensor_2": current_sensor_2 if current_sensor_2 >0.38 else 0,
                    "current_sensor_3": current_sensor_3 if current_sensor_3 >0.38 else 0,
                    "current_sensor_4": current_sensor_4 if current_sensor_4 >0.38 else 0,
                    "current_sensor_5": current_sensor_5 if current_sensor_5 >0.38 else 0,
                    "current_sensor_6": current_sensor_6 if current_sensor_6 >0.38 else 0,
                    "temperature_sensor_1": temperature_sensor_1,
                    "temperature_sensor_2": temperature_sensor_2,
                    "input_1": ((inputs_output & 1) == 0),
                    "input_2": ((inputs_output & 2) == 0),
                    "input_3": ((inputs_output & 4) == 0),
                    "output_1": not((inputs_output & 8) == 0),
                    "output_2": not((inputs_output & 16) == 0),
                    "output_3": not((inputs_output & 32) == 0)
                    }
                
                try:
                    conn = None
                    try:
                        conn = sqlite3.connect(f'file:{self.db_path}?mode=ro', uri=True, host= '192.168.1.96')       # create a database connection to a SQLite database
                        print( 'CON')
                    except Error as e:
                        print(e)
                    if conn is not None:
                        try:
                            conn.execute('''CREATE TABLE plots
                                    (update_time TEXT, current_sensor_1 REAL, current_sensor_2 REAL, current_sensor_3 REAL, current_sensor_4 REAL, current_sensor_5 REAL, current_sensor_6 REAL, temperature_sensor_1 REAL, temperature_sensor_2 REAL, input_1 BOOLEAN, input_2 BOOLEAN, input_3 BOOLEAN, output_1 BOOLEAN, output_2 BOOLEAN, output_3 BOOLEAN, kWh REAL)''')
                            print("Table created successfully")
                        except Error as e:
                            print(e)
                    else:
                        print("Error! cannot create the database connection.")
                    entities = (self.lastsync.strftime("%d/%m/%Y, %H:%M:%S.%f"), 
                receivedData['current_sensor_1'],
                receivedData['current_sensor_2'],
                receivedData['current_sensor_3'],
                receivedData['current_sensor_4'],
                receivedData['current_sensor_5'],
                receivedData['current_sensor_6'],
                receivedData['temperature_sensor_1'],
                receivedData['temperature_sensor_2'],
                receivedData['input_1'],
                receivedData['input_2'],
                receivedData['input_3'],
                receivedData['output_1'],
                receivedData['output_2'],
                receivedData['output_3'],
                (receivedData['current_sensor_1'] * 230 + receivedData['current_sensor_2'] * 230 + receivedData['current_sensor_3'] * 230 ) / 1000.0,
               )
                    try:
                        conn.execute('''INSERT INTO plots(update_time, current_sensor_1, current_sensor_2, current_sensor_3, current_sensor_4, current_sensor_5, current_sensor_6, temperature_sensor_1, temperature_sensor_2, input_1, input_2, input_3, output_1, output_2, output_3, kWh) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', entities)
                        conn.commit()
                        print("Record created successfully")
                    except Error as e:
                        print(e)
                except:
                    print('cos kurwa nie tak')
                #bufor = []
                ##bufor.append(receivedData['update time'])
                #bufor.append(receivedData['current_sensor_1'])
                #bufor.append(receivedData['current_sensor_2'])
                #bufor.append(receivedData['current_sensor_3'])
                #bufor.append(receivedData['current_sensor_4'])
                #bufor.append(receivedData['current_sensor_5'])
                #bufor.append(receivedData['current_sensor_6'])
                #bufor.append(receivedData['temperature_sensor_1'])
                #bufor.append(receivedData['temperature_sensor_2'])
                #bufor.append(receivedData['input_1'])
                #bufor.append(receivedData['input_2'])
                #bufor.append(receivedData['input_3'])
                #bufor.append(receivedData['output_1'])
                #bufor.append(receivedData['output_2'])
                #bufor.append(receivedData['output_3'])
                #bufor_kWh = (receivedData['current_sensor_1'] * 230 + receivedData['current_sensor_2'] * 230 + receivedData['current_sensor_3'] * 230 ) / 100.0
                #bufor.append(bufor_kWh)
                #bufor_OnOff = 0 if receivedData['current_sensor_1'] and receivedData['current_sensor_2'] and receivedData['current_sensor_3'] == 0 else 1
                #bufor.append(bufor_OnOff)
                #f = open("fullData.csv", 'a')
                #for i in range(len(bufor)):
                #    f.write(str(bufor[i]))
                #    f.write('   ')
                #f.write('\n')
                #f.close()
            except IOError as exc:
                print('[IOError] read step: %s' % read_step)
                print('[IOError] error: %s' % exc)
                self.port.flushInput()
                continue

            return receivedData


    def SendNewOutputValues(self, output_1, output_2, output_3 ):
        data = 0
        if output_1 == True or output_1 == 1:
            data |= 1
        if output_2 == True or output_2 == 1:
            data |= 2
        if output_3 == True or output_3 == 1:
            data |= 4

        data_byte = struct.pack('B', data)

        checksum = (sum(array.array('B', data_byte)) % 256)
        checksum_bytes = struct.pack('B', checksum)

        message = b'\xAA' + b'\x55' + data_byte + checksum_bytes

        self.mySerialPort.write(message)
        self.mySerialPort.flush()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        ports = serial.tools.list_ports.comports()
        port = 0
        for p in ports:
            if ("04D8" in p.hwid or "04d8" in p.hwid) and ("000A" in p.hwid or "000a" in p.hwid):
                port = p.device
                break
        if port == 0:
            print('No device attached to USB! Try by providing serialport path!')
            exit()
    else:
        port = sys.argv(2)
        
    PmB = PICmeBot_AmperWorks_SensorBoard(port)

    workingInProgress = False

    while True:
        try:
            # Read new data and save to file

            newData = PmB.ReceiveNewData()
            jsonString = json.dumps(newData)

            f = open("PmB_SensorsValues.json", "w")
            f.write(jsonString)
            f.close()

            # Read new Relay values and send to the board
            f = open("PmB_RelayValues.json", "r")
            jsonString = f.read()
            f.close()
            readData = json.loads(jsonString)
            PmB.SendNewOutputValues(readData['output_1'], readData['output_2'], readData['output_3'])

            if workingInProgress == False:
                print('Connection successfull! Data are two-way transfered...')
                workingInProgress = True

            time.sleep(0.5)
            PmB.mySerialPort.reset_input_buffer()
        except:
            print('Read or Write error! Reconnecting...')
            try:
                PmB.mySerialPort.close()
            except:
                pass
            PmB = PICmeBot_AmperWorks_SensorBoard(port)
            workingInProgress = False
