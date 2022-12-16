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
				Variables.Command_ID = New_Command.Module_ID

				# Log
				Service_Logger.debug(f"New command detected, recording... [{Variables.Command_ID}]")

			else:

				print("Command Found")







			# ------------------------------------------

			# Create Add Record Command
#			New_Stream = Models.Data_Stream(
#				Device_ID = Headers.Device_ID,
#				Measurement_Time = Headers.Device_Time,
#				Command_ID = Variables.Command_ID)

			# ------------------------------------------


			# Handle DeviceStatus
#			if Kafka_Message.DeviceStatus is not None:

				# Database Query
#				Query_DeviceStatus = DB_Connection.query(Models.Measurement_Type).filter(Models.Measurement_Type.Measurement_Pack_Name.like('DeviceStatus')).first()

				# Handle Record
#				if not Query_DeviceStatus:

#					print("ID not Found")

#				else:

					# Create Add Record Command
#					New_Module = Models.Measurement(




#						Device_ID = Headers.Device_ID,
#						Last_Online_Time = datetime.now(),
#						Data_Count = 1)

#					print("ID Found")









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
Payload_Parser()
