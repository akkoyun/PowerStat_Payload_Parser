# Import Libraries
from datetime import datetime
from Setup import Database, Schema, Models
from Setup.Config import APP_Settings
from kafka import KafkaConsumer
import logging, coloredlogs
import numpy as np
import json

# Set Log Options
Service_Logger = logging.getLogger(__name__)
logging.basicConfig(filename='Log/Service.LOG', level=logging.INFO, format='%(asctime)s - %(message)s')

# Set Log Colored
coloredlogs.install(level='DEBUG', logger=Service_Logger)

# Create DB Models
Database.Base.metadata.create_all(bind=Database.DB_Engine)

# Kafka Consumer
Kafka_Consumer = KafkaConsumer('Device', bootstrap_servers=f"{APP_Settings.POSTOFFICE_KAFKA_HOSTNAME}:{APP_Settings.POSTOFFICE_KAFKA_PORT}", group_id="Data_Consumer", auto_offset_reset='earliest', enable_auto_commit=False)

# Boot Log Message
Service_Logger.info("API Log --> Service Started.")

# List Finder Function
def List_Finder(List, Variable):
	# Set Variable
	for X in np.array(list(List.__dict__.items())):
		if X[0] == Variable:
			return X[1]


# Parser Function
def Device_Parser():

	try:

		for Message in Kafka_Consumer:

			# handle Message.
			Kafka_Message = Schema.IoT_Data_Pack_Device(**json.loads(Message.value.decode()))

			# Handle Headers
			class Headers:
				Command = Message.headers[0][1].decode('ASCII')
				Device_ID = Message.headers[1][1].decode('ASCII')
				Device_Time = Message.headers[2][1].decode('ASCII')
				Device_IP = Message.headers[3][1].decode('ASCII')
				Size = Message.headers[4][1].decode('ASCII')
				Buffer_ID = int(Message.headers[5][1].decode('ASCII'))

			# Declare Variables
			class Variables:
				Module_ID = 0		# Module ID 
				IoT_Module_ID = 0	# GSM Module ID
				SIM_ID = 0			# SIM ID
				IoT_ID = 0			# IoT Device ID
				Location_ID = 0		# Location ID

			# Print LOG
			Service_Logger.debug("--------------------------------------------------------------------------------")
			Service_Logger.debug(f"Command     : '{Headers.Command}'")
			Service_Logger.debug(f"Device ID   : '{Headers.Device_ID}'")
			Service_Logger.debug(f"Client IP   : '{Headers.Device_IP}'")
			Service_Logger.debug(f"Device Time : '{Headers.Device_Time}'")
			Service_Logger.debug(f"Packet Size : '{Headers.Size}'")
			Service_Logger.debug("--------------------------------------------------------------------------------")

			# ------------------------------------------

			# Define DB
			DB_Module = Database.SessionLocal()

			# Database Query
			Query_Module = DB_Module.query(Models.Module).filter(Models.Module.Device_ID.like(Headers.Device_ID)).first()

			# Handle Record
			if not Query_Module:

				# Create Add Record Command
				New_Module = Models.Module(
					Device_ID = Headers.Device_ID,
					Last_Online_Time = datetime.now(),
					Data_Count = 1)

				# Add and Refresh DataBase
				DB_Module.add(New_Module)
				DB_Module.commit()
				DB_Module.refresh(New_Module)

				# Set Variable
				Variables.Module_ID = New_Module.Module_ID

				# Log
				Service_Logger.debug(f"New module detected, recording... [{New_Module.Module_ID}]")

			else:

				# Set Variable
				Variables.Module_ID = List_Finder(Query_Module, "Module_ID")

				# Update Online Time
				setattr(Query_Module, 'Last_Online_Time', datetime.now())
				setattr(Query_Module, 'Data_Count', (Query_Module.Data_Count + 1))
				DB_Module.commit()

				# LOG
				Service_Logger.warning(f"Module allready recorded [{Variables.Module_ID}], bypassing...")

			# Close Database
			DB_Module.close()

			# ------------------------------------------

			# Parse Version
			if Kafka_Message.Info.Firmware != None and Kafka_Message.Info.Hardware != None:

				# Define DB
				DB_Version = Database.SessionLocal()

				# Database Query
				Query_Version = DB_Version.query(Models.Version).filter(
					Models.Version.Device_ID.like(Headers.Device_ID),
					Models.Version.Firmware_Version.like(Kafka_Message.Info.Firmware),
					Models.Version.Hardware_Version.like(Kafka_Message.Info.Hardware)).first()

				# Handle Record
				if not Query_Version:

					# Create Add Record Command
					New_Version = Models.Version(
						Device_ID = Headers.Device_ID, 
						Hardware_Version = Kafka_Message.Info.Hardware,
						Firmware_Version = Kafka_Message.Info.Firmware)

					# Add and Refresh DataBase
					DB_Version.add(New_Version)
					DB_Version.commit()
					DB_Version.refresh(New_Version)

					# Log 
					Service_Logger.debug(f"New version detected, recording... [{New_Version.Version_ID}]")

				else:

					# LOG
					Service_Logger.warning("Version allready recorded, bypassing...")

				# Close Database
				DB_Version.close()

			else:

				# LOG
				Service_Logger.warning("There is no version info, bypassing...")

			# ------------------------------------------

			# Parse IMU Data
			if Kafka_Message.Info.Temperature is not None and Kafka_Message.Info.Humidity is not None:

				# Define DB
				DB_IMU = Database.SessionLocal()

				# Create Add Record Command
				New_IMU = Models.IMU(
					Device_ID = Headers.Device_ID,
					Temperature = Kafka_Message.Info.Temperature,
					Humidity = Kafka_Message.Info.Humidity)

				# Add and Refresh DataBase
				DB_IMU.add(New_IMU)
				DB_IMU.commit()
				DB_IMU.refresh(New_IMU)

				# Log 
				Service_Logger.debug(f"New IMU data detected [{round(Kafka_Message.Info.Temperature, 2)} C / {round(Kafka_Message.Info.Humidity, 2)} %], recording... [{New_IMU.IMU_ID}]")

				# Close Database
				DB_IMU.close()

			else:

				# LOG
				Service_Logger.warning("There is no IMU data, bypassing...")

			# ------------------------------------------

			# Parse IoT Module
			if Kafka_Message.IoT.GSM.Module is not None:

				# Define DB
				DB_IoT_Module = Database.SessionLocal()

				# Database Query
				Query_IoT_Module = DB_IoT_Module.query(Models.IoT_Module).filter(
					Models.IoT_Module.Module_Firmware.like(Kafka_Message.IoT.GSM.Module.Firmware),
					Models.IoT_Module.Module_IMEI.like(Kafka_Message.IoT.GSM.Module.IMEI),
					Models.IoT_Module.Module_Serial.like(Kafka_Message.IoT.GSM.Module.Serial),
					Models.IoT_Module.Manufacturer_ID == Kafka_Message.IoT.GSM.Module.Manufacturer,
					Models.IoT_Module.Model_ID == Kafka_Message.IoT.GSM.Module.Model).first()

				# Handle Record
				if not Query_IoT_Module:

					# Create Add Record Command
					New_IoT_Module = Models.IoT_Module(
						Module_Type = 1,
						Module_Firmware = Kafka_Message.IoT.GSM.Module.Firmware,
						Module_IMEI = Kafka_Message.IoT.GSM.Module.IMEI,
						Module_Serial = Kafka_Message.IoT.GSM.Module.Serial,
						Manufacturer_ID = Kafka_Message.IoT.GSM.Module.Manufacturer,
						Model_ID = Kafka_Message.IoT.GSM.Module.Model)

					# Add and Refresh DataBase
					DB_IoT_Module.add(New_IoT_Module)
					DB_IoT_Module.commit()
					DB_IoT_Module.refresh(New_IoT_Module)

					# Set Variable
					Variables.IoT_Module_ID = New_IoT_Module.Module_ID

					# Log
					Service_Logger.debug(f"New IoT module detected, recording... [{New_IoT_Module.Module_ID}]")

				else:

					# Set Variable
					Variables.IoT_Module_ID = List_Finder(Query_IoT_Module, "Module_ID")

					# LOG
					Service_Logger.warning(f"IoT module allready recorded [{Variables.IoT_Module_ID}], bypassing...")

				# Close Database
				DB_IoT_Module.close()

			else:

				# LOG
				Service_Logger.warning("There is no IoT module data, bypassing...")

			# ------------------------------------------

			# Parse IoT Location
			if Kafka_Message.IoT.GSM.Operator.LAC is not None and Kafka_Message.IoT.GSM.Operator.Cell_ID is not None:

				# Define DB
				DB_Location = Database.SessionLocal()

				# Database Query
				Query_Location = DB_Location.query(Models.Location).filter(
					Models.Location.Device_ID.like(Headers.Device_ID)).order_by(Models.Location.Time_Stamp.desc()).first()

				# Handle Record
				if not Query_Location:

					# Create Add Record Command
					New_IoT_Location_Post = Models.Location(
						Device_ID = Headers.Device_ID,
						LAC = Kafka_Message.IoT.GSM.Operator.LAC,
						Cell_ID = Kafka_Message.IoT.GSM.Operator.Cell_ID)

					# Add and Refresh DataBase
					DB_Location.add(New_IoT_Location_Post)
					DB_Location.commit()
					DB_Location.refresh(New_IoT_Location_Post)

					# Log
					Service_Logger.debug(f"New location detected [{Kafka_Message.IoT.GSM.Operator.LAC} - {Kafka_Message.IoT.GSM.Operator.Cell_ID}], recording... [{New_IoT_Location_Post.Location_ID}]")

				else:

					# Set Variable
					Variables.Location_ID = List_Finder(Query_Location, "Location_ID")

					# Control for new location
					if List_Finder(Query_Location, "LAC") != Kafka_Message.IoT.GSM.Operator.LAC or List_Finder(Query_Location, "Cell_ID") != Kafka_Message.IoT.GSM.Operator.Cell_ID:

						# Create Add Record Command
						ReNew_IoT_Location_Post = Models.Location(
							Device_ID = Headers.Device_ID,
							LAC = Kafka_Message.IoT.GSM.Operator.LAC,
							Cell_ID = Kafka_Message.IoT.GSM.Operator.Cell_ID)

						# Add and Refresh DataBase
						DB_Location.add(ReNew_IoT_Location_Post)
						DB_Location.commit()
						DB_Location.refresh(ReNew_IoT_Location_Post)

						# LOG
						Service_Logger.debug(f"Location data updated [{Variables.Location_ID}]")

					else:

						# LOG
						Service_Logger.warning(f"Location data allready recorded [{Variables.Location_ID}], bypassing...")

				# Close Database
				DB_Location.close()

			else:

				# LOG
				Service_Logger.warning("There is no location data, bypassing...")

			# ------------------------------------------

			# Parse IoT SIM
			if Kafka_Message.IoT.GSM.Operator.ICCID is not None:

				# Define DB
				DB_SIM = Database.SessionLocal()

				# Database Query
				IoT_SIM_Query = DB_SIM.query(Models.SIM).filter(
					Models.SIM.ICCID.like(Kafka_Message.IoT.GSM.Operator.ICCID),
					Models.SIM.Operator_ID == Kafka_Message.IoT.GSM.Operator.Code).first()

				# Handle Record
				if not IoT_SIM_Query:

					# Create Add Record Command
					New_IoT_SIM_Post = Models.SIM(
						Device_ID = Headers.Device_ID,
						ICCID = Kafka_Message.IoT.GSM.Operator.ICCID,
						Operator_ID = Kafka_Message.IoT.GSM.Operator.Code)

					# Add and Refresh DataBase
					DB_SIM.add(New_IoT_SIM_Post)
					DB_SIM.commit()
					DB_SIM.refresh(New_IoT_SIM_Post)

					# Set Variable
					Variables.SIM_ID = New_IoT_SIM_Post.SIM_ID

					# Log
					Service_Logger.debug(f"New SIM detected, recording... [{New_IoT_SIM_Post.SIM_ID}]")

				else:

					# Set Variable
					Variables.SIM_ID = List_Finder(IoT_SIM_Query, "SIM_ID")

					# LOG
					Service_Logger.warning(f"SIM allready recorded [{Variables.SIM_ID}], bypassing...")

				# Close Database
				DB_SIM.close()

			else:

				# LOG
				Service_Logger.warning("There is no SIM data, bypassing...")

			# ------------------------------------------

			# Parse IoT Connection
			if Kafka_Message.IoT.GSM.Operator.RSSI is not None:

				# Define DB
				DB_Connection = Database.SessionLocal()

				# Create Add Record Command
				New_IoT_Connection_Post = Models.Connection(
					Device_ID = Headers.Device_ID,
					SIM_ID = Variables.SIM_ID,
					RSSI = Kafka_Message.IoT.GSM.Operator.RSSI,
					Device_IP = Headers.Device_IP,
					Connection_Time = Kafka_Message.IoT.GSM.Operator.ConnTime,
					Data_Size = Headers.Size)

				# Add and Refresh DataBase
				DB_Connection.add(New_IoT_Connection_Post)
				DB_Connection.commit()
				DB_Connection.refresh(New_IoT_Connection_Post)

				# Log 
				Service_Logger.debug(f"New connection data detected, recording... [{New_IoT_Connection_Post.Connection_ID}]")

				# Close Database
				DB_Connection.close()

			else:

				# Log 
				Service_Logger.warning("There is no connection data, bypassing...")

			# ------------------------------------------

			# Define DB
			DB_IoT = Database.SessionLocal()

			# Database Query
			IoT_Query = DB_IoT.query(Models.IoT).filter(
				Models.IoT.Device_ID.like(Headers.Device_ID),
				Models.IoT.Module_ID == Variables.Module_ID).first()

			# Handle Record
			if not IoT_Query:

				# Create Add Record Command
				New_IoT_Post = Models.IoT(
					Device_ID = Headers.Device_ID,
					Module_ID = Variables.Module_ID)

				# Add and Refresh DataBase
				DB_IoT.add(New_IoT_Post)
				DB_IoT.commit()
				DB_IoT.refresh(New_IoT_Post)

				# Set Variable
				Variables.IoT_ID = New_IoT_Post.IoT_ID

				# Log
				Service_Logger.debug(f"New Iot Device detected, recording... [{Variables.IoT_ID}]")

			else:

				# Set Variable
				Variables.IoT_ID = List_Finder(IoT_Query, "IoT_ID")

				# LOG
				Service_Logger.warning(f"IoT device allready recorded [{Variables.IoT_ID}], bypassing...")

			# Close Database
			DB_IoT.close()

			# ------------------------------------------

			# Parse Battery
			if Kafka_Message.Power.Battery is not None:

				# Define DB
				DB_Battery = Database.SessionLocal()

				# Create Add Record Command
				New_Battery_Post = Models.Battery(
					Device_ID = Headers.Device_ID,
					IV = Kafka_Message.Power.Battery.IV,
					AC = Kafka_Message.Power.Battery.AC,
					SOC = Kafka_Message.Power.Battery.SOC,
					Charge = Kafka_Message.Power.Battery.Charge,
					T = Kafka_Message.Power.Battery.T,
					FB = Kafka_Message.Power.Battery.FB,
					IB = Kafka_Message.Power.Battery.IB)

				# Add and Refresh DataBase
				DB_Battery.add(New_Battery_Post)
				DB_Battery.commit()
				DB_Battery.refresh(New_Battery_Post)

				# Log 
				Service_Logger.debug(f"New battery data detected, recording... [{New_Battery_Post.Battery_ID}]")

				# Close Database
				DB_Battery.close()

			else:

				# Log 
				Service_Logger.warning("There is no battery data, bypassing...")

			# ------------------------------------------

			# Define DB
			DB_Buffer = Database.SessionLocal()

			# Database Query
			Buffer_Query = DB_Buffer.query(Models.Incoming_Buffer).filter(Models.Incoming_Buffer.Buffer_ID == Headers.Buffer_ID).first()

			# Update Online Time
			setattr(Buffer_Query, 'Parse_Device', True)
			DB_Buffer.commit()

			# LOG
			Service_Logger.debug(f"Module raw table updated...")

			# Close Database
			DB_Buffer.close()

			# ------------------------------------------

			# Commit Message
			Kafka_Consumer.commit()

			# End LOG
			Service_Logger.debug("--------------------------------------------------------------------------------")
			print("")
			print("")


	finally:
		
		Service_Logger.fatal("Error Accured !!")

# Handle All Message in Topic
Device_Parser()
