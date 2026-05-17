import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import os
loaded_csv= [
    'dailyActivity_merged.csv',
    'dailyCalories_merged.csv',
    'dailyIntensities_merged.csv',
    'dailySteps_merged.csv',
    'heartrate_seconds_merged.csv',
    'hourlyCalories_merged.csv',
    'hourlyIntensities_merged.csv',
    'hourlySteps_merged.csv',
    'minuteCaloriesNarrow_merged.csv',
    'minuteCaloriesWide_merged.csv',
    'minuteIntensitiesNarrow_merged.csv',
    'minuteIntensitiesWide_merged.csv',
    'minuteMETsNarrow_merged.csv',
    'minuteSleep_merged.csv',
    'minuteStepsNarrow_merged.csv',
    'minuteStepsWide_merged.csv',
    'sleepDay_merged.csv',
    'weightLogInfo_merged.csv'
]

datasets = r'/Users/abhillaahsh/Downloads/STRAVA FITNESS py/datafiles'
DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'

full_paths = [os.path.join(datasets, fname) for fname in loaded_csv]

# Dictionary to store DataFrames
dataframes = {}

print(" Loading datasets:")
print("=" * 60)

# Load each CSV file
for path in full_paths:
    try:
        # Get simple name for dictionary key
        name = os.path.basename(path).replace('.csv', '')
        
        # Read CSV file
        df = pd.read_csv(path)
        dataframes[name] = df
        
        # Print status
        print(f" {name: <35} | Rows: {df.shape[0]:<6} | Columns: {df.shape[1]}")
        
    except Exception as e:
        print(f" Error loading {os.path.basename(path)}: {str(e)}")

print("=" * 60)
print(f"Successfully loaded {len(dataframes)}/{len(full_paths)} datasets\n")


print("\nAll files loaded (if found)")
print("DataFrames available in 'all_dataframes' dictionary:")
for df_name, df in dataframes.items():
    print(f"- {df_name} (columns: {df.columns.tolist()})")

