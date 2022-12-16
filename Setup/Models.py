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

# Measurement Type Database Model
class Measurement_Type(Base):

	# Define Database Name
	__tablename__ = "Measurement_Type"

	# Define Colomns
	Measurement_Type_ID = Column(Integer, primary_key=True, nullable=False)
	Measurement_Pack_Name = Column(String, nullable=False)
	Measurement_Name = Column(String, nullable=False)
	Measurement_Unit = Column(String, nullable=True)

# Measurement Stat Database Model
class Measurement_Stat(Base):

	# Define Database Name
	__tablename__ = "Measurement_Stat"

	# Define Colomns
	Stats_ID = Column(Integer, primary_key=True, nullable=False)
	Min = Column(FLOAT, nullable=True)
	Max = Column(FLOAT, nullable=True)
	Average = Column(FLOAT, nullable=True)
	Slope = Column(FLOAT, nullable=True)
	Offset = Column(FLOAT, nullable=True)
	R2 = Column(FLOAT, nullable=True)
	DataCount = Column(Integer, nullable=True)

# Measurement Database Model
class Measurement(Base):

	# Define Database Name
	__tablename__ = "Measurement"

	# Define Colomns
	Measurement_ID = Column(Integer, primary_key=True, nullable=False)
	Data_ID = Column(Integer, nullable=False)
	Device_ID = Column(String, nullable=False)
	Measurement = Column(FLOAT, nullable=False)
	Stats_ID = Column(Integer, nullable=True)
	Measurement_Type_ID = Column(Integer, nullable=False)

# Command Database Model
class Command(Base):

	# Define Database Name
	__tablename__ = "Command"

	# Define Colomns
	Command_ID = Column(Integer, primary_key=True, nullable=False)
	Command = Column(String, nullable=False)
	Device_Type = Column(Integer, nullable=False)

# Data Stream Database Model
class Data_Stream(Base):

	# Define Database Name
	__tablename__ = "Data_Stream"

	# Define Colomns
	Stream_ID = Column(Integer, primary_key=True, nullable=False)
	Device_ID = Column(String, nullable=False)
	Update_Time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
	Measurement_Time = Column(TIMESTAMP(timezone=True), nullable=False)
	Command_ID = Column(Integer, nullable=False)
