import json
import time
from datetime import datetime
import pandas as pd


dtypes = {'data1':str, 'data2':str, 
          'cabinet_L1':float, 'cabinet_L2':float, 'cabinet_L3':float, 
          'motor_L1':float, 'motor_L2':float, 'motor_L3':float, 
          'temp_1':float, 'temp_2':float, 
          'input_1':bool, 'input_2':bool, 'input_3':bool, 
          'output_1': bool, 'output_2':bool, 'output_3': bool, 
          'kWh':float, 'OnOff': int}
columns = ['data1', 'data2',  'cabinet_L1', 'cabinet_L2', 'cabinet_L3', 'motor_L1', 'motor_L2', 'motor_L3','temp_1', 'temp_2', 'input_1', 'input_2', 'input_3', 'output_1', 'output_2', 'output_3', 'kWh', 'OnOff']


thresholds ={
    'temp': -40,
    'asymetry': 80,
}
__sensors_path = "PmB_SensorsValues.json"
__relay_path = "PmB_RelayValues.json"
__plot_path = "fullData.csv"


class DataCenter:
    def __init__(self):

        # inicjacja tabeli danych, wartosci granicznych dla bledow
        self.readData = None
        self.alarm=None
        self.thresholds = {
            'temp' : 42.0,
            'asymetri' : 80.0,
            'input' : True
        }
        self.emergency_thresholds = []
        self.dtypes = {'data1':str, 'data2':str, 
          'cabinet_L1':float, 'cabinet_L2':float, 'cabinet_L3':float, 
          'motor_L1':float, 'motor_L2':float, 'motor_L3':float, 
          'temp_1':float, 'temp_2':float, 
          'input_1':bool, 'input_2':bool, 'input_3':bool, 
          'output_1': bool, 'output_2':bool, 'output_3': bool, 
          'kWh':float, 'OnOff': int}
        self.columns = ['data1', 'data2',  'cabinet_L1', 'cabinet_L2', 'cabinet_L3', 'motor_L1', 'motor_L2', 'motor_L3','temp_1', 'temp_2', 'input_1', 'input_2', 'input_3', 'output_1', 'output_2', 'output_3', 'kWh', 'OnOff']


    def load_data_from_json(self):
        
        # Ladowanie danych do zmiennej readData
        try:
            with open("PmB_SensorsValues.json", "r") as json_file:
                self.readData = json.load(json_file)
        except:
            print("Plik PmB_SensorsValues.json nie został znaleziony.")
            pass

    def load_data_to_plot(self):
        try:
            self.SensValues = pd.read_csv("fullData.csv",delimiter="\s+", names=columns, dtype=dtypes, engine='python')        
            self.last_10_values = self.SensValues.tail(3600)
            

            # Zapisz do pliku CSV o nazwie 'plot_data.csv'
            self.last_10_values.to_csv('plot_data.csv', sep='\t', header=False, index=False)
        except:
            print('Couldnt save plot_data.csv')
            pass

    def amperage_asymetries(self):
        try:
            # Wyznaczanie asymetrii silnika
            self.average_motor_amperage = (self.readData['current_sensor_4'] + self.readData['current_sensor_5'] + self.readData['current_sensor_6'])/ 3
            self.max_motor_bufor = [self.average_motor_amperage - self.readData['current_sensor_4'], self.average_motor_amperage - self.readData['current_sensor_5'], self.average_motor_amperage - self.readData['current_sensor_6']] 
            self.biggest_motor_deviation = max(self.max_motor_bufor)
            try:
                self.motor_asymetry_percent_list = [self.biggest_motor_deviation/self.readData['current_sensor_4']*100, self.biggest_motor_deviation/self.readData['current_sensor_5']*100, self.biggest_motor_deviation/self.readData['current_sensor_6']*100]
            except:
                self.motor_asymetry_percent_list = [0, 0, 0]
            # Wyznaczanie asymetrii szafy
            self.average_cabinet_amperage = (self.readData['current_sensor_1'] + self.readData['current_sensor_2'] + self.readData['current_sensor_3'])/ 3
            self.max_cabinet_bufor = [self.average_cabinet_amperage - self.readData['current_sensor_1'], self.average_cabinet_amperage - self.readData['current_sensor_2'], self.average_cabinet_amperage - self.readData['current_sensor_3']] 
            self.biggest_cabinet_deviation = max(self.max_cabinet_bufor)
            try:
                self.cabinet_asymetry_percent_list = [self.biggest_cabinet_deviation/self.readData['current_sensor_1']*100, self.biggest_cabinet_deviation/self.readData['current_sensor_2']*100, self.biggest_cabinet_deviation/self.readData['current_sensor_3']*100]
            except:
                self.cabinet_asymetry_percent_list = [0, 0, 0]        
        except:
            print("Some error in asymetry calculation")  

    def emergency_values(self):
        
        # wyznaczanie czy ktoras z wartosci jest emergency
        try:
            self.Warning_Motor_L1_Asymetrii = True if self.motor_asymetry_percent_list[0] > self.thresholds['asymetri'] else False
            self.Warning_Motor_L2_Asymetrii = True if self.motor_asymetry_percent_list[1] > self.thresholds['asymetri'] else False
            self.Warning_Motor_L3_Asymetrii = True if self.motor_asymetry_percent_list[2] > self.thresholds['asymetri'] else False
            self.Warning_Cabinet_L1_Asymetrii = True if self.cabinet_asymetry_percent_list[0] > self.thresholds['asymetri'] else False
            self.Warning_Cabinet_L2_Asymetrii = True if self.cabinet_asymetry_percent_list[1] > self.thresholds['asymetri'] else False
            self.Warning_Cabinet_L3_Asymetrii = True if self.cabinet_asymetry_percent_list[2] > self.thresholds['asymetri'] else False
            self.Warning_Temperature_T1 = True if self.readData["temperature_sensor_1"] > self.thresholds['temp'] else False
            self.Warning_Temperature_T2 = True if self.readData["temperature_sensor_2"] > self.thresholds['temp'] else False
            self.Warning_Input_1 = True if self.readData["input_1"] == self.thresholds['input'] else False
            self.Warning_Input_2 = True if self.readData["input_2"] == self.thresholds['input'] else False
            self.Warning_Input_3 = True if self.readData["input_3"] == self.thresholds['input'] else False
            
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
            # zapis wartosci przekaznikow do plytki
            if self.alarm == True:
                self.relays = {"update time": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                "output_1": True,
                "output_2": True,
                "output_3": True
                }
                with open("PmB_RelayValues.json", 'w') as f:
                    json.dump(self.relays, f)

            else:
                self.relays = {"update time": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                "output_1": False,
                "output_2": False,
                "output_3": False
                }
                with open("PmB_RelayValues.json", 'w') as f:
                    json.dump(self.relays, f)            
        except:
            print("Couldn't write to PmB_RelasValues.json couse some error")


    def emergency_information_csv(self):
        # Zapis emergency alarm do pliku
        self.emergency_information = {
                '0' : 'Asymetria fazy L1 suwaka jest wieksza niz 80%!',
                '1' : 'Asymetria fazy L2 suwaka jest wieksza niz 80%!',
                '2' : 'Asymetria fazy L3 suwaka jest wieksza niz 80%!',
                '3' : 'Asymetria fazy L1 szafy sterowniczej jest wieksza niz 80%!',
                '4' : 'Asymetria fazy L2 szafy sterowniczej jest wieksza niz 80%!',
                '5' : 'Asymetria fazy L3 szafy sterowniczej jest wieksza niz 80%!',
                '6' : 'Temperatura czujnika 1 przekracza dozwolony limit!',
                '7' : 'Temperatura czujnika 2 przekracza dozwolony limit!',
                '8' : 'Wejscie 1 jest aktywne!',
                '9' : 'Wejscie 2 jest aktywne!',
                '10' : 'Wejscie 3 jest aktywne!',
        }

        # sprawdzanie czy ktoras z wartosci alarmowych jest True i ich zapis do tabeli
        self.bufor_emergency = []

        if self.alarm == True:
            for i in range(len(self.emergency_thresholds)):
                if self.emergency_thresholds[i] == True:
                    self.bufor_emergency.append(self.emergency_information[str(i)])
        else:
            self.bufor_emergency = []

        # zapis wartosci alarmowych do pliku
        if self.bufor_emergency is not None:
            f = open("emergency_information.csv", 'w')
            for i in range(len(self.bufor_emergency)):
                f.write(str(self.bufor_emergency[i]))
                f.write('   ')
            f.close()
        else:
            f = open("emergency_information.csv", 'w')
            f.write('   ')
            f.close()
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
    def indicators(self):
        self.indicators_data = {
                'date time' : self.readData['update time'],
                'motor L1' : self.readData['current_sensor_4'],
                'warning motor L1' : self.Warning_Motor_L1_Asymetrii,
                'motor L2' : self.readData['current_sensor_5'],
                'warning motor L2' : self.Warning_Motor_L2_Asymetrii,
                'motor L3' : self.readData['current_sensor_6'],
                'warning motor L3' : self.Warning_Motor_L3_Asymetrii,
                'cabinet L1' : self.readData['current_sensor_1'],
                'warning cabinet L1' : self.Warning_Cabinet_L1_Asymetrii,
                'cabinet L2' : self.readData['current_sensor_2'],
                'warning cabinet L2' : self.Warning_Cabinet_L2_Asymetrii,
                'cabinet L3' : self.readData['current_sensor_3'],
                'warning cabinet L3' : self.Warning_Cabinet_L3_Asymetrii,
                'temperature T1' : self.readData['temperature_sensor_1'],
                'warning temperature T1' : self.Warning_Temperature_T1,
                'temperature T2' : self.readData['temperature_sensor_2'],
                'warning temperature T2' : self.Warning_Temperature_T2,
                'input 1' : self.readData['input_1'],
                'warning input 1' : self.Warning_Input_1,
                'input 2' : self.readData['input_2'],
                'warning input 2' : self.Warning_Input_2,
                'input 3' : self.readData['input_3'], 
                'warning input 3' : self.Warning_Input_3,
                'kW' : (self.readData['current_sensor_1'] * 230 + self.readData['current_sensor_2'] * 230 + self.readData['current_sensor_3'] * 230 ) / 1000.0,
                }
        try: 
            with open("Indicator.json", 'w') as f:
                    json.dump(self.indicators_data, f)
        except:
            print("Couldn't write indicator data to Indicator.json")
        





# Utwórz instancję klasy DataCenter
data_center = DataCenter()

try:
    print("Program is running...")
    while True:
        # Wywołaj pierwszą metodę
        data_center.load_data_from_json()
        data_center.amperage_asymetries()
        data_center.emergency_values()
        data_center.emergency_information_csv()
        data_center.indicators()
        #data_center.load_data_to_plot()
        data_center.LCD()
        print('Done work..')
        time.sleep(0.5)    
except KeyboardInterrupt:
    print('interrupted!')

