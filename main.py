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
Kafka_Consumer = KafkaConsumer('Payload', bootstrap_servers=f"{APP_Settings.POSTOFFICE_KAFKA_HOSTNAME}:{APP_Settings.POSTOFFICE_KAFKA_PORT}", group_id="Data_Consumer", auto_offset_reset='earliest', enable_auto_commit=False)

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
			Kafka_Message = Schema.IoT_Data_Pack_Payload(**json.loads(Message.value.decode()))

			# Handle Headers
			class Headers:
				Command = Message.headers[0][1].decode('ASCII')
				Device_ID = Message.headers[1][1].decode('ASCII')
				Device_Time = Message.headers[2][1].decode('ASCII')
				Device_IP = Message.headers[3][1].decode('ASCII')
				Size = Message.headers[4][1].decode('ASCII')
				Buffer_ID = int(Message.headers[5][1].decode('ASCII'))

			# Print LOG
			Service_Logger.debug("--------------------------------------------------------------------------------")
			Service_Logger.debug(f"Command     : '{Headers.Command}'")
			Service_Logger.debug(f"Device ID   : '{Headers.Device_ID}'")
			Service_Logger.debug(f"Client IP   : '{Headers.Device_IP}'")
			Service_Logger.debug(f"Device Time : '{Headers.Device_Time}'")
			Service_Logger.debug(f"Packet Size : '{Headers.Size}'")
			Service_Logger.debug("--------------------------------------------------------------------------------")

			# ------------------------------------------



			print(Kafka_Message)




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
