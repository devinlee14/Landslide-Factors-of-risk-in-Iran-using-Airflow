-- CREATE DATABASE milestone;

BEGIN;

CREATE TABLE table_m3 (
    "ID" FLOAT,
    "LONG" FLOAT,
    "LAT" FLOAT,
    "SUB_Basin" VARCHAR(255),
    "Elevation" FLOAT,
    "AAP_(mm)" FLOAT,
    "RiverDIST_(m)" FLOAT,
    "FaultDIST_(m)" FLOAT,
    "Landuse_Type" VARCHAR(255),
    "Slop(Percent)" FLOAT,
    "Slop(Degrees)" FLOAT,
    "GEO_UNIT" VARCHAR(255),
    "DES_GEOUNI" TEXT,
    "Climate_Type" VARCHAR(255),
    "DES_ClimateType" TEXT
);

COMMIT;

-- Import the csv file into the table
COPY table_m3
FROM '/files/Landslide_Factors_IRAN.csv'
DELIMITER ',' 
CSV HEADER;