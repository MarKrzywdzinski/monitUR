import sys
import array
import struct
import time
import json
import math
import serial.tools.list_ports
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
from serial import Serial, SerialException

class PICmeBot_AmperWorks_SensorBoard():
    def __init__(self, port, baudrate=57600, timeout=5.0):
        self.last_read = datetime.now()
        self.timeout = timeout
        self.port = port
        self.baudrate = baudrate

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
        self.last_value = 0
        self.last_date = datetime.now()
        self.conn = None
        self.thresholds ={
            'temp': 40,
            'asymetry': 80,
            'input': True,
        }
        try:
            self.conn = sqlite3.connect('sensor_new.db')       # create a database connection to a SQLite database
            print(sqlite3.version)
        except Error as e:
            print(e)
        if self.conn is not None:
            try:
                self.conn.execute('''CREATE TABLE data_center
                        (update_time TEXT, 
                                  cabinet_L1 REAL, 
                                  warning_current_sensor_1 BOOLEAN, 
                                  cabinet_L2 REAL, 
                                  warning_current_sensor_2 BOOLEAN, 
                                  cabinet_L3 REAL, 
                                  warning_current_sensor_3 BOOLEAN, 
                                  motor_L1 REAL, 
                                  warning_current_sensor_4 BOOLEAN, 
                                  motor_L2 REAL, 
                                  warning_current_sensor_5 BOOLEAN, 
                                  motor_L3 REAL, 
                                  warning_current_sensor_6 BOOLEAN,
                                  temperature_sensor_1 REAL, 
                                  warning_temperature_1 BOOLEAN,
                                  temperature_sensor_2 REAL, 
                                  warning_temperature_2 BOOLEAN,
                                  input_1 BOOLEAN, 
                                  warning_input_1 BOOLEAN,
                                  input_2 BOOLEAN, 
                                  warning_input_2 BOOLEAN,
                                  input_3 BOOLEAN, 
                                  warning_input_3 BOOLEAN,
                                  output_1 BOOLEAN, 
                                  output_2 BOOLEAN, 
                                  output_3 BOOLEAN, 
                                  kW REAL, 
                                  cabinet_amperage REAL, 
                                  motor_amperage REAL, 
                                  day_kWh REAL, 
                                  biggest_kWh_of_day REAL,
                                  average_kWh_if_day REAL,
                                  cabinet_asymetrii_L1 REAL,
                                  cabinet_asymetrii_L2 REAL, 
                                  cabinet_asymetrii_L3 REAL, 
                                  motor_asymetrii_L1 REAL, 
                                  motor_asymetrii_L2 REAL, 
                                  motor_asymetrii_L3 REAL)''')
                print("Table created successfully")
                #print("chusahduasjduajsudjasudjasujduashdiuashodiuashoidhsao")
                            # Sprawdzenie długości tabeli
                
            except Error as e:
                print(e)
        else:
            print("Error! cannot create the database connection.")
        
    
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
                

                if current_sensor_1 <= 0.39:
                   current_sensor_1 = 0.0
                else:
                   pass
                if current_sensor_2 <= 0.39:
                   current_sensor_2 = 0.0
                else:
                   pass
                if current_sensor_3 <= 0.39:
                   current_sensor_3 = 0.0
                else:
                   pass
                if current_sensor_4 <= 0.39:
                   current_sensor_4 = 0.0
                else:
                   pass
                if current_sensor_5 <= 0.39:
                   current_sensor_5 = 0.0
                else:
                   pass
                if current_sensor_6 <= 0.39:
                   current_sensor_6 = 0.0
                else:
                   pass
                print('current', current_sensor_1)
                ################################################BACKEND SHIT
                #print('YYYYYYYYYYOOOOOOOOOOOOOLOOOOOOOOOOOOOOO')
                cursor = self.conn.cursor()
                one_hour_ago = datetime.now() - timedelta(hours=1)
                query = "SELECT kW FROM data_center WHERE update_time > ?"
                cursor.execute(query, (one_hour_ago,))
                #print('YYYYYYYYYYOOOOOOOOOOOOOLOOOOOOOOOOOOOOO2')
                self.kW = cursor.fetchall()
                
                for i in range(len(self.kW)):
                    self.kW[i] = self.kW[i][0]
                try:
                    self.average_kW = sum(self.kW)/len(self.kW)
                    #print('AVEEEERAAAAAAAAAGEEEEEE: ', self.average_kW)
                    
                except:
                    self.average_kW = 0.0
                try:    
                    self.biggest_kW = max(self.kW)
                    #print('biggerst : ', self.biggest_kW)
                    #print('sdasdasdasd : ', self.kW)
                except:
                    self.biggest_kW = 0.0
                
                #print('YYYYYYYYYYOOOOOOOOOOOOOLOOOOOOOOOOOOOOO5')
                #print('YYYYYYYYYYOOOOOOOOOOOOOLOOOOOOOOOOOOOOO3')



                try:
                    # Wyznaczanie asymetrii silnika
                    self.average_motor_amperage = (current_sensor_4 + current_sensor_5 + current_sensor_6)/ 3

                    self.max_motor_bufor = [self.average_motor_amperage - current_sensor_4, self.average_motor_amperage - current_sensor_5, self.average_motor_amperage - current_sensor_6] 
                    
                    self.max_motor_bufor[0] = round(self.max_motor_bufor[0], 6)
                    self.max_motor_bufor[1] = round(self.max_motor_bufor[1], 6)
                    self.max_motor_bufor[2] = round(self.max_motor_bufor[2], 6)
                    try:
                        self.biggest_motor_deviation = max(self.max_motor_bufor)
                        self.motor_asymetry_percent_list = [self.biggest_motor_deviation/current_sensor_4*100, self.biggest_motor_deviation/current_sensor_5*100, self.biggest_motor_deviation/current_sensor_6*100]
                    except:
                        self.motor_asymetry_percent_list = [0, 0, 0] ## TO DO SQL
                    # Wyznaczanie asymetrii szafy
                    
                    
                    self.average_cabinet_amperage = (current_sensor_1 + current_sensor_2 + current_sensor_3)/ 3
                    self.max_cabinet_bufor = [self.average_cabinet_amperage - current_sensor_1, self.average_cabinet_amperage - current_sensor_2, self.average_cabinet_amperage - current_sensor_3] 
                    self.max_cabinet_bufor[0] = round(self.max_cabinet_bufor[0], 6)
                    self.max_cabinet_bufor[1] = round(self.max_cabinet_bufor[1], 6)
                    self.max_cabinet_bufor[2] = round(self.max_cabinet_bufor[2], 6)
                    
                    try:
                        self.biggest_cabinet_deviation = max(self.max_cabinet_bufor)
                        self.cabinet_asymetry_percent_list = [self.biggest_cabinet_deviation/current_sensor_1*100, self.biggest_cabinet_deviation/current_sensor_2*100, self.biggest_cabinet_deviation/current_sensor_3*100]
                    except:
                        self.cabinet_asymetry_percent_list = [0, 0, 0] ## TO DO SQL
                    #print(self.cabinet_asymetry_percent_list)    

                    self.Cabinet_Amperage = current_sensor_1 + current_sensor_2 + current_sensor_3 ## TO DO SQL
                    self.Motor_Amperage = current_sensor_4 + current_sensor_5 + current_sensor_6 ## TO DO SQL
            
                    self.time_diff = datetime.now() - self.last_date
                    self.last_date = datetime.now()
                    #print('chuuuuuuuuuuuuuuuuuuuuuuuuuj', self.time_diff.total_seconds())
                    self.kW = (current_sensor_1*230 + current_sensor_2*230 + current_sensor_3*230)/1000.0 ## TO DO SQL
                    self.sum_of_kWh = (self.kW)*(self.time_diff.total_seconds()/3600) + self.last_value 
                    #print('chuuuuuuuuuuuuuuuuuuuuuuuuuj2')
                    if datetime.today().day != self.last_date.day:
                        self.sum_of_kWh = 0 ## TO DO SQL
                        self.last_value = 0 ## TO DO SQL

                    else:
                        self.last_value = self.sum_of_kWh ## TO DO SQL
                    ##print('cosocsoco ' , self.last_date.day, datetime.today().day)
                    #print('last_values: ',self.last_value)

                    self.Warning_Motor_L1_Asymetrii = True if self.motor_asymetry_percent_list[0] > self.thresholds['asymetry'] else False
                    self.Warning_Motor_L2_Asymetrii = True if self.motor_asymetry_percent_list[1] > self.thresholds['asymetry'] else False
                    self.Warning_Motor_L3_Asymetrii = True if self.motor_asymetry_percent_list[2] > self.thresholds['asymetry'] else False
                    self.Warning_Cabinet_L1_Asymetrii = True if self.cabinet_asymetry_percent_list[0] > self.thresholds['asymetry'] else False
                    self.Warning_Cabinet_L2_Asymetrii = True if self.cabinet_asymetry_percent_list[1] > self.thresholds['asymetry'] else False
                    self.Warning_Cabinet_L3_Asymetrii = True if self.cabinet_asymetry_percent_list[2] > self.thresholds['asymetry'] else False
                    self.Warning_Temperature_T1 = True if temperature_sensor_1 > self.thresholds['temp'] else False
                    self.Warning_Temperature_T2 = True if temperature_sensor_2 > self.thresholds['temp'] else False
                    self.Warning_Input_1 = True if ((inputs_output & 1) == 0) == self.thresholds['input'] else False
                    self.Warning_Input_2 = True if ((inputs_output & 2) == 0) == self.thresholds['input'] else False
                    self.Warning_Input_3 = True if ((inputs_output & 4) == 0) == self.thresholds['input'] else False
                    #print(self.Warning_Temperature_T2)
                    
                    self.emergency_thresholds = [
                        self.Warning_Motor_L1_Asymetrii,
                        self.Warning_Motor_L2_Asymetrii,
                        self.Warning_Motor_L3_Asymetrii,
                        self.Warning_Cabinet_L1_Asymetrii,
                        self.Warning_Cabinet_L2_Asymetrii,
                        self.Warning_Cabinet_L3_Asymetrii,
                        self.Warning_Temperature_T1,
                        self.Warning_Temperature_T2,
                        self.Warning_Input_1,
                        self.Warning_Input_2,
                        self.Warning_Input_3 
                    ]
                   
                    self.alarm = any(self.emergency_thresholds)  
                    #print('alarm', self.alarm)
                    if self.alarm == True:
                        self.SendNewOutputValues(True, True, True)
                    else:
                        self.SendNewOutputValues(False, False, False)



                except:
                    print("Some error in asymetry calculation")  



                
                receivedData = {
                    "update time": self.lastsync.strftime("%d/%m/%Y, %H:%M:%S.%f"),
                    "cabinet_L1": current_sensor_1, #if current_sensor_1 >0.38 else 0,
                    "warning_current_sensor_1": self.Warning_Cabinet_L1_Asymetrii,
                    "cabinet_L2": current_sensor_2, #if current_sensor_2 >0.38 else 0,
                    "warning_current_sensor_2": self.Warning_Cabinet_L2_Asymetrii,
                    "cabinet_L3": current_sensor_3, #if current_sensor_3 >0.38 else 0,
                    "warning_current_sensor_3": self.Warning_Cabinet_L3_Asymetrii,
                    "motor_L1": current_sensor_4, #if current_sensor_4 >0.38 else 0,
                    "warning_current_sensor_4": self.Warning_Motor_L1_Asymetrii,
                    "motor_L2": current_sensor_5, #if current_sensor_5 >0.38 else 0,
                    "warning_current_sensor_5": self.Warning_Motor_L2_Asymetrii,
                    "motor_L3": current_sensor_6, #if current_sensor_6 >0.38 else 0,
                    "warning_current_sensor_6": self.Warning_Motor_L3_Asymetrii,
                    "temperature_sensor_1": temperature_sensor_1,
                    "warning_temperature_1": self.Warning_Temperature_T1,
                    "temperature_sensor_2": temperature_sensor_2,
                    "warning_temperature_2": self.Warning_Temperature_T2,
                    "input_1": ((inputs_output & 1) == 0),
                    "warning_input_1": self.Warning_Input_1,
                    "input_2": ((inputs_output & 2) == 0),
                    "warning_input_2": self.Warning_Input_2,
                    "input_3": ((inputs_output & 4) == 0),
                    "warning_input_3": self.Warning_Input_3,
                    "output_1": not((inputs_output & 8) == 0),
                    "output_2": not((inputs_output & 16) == 0),
                    "output_3": not((inputs_output & 32) == 0), 
                    "kW": self.kW, 
                    "cabinet_amperage": self.Cabinet_Amperage, 
                    "motor_amperage": self.Motor_Amperage, 
                    "day_kWh": self.last_value,
                    "average_kW_of_day": self.average_kW,
                    "biggest_kW_of_day": self.biggest_kW ,
                    "cabinet_asymetrii_L1": self.cabinet_asymetry_percent_list[0], 
                    "cabinet_asymetrii_L2": self.cabinet_asymetry_percent_list[1], 
                    "cabinet_asymetrii_L3": self.cabinet_asymetry_percent_list[2], 
                    "motor_asymetrii_L1": self.motor_asymetry_percent_list[0], 
                    "motor_asymetrii_L2": self.motor_asymetry_percent_list[1], 
                    "motor_asymetrii_L3": self.motor_asymetry_percent_list[2], 

                    }
                
                try:
                    entities = (self.lastsync.strftime("%d/%m/%Y, %H:%M:%S.%f"), 
                receivedData['cabinet_L1'],
                receivedData['warning_current_sensor_1'],
                receivedData['cabinet_L2'],
                receivedData['warning_current_sensor_2'],
                receivedData['cabinet_L3'],
                receivedData['warning_current_sensor_3'],
                receivedData['motor_L1'],
                receivedData['warning_current_sensor_4'],
                receivedData['motor_L2'],
                receivedData['warning_current_sensor_5'],
                receivedData['motor_L3'],
                receivedData['warning_current_sensor_6'],
                receivedData['temperature_sensor_1'],
                receivedData['warning_temperature_1'], 
                receivedData['temperature_sensor_2'],      
                receivedData['warning_temperature_2'], 
                receivedData['input_1'], 
                receivedData['warning_input_1'], 
                receivedData['input_2'], 
                receivedData['warning_input_2'], 
                receivedData['input_3'], 
                receivedData['warning_input_3'],  
                receivedData['output_1'],  
                receivedData['output_2'],           
                receivedData['output_3'],      
                receivedData['kW'], 
                receivedData['cabinet_amperage'], 
                receivedData['motor_amperage'], 
                receivedData['day_kWh'],
                receivedData['biggest_kW_of_day'],
                receivedData['average_kW_of_day'],
                receivedData['cabinet_asymetrii_L1'], 
                receivedData['cabinet_asymetrii_L2'], 
                receivedData['cabinet_asymetrii_L3'],  
                receivedData['motor_asymetrii_L1'],  
                receivedData['motor_asymetrii_L2'],    
                receivedData['motor_asymetrii_L3'],          
                
               )
                    
                    print('przeproeporeore')
                    try:
                        self.conn.execute('''INSERT INTO data_center(
                                          update_time, 
                                  cabinet_L1, 
                                  warning_current_sensor_1 , 
                                  cabinet_L2 , 
                                  warning_current_sensor_2 , 
                                  cabinet_L3 , 
                                  warning_current_sensor_3 , 
                                  motor_L1 , 
                                  warning_current_sensor_4 , 
                                  motor_L2 , 
                                  warning_current_sensor_5 , 
                                  motor_L3 , 
                                  warning_current_sensor_6,
                                  temperature_sensor_1 , 
                                  warning_temperature_1 ,
                                  temperature_sensor_2 , 
                                  warning_temperature_2 ,
                                  input_1 , 
                                  warning_input_1 ,
                                  input_2 , 
                                  warning_input_2 ,
                                  input_3 , 
                                  warning_input_3 ,
                                  output_1 , 
                                  output_2 , 
                                  output_3 , 
                                  kW , 
                                  cabinet_amperage , 
                                  motor_amperage , 
                                  day_kWh ,
                                  biggest_kWh_of_day ,
                                  average_kWh_if_day ,
                                  cabinet_asymetrii_L1 ,
                                  cabinet_asymetrii_L2 , 
                                  cabinet_asymetrii_L3 , 
                                  motor_asymetrii_L1 , 
                                  motor_asymetrii_L2 , 
                                  motor_asymetrii_L3 
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', entities)
                        self.conn.commit()
                        print("Record created successfully")
                    except Error as e:
                        print(e)
                except:
                    print('cos kurwa nie tak')
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


    def LCD(self):
        try:
            #! /usr/bin/env python

            import drivers
            from time import sleep
            from datetime import datetime
            from subprocess import check_output
            self.display = drivers.Lcd()
            self.IP = check_output(["hostname", "-I"], encoding="utf8").split()[0]
            self.HOSTANME = check_output("hostname", encoding="utf8")
            try:
                self.display.lcd_display_string(str(self.HOSTANME), 1)
                self.display.lcd_display_string(str(self.IP), 2)
                # Uncomment the following line to loop with 1 sec delay
                # sleep(1)
            except KeyboardInterrupt:
                # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
                print("Cleaning up!")
                self.display.lcd_clear()
        except:
            print("Nie można uruchomić LCD")
            pass

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
    #print('YYYYYYYYYYOOOOOOOOOOOOOLOOOOOOOOOOOOOOO3')
    PmB = PICmeBot_AmperWorks_SensorBoard(port)
    #print('YYYYYYYYYYOOOOOOOOOOOOOLOOOOOOOOOOOOOOO4' )
    workingInProgress = False

    while True:
        try:
            PmB.LCD()
            # Read new data and save to file
            #print('YYYYYYYYYYOOOOOOOOOOOOOLOOOOOOOOOOOOOOO1')
            newData = PmB.ReceiveNewData()
            #print('YYYYYYYYYYOOOOOOOOOOOOOLOOOOOOOOOOOOOOO2')
            jsonString = json.dumps(newData)

            f = open("PmB_SensorsValues.json", "w")
            f.write(jsonString)
            f.close()

            # Read new Relay values and send to the board
            #f = open("PmB_RelayValues.json", "r")
            #jsonString = f.read()
            #f.close()
            #readData = json.loads(jsonString)
            #PmB.SendNewOutputValues(readData['output_1'], readData['output_2'], readData['output_3'])

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
