from sqlalchemy import Column, Integer, String, FLOAT, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .Database import Base

# Incoming Buffer Database Model
class Incoming_Buffer(Base):

	# Define Buffer Database
	__tablename__ = "Incoming_Buffer"

	# Define Colomns
	Buffer_ID = Column(Integer, primary_key=True, nullable=False)
	Buffer_Created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
	Buffer_Device_ID = Column(String, nullable=True)
	Buffer_Command = Column(String, nullable=True)
	Buffer_Client_IP = Column(String, nullable=True)
	Buffer_Data = Column(String, nullable=True)
	Parse_Device = Column(Boolean, default=False)
	Parse_Payload = Column(Boolean, default=False)

# Device IoT Module Table Model
class Module(Base):

	# Define Table Name
	__tablename__ = "Module"

	# Define Colomns
	Module_ID = Column(Integer, primary_key=True, nullable=False)
	Module_Create_Time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
	Device_ID = Column(String, nullable=False)
	Device_Development = Column(Boolean, default=False)
	Module_Name = Column(String, nullable=True)
	Last_Online_Time = Column(TIMESTAMP(timezone=True), nullable=True)
	Data_Count = Column(Integer, nullable=False)

# Device Version Table Model
class Version(Base):

	# Define Table Name
	__tablename__ = "Version"

	# Define Colomns
	Version_ID = Column(Integer, primary_key=True, nullable=False)
	Device_ID = Column(String, nullable=False)
	Hardware_Version = Column(String, nullable=False)
	Firmware_Version = Column(String, nullable=False)
	Update_Time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# Device IMU Table Model
class IMU(Base):

	# Define Table Name
	__tablename__ = "IMU"

	# Define Colomns
	IMU_ID = Column(Integer, primary_key=True, nullable=False)
	Update_Time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
	Device_ID = Column(String, nullable=False)
	Temperature = Column(FLOAT, nullable=True)
	Humidity = Column(FLOAT, nullable=True)

# Module Type Table Model
class Module_Type(Base):

	# Define Table Name
	__tablename__ = "Module_Type"

	# Define Colomns
	Module_Type_ID = Column(Integer, primary_key=True, nullable=False)
	Module_Type_Name = Column(String, nullable=False)

# Manufacturer Table Model
class Manufacturer(Base):

	# Define Table Name
	__tablename__ = "Manufacturer"

	# Define Colomns
	Manufacturer_ID = Column(Integer, primary_key=True, nullable=False)
	Manufacturer_Name = Column(String, nullable=False)

# Model Table Model
class Model(Base):

	# Define Table Name
	__tablename__ = "Model"

	# Define Colomns
	Model_ID = Column(Integer, primary_key=True, nullable=False)
	Model_Name = Column(String, nullable=False)

# IoT Module Table Model
class IoT_Module(Base):

	# Define Table Name
	__tablename__ = "IoT_Module"

	# Define Colomns
	Module_ID = Column(Integer, primary_key=True, nullable=False)
	Module_Type = Column(Integer, nullable=False)
	Module_Firmware = Column(String, nullable=True)
	Module_IMEI = Column(String, nullable=True)
	Module_Serial = Column(String, nullable=True)
	Manufacturer_ID = Column(Integer, nullable=False)
	Model_ID = Column(Integer, nullable=False)
	Create_Time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# Location Table Model
class Location(Base):

	# Define Table Name
	__tablename__ = "Location"

	# Define Colomns
	Location_ID = Column(Integer, primary_key=True, nullable=False)
	Device_ID = Column(String, nullable=False)
	LAC = Column(String, nullable=False)
	Cell_ID = Column(String, nullable=False)
	Time_Stamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# Operator Table Model
class Operator(Base):

	# Define Table Name
	__tablename__ = "Operator"

	# Define Colomns
	Operator_ID = Column(Integer, primary_key=True, nullable=False)
	Operator_Name = Column(String, nullable=False)

# SIM Table Model
class SIM(Base):

	# Define Table Name
	__tablename__ = "SIM"

	# Define Colomns
	SIM_ID = Column(Integer, primary_key=True, nullable=False)
	Device_ID = Column(String, nullable=False)
	ICCID = Column(String, nullable=False)
	Operator_ID = Column(Integer, nullable=False)
	Create_Time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# Connection Table Model
class Connection(Base):

	# Define Table Name
	__tablename__ = "Connection"

	# Define Colomns
	Connection_ID = Column(Integer, primary_key=True, nullable=False)
	Device_ID = Column(String, nullable=False)
	SIM_ID = Column(Integer, nullable=False)
	RSSI = Column(Integer, nullable=True)
	Device_IP = Column(String, nullable=True)
	Connection_Time = Column(Integer, nullable=True)
	Data_Size = Column(Integer, nullable=True)
	Time_Stamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# IoT Table Model
class IoT(Base):

	# Define Table Name
	__tablename__ = "IoT"

	# Define Colomns
	IoT_ID = Column(Integer, primary_key=True, nullable=False)
	Module_ID = Column(Integer, nullable=False)
	Device_ID = Column(String, nullable=False)
	Active = Column(Boolean, default=False)

# Battery Table Model
class Battery(Base):

	# Define Table Name
	__tablename__ = "Battery"

	# Define Colomns
	Battery_ID = Column(Integer, primary_key=True, nullable=False)
	Device_ID = Column(String, nullable=False)
	IV = Column(FLOAT, nullable=False)
	AC = Column(FLOAT, nullable=False)
	SOC = Column(FLOAT, nullable=False)
	Charge = Column(Integer, nullable=False)
	T = Column(FLOAT, nullable=True)
	FB = Column(Integer, nullable=True)
	IB = Column(Integer, nullable=True)
	Update_Time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