# Show available datasets
if dataframes:
    print(" Available datasets:")
    for name, df in dataframes.items():
        print(f"- {name}: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Show sample from first dataset
    first_key = list(dataframes.keys())[0]
    print(f"\n Sample from '{first_key}':")
    print(dataframes[first_key].head(3))
else:
    print(" No datasets loaded - check file paths")


    # data cleaning and preprocessing
   

print("Starting Data Cleaning and Preprocessing for loaded DataFrames")
for df_name, df in dataframes.items():
    print(f"\nProcessing DataFrame: '{df_name}")
    print(f"Original info for '{df_name}':")
    df.info(verbose=False, memory_usage="deep")
    print(df.head())
    if 'ActivityDate' in df.columns: 
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
        df['DayOfWeek'] = df['ActivityDate'].dt.day_name()
        df['ActivityMonth'] = df['ActivityDate'].dt.month_name()
        print(f"  - Converted 'ActivityDate' to datetime. Added 'DayOfWeek', 'ActivityMonth'.")
    elif 'SleepDay' in df.columns: 
        df['SleepDay'] = pd.to_datetime(df['SleepDay'], errors='coerce')
        df['DayOfWeek'] = df['SleepDay'].dt.day_name()
        print(f"  - Converted 'SleepDay' to datetime. Added 'DayOfWeek'.")
    elif 'ActivityHour' in df.columns: #'MM/DD/YYYY HH:MM:SS AM/PM'
        df['ActivityHour'] = pd.to_datetime(df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
        df['ActivityDay'] = df['ActivityHour'].dt.date 
        df['HourOfDay'] = df['ActivityHour'].dt.hour 
        print(f"  - Converted 'ActivityHour' to datetime. Added 'ActivityDay', 'HourOfDay'.")

    elif 'ActivityMinute' in df.columns: # Found in minuteCaloriesNarrow, minuteIntensitiesNarrow, minuteMETsNarrow, minuteStepsNarrow, minuteSleep
        # Try a flexible parse, then a specific one if needed
        df['ActivityMinute'] = pd.to_datetime(df['ActivityMinute'], errors='coerce')
        if df['ActivityMinute'].isnull().all(): 
             df['ActivityMinute'] = pd.to_datetime(df['ActivityMinute'], format='%Y-%m-%d %H:%M:%S', errors='coerce') # Try another format
        df['ActivityDay'] = df['ActivityMinute'].dt.date
        df['HourOfDay'] = df['ActivityMinute'].dt.hour

        print(f" Converted 'ActivityMinute' to datetime. Added 'ActivityDay', 'HourOfDay'.")
        if df_name == 'minuteSleep_merged' and 'date' in df.columns:
            df = df.rename(columns={'date': 'ActivityMinute'}) 
            df['ActivityMinute'] = pd.to_datetime(df['ActivityMinute'], errors=['coerce'])
            df['ActivityDay'] = df['ActivityMinute'].dt.date
            df['HourOfDay'] = df['ActivityMinute'].dt.hour
            print(f"(minuteSleep_merged specific) Renamed 'date' to 'ActivityMinute', converted and added features.")

    elif 'Time' in df.columns and df_name == 'heartrate_seconds_merged': 
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df['ActivityDay'] = df['Time'].dt.date
        df['HourOfDay'] = df['Time'].dt.hour
        print(f"Converted 'Time' to datetime. Added 'ActivityDay', 'HourOfDay'.")

    elif 'Date' in df.columns and df_name == 'weightLogInfo_merged': 
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
        df['ActivityDay'] = df['Date'].dt.date
        print(f"Converted 'Date' to datetime. Added 'ActivityDay'.")

    elif 'ActivityDay' in df.columns: 
        df['ActivityDay'] = pd.to_datetime(df['ActivityDay'], errors='coerce')
        df['DayOfWeek'] = df['ActivityDay'].dt.day_name()
        print(f"Converted 'ActivityDay' to datetime. Added 'DayOfWeek'.")
else:
        print(f"No standard date/time column found for automatic conversion in '{df_name}'.")

    # 2 Handle Missing Values (Reporting and Basic Action)
    # or were already present.
null_counts = df.isnull().sum()
null_cols_with_counts = null_counts[null_counts > 0]

if not null_cols_with_counts.empty:
        print(f"Detected Null values in '{df_name}' after conversion:")
        print(null_cols_with_counts)
        # Decision: For now, we'll just report. In a full project, you'd decide to:
        initial_rows = df.shape[0]
        df.dropna(subset=[col for col in df.columns if df[col].dtype == '<M8[ns]'], inplace=True) # Drop rows where essential date columns became NaT
        rows_after_drop = df.shape[0]
        if initial_rows > rows_after_drop:
            print(f"Dropped {initial_rows - rows_after_drop} rows due to unparseable date/time values.")
else:
        print(f"No null values detected in '{df_name}' after primary processing.")

    #2.3 Specific Data Quality Checks and Adjustments (as per PPT) ---
if df_name == 'dailyActivity_merged' and 'SedentaryMinutes' in df.columns:
        # 1440 sedentary minutes might indicate tracker non-wear.
        full_day_sedentary_records = df[df['SedentaryMinutes'] >= 1440]
        if not full_day_sedentary_records.empty:
            print(f"Identified {len(full_day_sedentary_records)} records with >= 1440 SedentaryMinutes (potential non-wear).")
            # For demonstration, we can calculate the percentage of such records
            percentage_sedentary = (len(full_day_sedentary_records) / df.shape[0]) * 100
            print(f"This represents {percentage_sedentary:.2f}% of 'dailyActivity_merged' records.")
else:
            print("No records with >= 1440 SedentaryMinutes detected.")
        
if df_name == 'sleepDay_merged':
        # Check for consistency between TotalSleepRecords and actual sleep duration Or look for zero sleep records with non-zero time in bed
   if (df['TotalMinutesAsleep'] == 0).any():
            zero_sleep_records = df[df['TotalMinutesAsleep'] == 0].shape[0]
            print(f"Detected {zero_sleep_records} records with 0 'TotalMinutesAsleep'.")

if df_name == 'weightLogInfo_merged':
        # Check for BMI values, or manual reports
        if 'BMI' in df.columns and df['BMI'].isnull().any():
            print(f"Detected {df['BMI'].isnull().sum()} nulls in 'BMI' column.")
        if 'IsManualReport' in df.columns:
            manual_reports = df['IsManualReport'].sum()
            print(f"{manual_reports} records are manually reported ('IsManualReport' is True).")

    # Update the DataFrame in the global dictionary after all cleaning for this file
dataframes[df_name] = df

print(f" Finished processing '{df_name}'. Updated info:")
df.info(verbose=False, memory_usage="deep")
print(df.head()) 
print("Finished processing and Updated info")

print("\nData Cleaning and Preprocessing Complete for all loaded DataFrames")
print("All processed DataFrames are now ready for analysis and stored in the 'all_dataframes' dictionary.")
print("You can access them using e.g., all_dataframes['dailyActivity_merged']")


# Prepare daily activity for merging
print("\nStarting Data Merging for Daily Analysis")

# Prepare daily activity for merging
df_daily = dataframes.get('dailyActivity_merged')
if df_daily is None:
    print("ERROR: 'dailyActivity_merged' DataFrame is not available. Cannot perform daily merges. Please ensure the file was loaded successfully.")

df_daily = df_daily.rename(columns={'ActivityDate': 'Date'})
df_daily['Date'] = pd.to_datetime(df_daily['Date'])
df_daily['Date'] = df_daily['Date'].dt.date

# Merge dailyCalories_merged
df_calories = dataframes.get('dailyCalories_merged')
if df_calories is not None:
    df_calories = df_calories.rename(columns={'ActivityDay': 'Date'})
    df_calories['Date'] = pd.to_datetime(df_calories['Date'], errors='coerce').dt.date
    df_daily = pd.merge(df_daily, df_calories[['Id', 'Date', 'Calories']], on=['Id', 'Date'], how='left', suffixes=('_activity', '_calories'))
    print("Merged 'dailyCalories_merged'.")

  # Merge dailyIntensities_merged
df_intensities = dataframes.get('dailyIntensities_merged')
if df_intensities is not None:
    df_intensities = df_intensities.rename(columns={'ActivityDay': 'Date'})
    df_intensities['Date'] = pd.to_datetime(df_intensities['Date'], errors='coerce').dt.date
    # Be careful with columns that might duplicate or need to be differentiated
    df_daily = pd.merge(df_daily, df_intensities.drop(columns=['SedentaryActiveDistance', 'LightActiveDistance', 'ModeratelyActiveDistance', 'VeryActiveDistance'], errors='ignore'), on=['Id', 'Date'], how='left', suffixes=('', '_intensity'))
    print("Merged 'dailyIntensities_merged'.")

    # Merge sleepDay_merged
df_sleep = dataframes.get('sleepDay_merged')
if df_sleep is not None:
    df_sleep = df_sleep.rename(columns={'SleepDay': 'Date'})
    df_sleep['Date'] = pd.to_datetime(df_sleep['Date'], format=DATE_FORMAT, errors='coerce').dt.date
    df_daily = pd.merge(df_daily, df_sleep[['Id', 'Date', 'TotalSleepRecords', 'TotalMinutesAsleep', 'TotalTimeInBed']], on=['Id', 'Date'], how='left')
    print("Merged 'sleepDay_merged'.")

    print("\nDaily Merged DataFrame Head")
print(df_daily.head())
print(f"\nShape of combined daily DataFrame: {df_daily.shape}")
print(f"Null values after merging (check sleep columns):\n{df_daily[['TotalMinutesAsleep', 'TotalTimeInBed']].isnull().sum()}")


# Key Analysis and Visualizations

print("\n\nData Visualizations")

# Set style for all plots
try:
    plt.style.use('seaborn-v0_8')  # Newer style name
except:
    try:
        plt.style.use('seaborn')  # Fallback to older style
    except:
        plt.style.use('ggplot')  # Final fallback

sns.set_palette("husl")

# Visualization Weekly Activity Pattern
if df_daily is not None and 'TotalSteps' in df_daily.columns:
    # Ensure we have DayOfWeek column
    if 'DayOfWeek' not in df_daily.columns and 'Date' in df_daily.columns:
        df_daily['DayOfWeek'] = pd.to_datetime(df_daily['Date']).dt.day_name()
    
    if 'DayOfWeek' in df_daily.columns:
        weekdays_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        avg_steps = df_daily.groupby('DayOfWeek')['TotalSteps'].mean().reindex(weekdays_order)
        
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x=avg_steps.index, 
                y=avg_steps.values,
                hue=avg_steps.index,   
                palette="coolwarm",
                legend=False)     
          
        plt.title('Average Daily Steps by Day of Week', fontsize=16, pad=20)
        plt.xlabel('Day of Week', fontsize=12)
        plt.ylabel('Average Steps', fontsize=12)
        
        for p in ax.patches:
            ax.annotate(f"{int(p.get_height())}", 
                       (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='center', xytext=(0, 10), 
                       textcoords='offset points')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    else:
        print("Cannot create weekly activity plot - missing day of week data")
else:
    print("Cannot create weekly activity plot - missing steps data")

# Visualization Activity Distribution
if df_daily is not None:
    activity_cols = ['VeryActiveMinutes', 'FairlyActiveMinutes', 
                    'LightlyActiveMinutes', 'SedentaryMinutes']
    if all(col in df_daily.columns for col in activity_cols):
        avg_activity = df_daily[activity_cols].mean()
        
        plt.figure(figsize=(10, 6))
        ax = avg_activity.plot(kind='bar', color=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'])
        
        plt.title('Average Daily Activity Minutes', fontsize=16, pad=20)
        plt.xlabel('Activity Level', fontsize=12)
        plt.ylabel('Minutes', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        for p in ax.patches:
            ax.annotate(f"{int(p.get_height())}", 
                       (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='center', xytext=(0, 10), 
                       textcoords='offset points')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    
# Visualization 3: Hourly Calories
df_hourly = dataframes.get('hourlyCalories_merged')
if df_hourly is not None and 'Calories' in df_hourly.columns:
   
    if 'HourOfDay' not in df_hourly.columns and 'ActivityHour' in df_hourly.columns:
        df_hourly['HourOfDay'] = pd.to_datetime(df_hourly['ActivityHour'], format=DATE_FORMAT).dt.hour

    if 'HourOfDay' in df_hourly.columns:
        avg_hourly_calories = df_hourly.groupby('HourOfDay')['Calories'].mean()
        
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=avg_hourly_calories.index, y=avg_hourly_calories.values, 
                         marker='o', color='#9b59b6', linewidth=2.5)
        
        plt.title('Average Hourly Calories Burned', fontsize=16, pad=20)
        plt.xlabel('Hour of Day', fontsize=12)
        plt.ylabel('Calories Burned', fontsize=12)
        plt.xticks(range(24))
        
        peak_hour = avg_hourly_calories.idxmax()
        plt.axvline(x=peak_hour, color='#e74c3c', linestyle='--', alpha=0.7)
        plt.text(peak_hour+0.5, avg_hourly_calories.max()-5, 
                f'Peak: {peak_hour}:00 ({avg_hourly_calories.max():.1f} cal)',
                color='#e74c3c')
        
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()
    
# Visualization 4: Sleep vs Activity
if df_daily is not None and 'TotalMinutesAsleep' in df_daily.columns and 'TotalSteps' in df_daily.columns:
    # Create a copy for plotting
    plot_data = df_daily.copy()
    
    # Add DayOfWeek if not present but Date is available
    if 'DayOfWeek' not in plot_data.columns and 'Date' in plot_data.columns:
        plot_data['DayOfWeek'] = pd.to_datetime(plot_data['Date']).dt.day_name()
    
    plt.figure(figsize=(10, 6))
    
    # Create the plot with or without DayOfWeek
    if 'DayOfWeek' in plot_data.columns and len(plot_data['DayOfWeek'].unique()) > 1:
        ax = sns.scatterplot(data=plot_data, x='TotalSteps', y='TotalMinutesAsleep',
                            hue='DayOfWeek', palette='viridis', s=100, alpha=0.7)
    else:
        ax = sns.scatterplot(data=plot_data, x='TotalSteps', y='TotalMinutesAsleep',
                            color='blue', s=100, alpha=0.7)
    
    plt.title('Daily Steps vs Sleep Duration', fontsize=16, pad=20)
    plt.xlabel('Total Steps', fontsize=12)
    plt.ylabel('Minutes Asleep', fontsize=12)
    
    # Add regression line
    sns.regplot(data=plot_data, x='TotalSteps', y='TotalMinutesAsleep',
               scatter=False, color='red', line_kws={'linestyle':'--', 'alpha':0.5})
    
    # Calculate and display correlation
    correlation = plot_data['TotalSteps'].corr(plot_data['TotalMinutesAsleep'])
    plt.text(0.05, 0.95, f'Correlation: {correlation:.2f}',
            transform=ax.transAxes, fontsize=12,
            bbox=dict(facecolor='white', alpha=0.8))
    
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3

# Comprehensive Activity Dashboard
if df_daily is not None:
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle('Fitness Activity Dashboard', fontsize=16, y=1.02)

    # Activity Minutes Breakdown
if all(col in df_daily.columns for col in ['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']):
        activity_cols = ['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']
        activity_labels = ['Very Active', 'Fairly Active', 'Lightly Active', 'Sedentary']
        activity_pct = df_daily[activity_cols].mean() / df_daily[activity_cols].mean().sum() * 100
        
        wedges, texts, autotexts = axes[0,0].pie(activity_pct, 
                                               labels=activity_labels,
                                               autopct='%1.1f%%',
                                               startangle=90,
                                               colors=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'])
        axes[0,0].set_title('Activity Minutes Distribution', pad=20)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    # Steps Trend Over Time
if 'Date' in df_daily.columns and 'TotalSteps' in df_daily.columns:
        df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        df_daily.set_index('Date', inplace=True)
        monthly_steps = df_daily['TotalSteps'].resample('W').mean()
        
        axes[0,1].plot(monthly_steps.index, monthly_steps.values, 
                      marker='o', color='#9b59b6', linewidth=2)
        axes[0,1].set_title('Weekly Steps Trend')
        axes[0,1].set_ylabel('Average Steps')
        axes[0,1].fill_between(monthly_steps.index, monthly_steps.values, 
                              alpha=0.2, color='#9b59b6')
    
    # Calories vs Steps Relationship
if all(col in df_daily.columns for col in ['Calories_calories', 'TotalSteps']):
        
        # Convert to numeric if needed
        df_daily['Calories_calories'] = pd.to_numeric(df_daily['Calories_calories'], errors='coerce')
        df_daily['TotalSteps'] = pd.to_numeric(df_daily['TotalSteps'], errors='coerce')
        
        # Drop NA values
        plot_data = df_daily[['Calories_calories', 'TotalSteps']].dropna()
        
        
        if len(plot_data) > 0:
            sns.regplot(ax=axes[1,0], 
                       x='TotalSteps', y='Calories_calories', 
                       data=plot_data,
                       scatter_kws={'alpha':0.6, 'color':'#3498db'},
                       line_kws={'color':'#e74c3c', 'linestyle':'--'})
            axes[1,0].set_title('Steps vs Calories Burned')
            axes[1,0].set_xlabel('Total Steps')
            axes[1,0].set_ylabel('Calories Burned')
            
            corr = plot_data['TotalSteps'].corr(plot_data['Calories_calories'])
            axes[1,0].annotate(f'Correlation: {corr:.2f}', 
                              xy=(0.7, 0.1), xycoords='axes fraction',
                              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
else:
            axes[1,0].text(0.5, 0.5, 'No valid data points', ha='center', va='center')
    
    # Sleep Efficiency
if 'TotalMinutesAsleep' in df_daily.columns and 'TotalTimeInBed' in df_daily.columns:
        df_daily['SleepEfficiency'] = df_daily['TotalMinutesAsleep'] / df_daily['TotalTimeInBed'] * 100
        sns.histplot(ax=axes[1,1], 
                    x=df_daily['SleepEfficiency'].dropna(),
                    bins=20, 
                    kde=True,
                    color='#2ecc71')
        axes[1,1].axvline(x=85, color='#e74c3c', linestyle='--')
        axes[1,1].set_title('Sleep Efficiency Distribution')
        axes[1,1].set_xlabel('Sleep Efficiency (%)')
        axes[1,1].annotate('Recommended >85%', 
                          xy=(0.65, 0.9), xycoords='axes fraction',
                          color='#e74c3c')
    
plt.tight_layout()
plt.show()

# Hourly Activity Heatmap
if 'hourlySteps_merged' in dataframes:
    df_hourly_steps = dataframes['hourlySteps_merged'].copy()
    if 'ActivityHour' in df_hourly_steps.columns:
        df_hourly_steps['Hour'] = pd.to_datetime(df_hourly_steps['ActivityHour'], format=DATE_FORMAT).dt.hour
        df_hourly_steps['DayOfWeek'] = pd.to_datetime(df_hourly_steps['ActivityHour'], format=DATE_FORMAT).dt.day_name()
        
        # Prepare heatmap data
        heatmap_data = df_hourly_steps.pivot_table(index='DayOfWeek', 
                                                  columns='Hour', 
                                                  values='StepTotal', 
                                                  aggfunc='mean')
        
        # Order days properly
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(day_order)
        
        plt.figure(figsize=(16, 6))
        sns.heatmap(heatmap_data, 
                   cmap='YlOrRd',
                   linewidths=0.1,
                   annot=True, 
                   fmt='.0f',
                   cbar_kws={'label': 'Average Steps'})
        plt.title('Hourly Activity Patterns by Day of Week', pad=20)
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.tight_layout()
        plt.show()

# Activity-Sleep Relationship Matrix
if df_daily is not None:
    if all(col in df_daily.columns for col in ['TotalSteps', 'TotalMinutesAsleep', 'SedentaryMinutes', 'Calories']):
        # Select relevant columns
        relationship_cols = ['TotalSteps', 'TotalMinutesAsleep', 'SedentaryMinutes', 'Calories']
        relationship_df = df_daily[relationship_cols].dropna()
        
        # Calculate correlations
        corr_matrix = relationship_df.corr()
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, 
                   mask=mask,
                   cmap='coolwarm',
                   vmin=-1, vmax=1,
                   annot=True,
                   fmt=".2f",
                   linewidths=0.5,
                   center=0)
        plt.title('Activity-Sleep Relationship Matrix', pad=20)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
