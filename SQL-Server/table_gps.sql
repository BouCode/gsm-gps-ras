CREATE TABLE GPS_POSITION (
    ID_GPS_POSITION INT IDENTITY (1,1) PRIMARY KEY,
    LATITUD VARCHAR (50),
    LONGITUD VARCHAR (50),
    TIMESTAMP VARCHAR (20),
    ID_HARDWARE VARCHAR (20),
)

INSERT INTO GPS_POSITION (LATITUD, LONGITUD, TIMESTAMP, ID_HARDWARE) VALUES ('', '', '', '')

SELECT * FROM GPS_POSITION

