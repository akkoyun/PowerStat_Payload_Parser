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
Kafka_Consumer = KafkaConsumer('PowerStat.Payload', bootstrap_servers=f"{APP_Settings.POSTOFFICE_KAFKA_HOSTNAME}:{APP_Settings.POSTOFFICE_KAFKA_PORT}", group_id="Data_Consumer", auto_offset_reset='earliest', enable_auto_commit=False)

# Boot Log Message
Service_Logger.debug("Service Started.")

# List Finder Function
def List_Finder(List, Variable):
	# Set Variable
	for X in np.array(list(List.__dict__.items())):
		if X[0] == Variable:
			return X[1]

# Parser Function
def Payload_Parser():

	try:

		for Message in Kafka_Consumer:

			# handle Message.
			Kafka_Message = Schema.IoT_Data_Pack_Payload_PowerStat(**json.loads(Message.value.decode()))

			# Handle Headers
			class Headers:
				Command = Message.headers[0][1].decode('ASCII')
				Device_ID = Message.headers[1][1].decode('ASCII')
				Device_Time = Message.headers[2][1].decode('ASCII')
				Device_IP = Message.headers[3][1].decode('ASCII')
				Size = Message.headers[4][1].decode('ASCII')
				Buffer_ID = int(Message.headers[5][1].decode('ASCII'))

			# Function Variables
			class Variables:
				Command_ID = 0
				Stream_ID = 0

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
			DB_Connection = Database.SessionLocal()

			# ------------------------------------------

			# Database Query
			Query_Command = DB_Connection.query(Models.Command).filter(Models.Command.Command.like(Headers.Command)).first()

			# Handle Record
			if not Query_Command:

				# Create Add Record Command
				New_Command = Models.Command(
					Command = Headers.Command,
					Device_Type = 0)

				# Add and Refresh DataBase
				DB_Connection.add(New_Command)
				DB_Connection.commit()
				DB_Connection.refresh(New_Command)

				# Set Variable
				Variables.Command_ID = New_Command.Command_ID

			else:

				# Set Variable
				Variables.Command_ID = Query_Command.Command_ID

			# ------------------------------------------

			# Create Add Record Command
			New_Stream = Models.Data_Stream(
				Device_ID = Headers.Device_ID,
				Measurement_Time = Headers.Device_Time,
				Command_ID = Variables.Command_ID)

			# Add and Refresh DataBase
			DB_Connection.add(New_Stream)
			DB_Connection.commit()
			DB_Connection.refresh(New_Stream)

			# Get Stream ID
			Variables.Stream_ID = New_Stream.Stream_ID

			# ------------------------------------------

			# Handle DeviceStatus and FaultStatus
			if Kafka_Message.DeviceStatus is not None and Kafka_Message.FaultStatus is not None:

				# Database Query
				Query_Status = DB_Connection.query(Models.Status).filter(
					Models.Status.Device_ID.like(Headers.Device_ID)).order_by(Models.Status.Status_ID.desc()).first()

				# Handle Record
				if not Query_Status:

					# Create Add Record Command
					New_Status = Models.Status(
						Data_ID = Variables.Stream_ID,
						Device_ID = Headers.Device_ID,
						Device_Status = Kafka_Message.DeviceStatus,
						Fault_Status = Kafka_Message.FaultStatus)

					# Add and Refresh DataBase
					DB_Connection.add(New_Status)
					DB_Connection.commit()
					DB_Connection.refresh(New_Status)

					# Log
					Service_Logger.debug(f"New status detected [{Kafka_Message.DeviceStatus} - {Kafka_Message.FaultStatus}], recording... [{New_Status.Status_ID}]")

				else:
					print(Query_Status.DeviceStatus, " - ", Query_Status.FaultStatus)
					# Control for new location
					if Query_Status.DeviceStatus != Kafka_Message.DeviceStatus or Query_Status.FaultStatus != Kafka_Message.FaultStatus:

						# Create Add Record Command
						ReNew_Status = Models.Status(
							Data_ID = Variables.Stream_ID,
							Device_ID = Headers.Device_ID,
							Device_Status = Kafka_Message.DeviceStatus,
							Fault_Status = Kafka_Message.FaultStatus)

						# Add and Refresh DataBase
						DB_Connection.add(ReNew_Status)
						DB_Connection.commit()
						DB_Connection.refresh(ReNew_Status)

						# LOG
						Service_Logger.debug(f"Status data updated [{ReNew_Status.Status_ID}]")

					else:

						# LOG
						Service_Logger.warning(f"Status not changed, bypassing...")

			else:

				# LOG
				Service_Logger.warning("There is no status data, bypassing...")

			# Handle Pressure
			if Kafka_Message.Pressure is not None:

				# Define Measurement Type ID
				Type_ID_Pressure = 0

				# Database Query
				Query_Pressure = DB_Connection.query(Models.Measurement_Type).filter(Models.Measurement_Type.Measurement_Pack_Name.like('Pressure')).first()

				# Handle Record
				if not Query_Pressure:

					# Create Add Record Command
					New_Measurement_Type_Pressure = Models.Measurement_Type(
						Measurement_Pack_Name = 'Pressure',
						Measurement_Name = 'Pressure Measurement')

					# Add and Refresh DataBase
					DB_Connection.add(New_Measurement_Type_Pressure)
					DB_Connection.commit()
					DB_Connection.refresh(New_Measurement_Type_Pressure)

					# Set Variable
					Type_ID_FaultStatus = New_Measurement_Type_Pressure.Measurement_Type_ID

				else:

					# Set Variable
					Type_ID_Pressure = Query_Pressure.Measurement_Type_ID

				# Create Add Record Command
				New_Pressure = Models.Measurement(
					Data_ID = Variables.Stream_ID,
					Device_ID = Headers.Device_ID,
					Measurement_Type_ID = Type_ID_Pressure,
					Instant =Kafka_Message.Pressure.Inst,
					Min = Kafka_Message.Pressure.Min,
					Max = Kafka_Message.Pressure.Max,
					Average = Kafka_Message.Pressure.Avg,
					Slope = Kafka_Message.Pressure.Slope,
					Offset = Kafka_Message.Pressure.Offset,
					R2 = Kafka_Message.Pressure.R2,
					DataCount = Kafka_Message.Pressure.DataCount)

				# Add and Refresh DataBase
				DB_Connection.add(New_Pressure)
				DB_Connection.commit()
				DB_Connection.refresh(New_Pressure)

				# Print Log
				Service_Logger.debug(f"New measurement 'Pressure' recorded... ['{New_Pressure.Measurement_ID}']")

			else:

				# LOG
				Service_Logger.warning("There is no pressure data, bypassing...")











			# ------------------------------------------

			# Close Database
			DB_Connection.close()

			# Commit Message
			Kafka_Consumer.commit()

			# End LOG
			Service_Logger.debug("--------------------------------------------------------------------------------")
			print("")
			print("")


	finally:
		
		Service_Logger.fatal("Error Accured !!")

# Handle All Message in Topic
Payload_Parser()
