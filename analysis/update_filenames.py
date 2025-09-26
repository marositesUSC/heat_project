import os
import shutil
import pandas as pd

def update_filenames(input_directory, output_directory = None):
    """
    Our data files are named based on the Raspberry Pi's datetime, which is not correct. 
    This function copies, reads, and renames the files in the specified directory to the first timestamp in the file and the sensor name. 
    

    Args:
        input_directory (str): The path to the directory containing the files to be renamed.
        output_directory (str): The path to the directory where renamed files will be saved.
    """
    for filename in os.listdir(input_directory):
        if filename.startswith('sensor') and filename.endswith('.csv'):
            try:   
                # read the file
                file_path = os.path.join(input_directory, filename)
                df = pd.read_csv(file_path)
                df = df.dropna()  # Drop rows with all NaN values
                df['GPS_Timestamp_UTC'] = pd.to_datetime(df['GPS_Timestamp_UTC'])

                # Get the first timestamp and Raspberry Pi name
                raspberry_pi_name = df['RaspberryPiName'].iloc[0]
                first_timestamp = df['GPS_Timestamp_UTC'].iloc[0].strftime('%Y%m%d_%H%M')

                # Create the new filename
                new_filename = f"{raspberry_pi_name}_{first_timestamp}.csv"
                if output_directory is None:
                    output_directory = input_directory+'/renamed_files'
                os.makedirs(output_directory, exist_ok=True)
                new_file_path = os.path.join(output_directory, new_filename)
                # Save the renamed file
                df.to_csv(new_file_path, index=False)
                print(f"Renamed {filename} to {new_filename}")

            # if there is no data, move the file to a new directory
            except pd.errors.EmptyDataError:
                print(f"No data in {filename}, moving to 'empty_files' directory.")
                empty_dir = os.path.join(input_directory, 'empty_files')
                os.makedirs(empty_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(empty_dir, filename))

            # if there is an error, print the error
            except Exception as e:
                print(f"Error processing {filename}: {e}")



if __name__ == "__main__":
    input_dir = r'C:\Users\bmaro\OneDrive\Desktop\New folder (2)\post'
    update_filenames(input_dir)




# d = r"C:\Users\bmaro\OneDrive - University of South Carolina\Columbia Heat Project\heat_mapping\Raw_files\sensor_data_20250818_205431.csv"
# data = pd.read_csv(d)
# print(data)
