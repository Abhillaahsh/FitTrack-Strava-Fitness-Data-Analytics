# Python code to clean, process, and merge a subset of Bellabeat CSV files using SQLite with data validation and visualization support

import sqlite3
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to SQLite database
print("Connecting to SQLite database...")
conn = sqlite3.connect('bellabeat_fitness.db')
cursor = conn.cursor()
print("Connection established.")

# Subset of files used for this demonstration
csv_files = {
    'daily_activity_data': 'datafiles/dailyActivity_merged.csv',
    'sleep_data': 'datafiles/sleepDay_merged.csv',
    'heartrate_data': 'datafiles/heartrate_seconds_merged.csv',
    'weight_log_data': 'datafiles/weightLogInfo_merged.csv'
}

# Load and clean the selected CSV files
for table_name, path in csv_files.items():
    if os.path.exists(path):
        print(f"Loading: {path}")
        df = pd.read_csv(path)
        print(f"Initial shape of {table_name}: {df.shape}")
        df.columns = [col.strip().replace(' ', '_').replace('-', '_').lower() for col in df.columns]
        df.dropna(how='all', inplace=True)
        print(f"Post-cleaning shape of {table_name}: {df.shape}")
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Loaded and cleaned: {table_name}")
    else:
        print(f"Missing file: {path}")

# SQL script to clean and merge these key tables
cursor.executescript('''
DROP TABLE IF EXISTS daily_activity_cleaned;
CREATE TABLE daily_activity_cleaned AS
SELECT DISTINCT 
    id,
    DATE(activitydate) AS activity_date,
    totalsteps,
    totaldistance,
    calories,
    veryactiveminutes,
    fairlyactiveminutes,
    lightlyactiveminutes,
    sedentaryminutes
FROM daily_activity_data
WHERE totalsteps IS NOT NULL AND activitydate IS NOT NULL;

DROP TABLE IF EXISTS sleep_data_cleaned;
CREATE TABLE sleep_data_cleaned AS
SELECT DISTINCT 
    id,
    DATE(sleepday) AS sleep_date,
    totalsleeprecords,
    totalminutesasleep,
    totaltimeinbed
FROM sleep_data
WHERE totalminutesasleep IS NOT NULL AND totaltimeinbed IS NOT NULL;

DROP TABLE IF EXISTS heartrate_cleaned;
CREATE TABLE heartrate_cleaned AS
SELECT
    id,
    DATE(time) AS hr_date,
    TIME(time) AS hr_time,
    value AS heart_rate
FROM heartrate_data
WHERE value IS NOT NULL;

DROP TABLE IF EXISTS weight_log_cleaned;
CREATE TABLE weight_log_cleaned AS
SELECT
    id,
    DATE(date) AS weight_date,
    weightkg,
    weightpounds,
    fat,
    bmi,
    ismanualreport,
    logid
FROM weight_log_data
WHERE weightkg IS NOT NULL;

DROP TABLE IF EXISTS combined_daily_data;
CREATE TABLE combined_daily_data AS
SELECT
    da.id,
    da.activity_date,
    da.totalsteps,
    da.totaldistance,
    da.calories,
    da.veryactiveminutes,
    da.fairlyactiveminutes,
    da.lightlyactiveminutes,
    da.sedentaryminutes,
    sd.totalminutesasleep,
    sd.totaltimeinbed,
    CASE 
        WHEN sd.totaltimeinbed > 0 THEN ROUND(CAST(sd.totalminutesasleep AS FLOAT) / sd.totaltimeinbed * 100, 2)
        ELSE NULL
    END AS sleepefficiency,
    AVG(hr.heart_rate) AS avg_heart_rate,
    MAX(hr.heart_rate) AS max_heart_rate,
    MIN(hr.heart_rate) AS min_heart_rate,
    wl.weightkg,
    wl.bmi
FROM daily_activity_cleaned AS da
LEFT JOIN sleep_data_cleaned AS sd ON da.id = sd.id AND da.activity_date = sd.sleep_date
LEFT JOIN heartrate_cleaned AS hr ON da.id = hr.id AND da.activity_date = hr.hr_date
LEFT JOIN weight_log_cleaned AS wl ON da.id = wl.id AND da.activity_date = wl.weight_date
GROUP BY da.id, da.activity_date;
''')

print("Data cleaning, processing, and merging completed.")

# Load merged data for visualization
print("Reading merged data for visualization...")
df_combined = pd.read_sql_query("SELECT * FROM combined_daily_data", conn)

# Example visualization: Steps vs. Calories
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
if 'sleepefficiency' in df_combined.columns and not df_combined['sleepefficiency'].isnull().all():
    scatter = plt.scatter(df_combined['totalsteps'], df_combined['calories'], c=df_combined['sleepefficiency'], cmap='coolwarm')
    cbar = plt.colorbar(scatter)
    cbar.set_label('Sleep Efficiency')
else:
    plt.scatter(df_combined['totalsteps'], df_combined['calories'], color='gray')
    print("Sleep Efficiency data not available for coloring.")
plt.title("Total Steps vs Calories")
plt.xlabel("Total Steps")
plt.ylabel("Calories")
plt.tight_layout()
plt.show()

# Visualization of variation: Active minutes
plt.figure(figsize=(10, 6))
df_variations = df_combined[['veryactiveminutes', 'fairlyactiveminutes', 'lightlyactiveminutes', 'sedentaryminutes']]
df_variations.boxplot()
plt.title("Distribution of Activity Minutes by Type")
plt.ylabel("Minutes")
plt.tight_layout()
plt.show()

conn.commit()
conn.close()
print("Connection closed.")
