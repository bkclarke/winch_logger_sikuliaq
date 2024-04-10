import socket
import pandas as pd
import mysql.connector
from datetime import datetime

mydb=mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='67Giffordstreet!',
    database='winch_data'
)

cursor=mydb.cursor()

UDP_PORT=53128

sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("",UDP_PORT))

df1=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})
df2=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})
df7=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})


while True:
    data, addr = sock.recvfrom(1024) 
    data=str(data)
    data_comma=data.split(",")

    winch=data_comma[1]
    payout=data_comma[3]
    tension_motor_calculated=data_comma[4]
    speed=data_comma[5]

    tension_load_cell=data_comma[8]
    tension_load_cell=tension_load_cell[0:8]
    tension_load_cell=float(tension_load_cell)*2204.62

    if winch=="1":
        if len(df1)<10:
            dict=pd.DataFrame({"winch": [winch],"payout": [payout], "tension_motor_calculated": [tension_motor_calculated], "speed": [speed], "tension_load_cell":[tension_load_cell]})
            df1=pd.concat([df1, dict], ignore_index=True)
          
        else:
            date_time=datetime.now()
            
            winch_last=str(df1.winch[0])
            payout_max=int(round(float(df1['payout'].max())))
            payout_min=int(round(float(df1['payout'].min())))
            payout_diff=payout_max-payout_min
            tension_motor_calculated_max=int(round(float(df1['tension_motor_calculated'].max())))
            tension_motor_calculated_min=int(round(float(df1['tension_motor_calculated'].min())))
            tension_motor_calculated_diff=tension_motor_calculated_max-tension_motor_calculated_min
            speed_max=int(round(float(df1['speed'].max())))
            tension_load_cell_max=int(round(float(df1['tension_load_cell'].max())))
            tension_load_cell_min=int(round(float(df1['tension_load_cell'].min())))
            tension_load_cell_diff=tension_load_cell_max-tension_load_cell_min

            if payout_diff<1 or tension_load_cell_diff<20:
                print("no diff winch 1")
                df1=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})

            else:
                sql="INSERT INTO winch_1 (date_time, winch, payout, tension_motor_calculated, speed, tension_load_cell) VALUES (%s, %s, %s, %s,%s, %s)"
                val=(date_time, winch_last, payout_max, tension_motor_calculated_max, speed_max, tension_load_cell_max)
                print("inserting row into winch 1")
                cursor.execute(sql,val)
                mydb.commit()

                df1=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})

    elif winch=="2":
        if len(df2)<10:
            dict=pd.DataFrame({"winch": [winch],"payout": [payout], "tension_motor_calculated": [tension_motor_calculated], "speed": [speed], "tension_load_cell":[tension_load_cell]})
            df2=pd.concat([df2, dict], ignore_index=True)

        else:
            date_time=datetime.now()
            
            winch_last=str(df2.winch[0])
            payout_max=int(round(float(df2['payout'].max())))
            payout_min=int(round(float(df2['payout'].min())))
            payout_diff=payout_max-payout_min
            tension_motor_calculated_max=int(round(float(df2['tension_motor_calculated'].max())))
            tension_motor_calculated_min=int(round(float(df2['tension_motor_calculated'].min())))
            tension_motor_calculated_diff=tension_motor_calculated_max-tension_motor_calculated_min
            speed_max=int(round(float(df2['speed'].max())))
            tension_load_cell_max=int(round(float(df2['tension_load_cell'].max())))
            tension_load_cell_min=int(round(float(df2['tension_load_cell'].min())))
            tension_load_cell_diff=tension_load_cell_max-tension_load_cell_min

            
            if payout_diff<1 or tension_load_cell_diff<20:
                print("no diff winch 2")
                df2=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})

            else:
                sql="INSERT INTO winch_2 (date_time, winch, payout, tension_motor_calculated, speed, tension_load_cell) VALUES (%s, %s, %s, %s,%s, %s)"
                val=(date_time, winch_last, payout_max, tension_motor_calculated_max, speed_max, tension_load_cell_max)
                print("inserting row into winch 2")
                cursor.execute(sql,val)
                mydb.commit()
        
                df2=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})

    elif winch=="7":
        if len(df7)<10:
            dict=pd.DataFrame({"winch": [winch],"payout": [payout], "tension_motor_calculated": [tension_motor_calculated], "speed": [speed], "tension_load_cell":[tension_load_cell]})
            df7=pd.concat([df7, dict], ignore_index=True)

        else:
            date_time=datetime.now()
            
            winch_last=str(df7.winch[0])
            payout_max=int(round(float(df7['payout'].max())))
            payout_min=int(round(float(df7['payout'].min())))
            payout_diff=payout_max-payout_min
            tension_motor_calculated_max=int(round(float(df7['tension_motor_calculated'].max())))
            tension_motor_calculated_min=int(round(float(df7['tension_motor_calculated'].min())))
            tension_motor_calculated_diff=tension_motor_calculated_max-tension_motor_calculated_min
            speed_max=int(round(float(df7['speed'].max())))
            tension_load_cell_max=int(round(float(df7['tension_load_cell'].max())))
            tension_load_cell_min=int(round(float(df7['tension_load_cell'].min())))
            tension_load_cell_diff=tension_load_cell_max-tension_load_cell_min

            if payout_diff<1 or tension_load_cell_diff<50:
                print("no diff winch 7")
                df7=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})

            else:
                sql="INSERT INTO winch_7 (date_time, winch, payout, tension_motor_calculated, speed, tension_load_cell) VALUES (%s, %s, %s, %s,%s, %s)"
                val=(date_time, winch_last, payout_max, tension_motor_calculated_max, speed_max, tension_load_cell_max)
                print("inserting row into winch 7")
                cursor.execute(sql,val)
                mydb.commit()
        
                df7=pd.DataFrame({"winch": [],"payout": [], "tension_motor_calculated": [], "speed": [], "tension_load_cell": []})



    
