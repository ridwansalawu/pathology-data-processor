# mains

def produce(begins, ends, file_path, file_output):
    
    
    required_bloods = [ 
                        'HB', 'WCC', 'PLT', 'Sodium', 'Potassium', "Chloride", "Bicarbonate",
                        'Urea', 'Creatinine', "Estimated GFR", "Calcium", "Corrected Calcium",
                        "Magnesium", "Phosphate", "Bilirubin Total", "Albumin", "ALT", "AST", "ALP",
                        "Gamma GT", 'C Reactive Protein', 'INR', "APTT", "PT." 
                      ]
    
    
    
    
    
    
    
    
    
    
    ########################################################################################################################################
    

    
    
    ########################################################################################################################################
    
    
    
    import pandas as pd
    import openpyxl
    from tkinter import filedialog
    # import the excel as a dataframe
    labs_raw = pd.read_excel(file_path)
    # preserve the raw data, make a copy as draft
    draft = labs_raw.copy()
    # fix the columns
    drafted = draft.rename(columns= {"Detail":"observation", "Date": "date",  "Value w/Units": "value", "Normal Range":"normal_range"})
    # split the datetime column into time and date, while preserving the original datetime column
    drafted["time"] = drafted["date"].dt.time
    drafted["blood test date"] = drafted["date"].dt.strftime("%d/%m/%Y")
    # sift the needed columns
    drafted = drafted[["blood test date", "time", "observation", "value", "normal_range", "Flags"]]
    
    
    specimen = drafted.copy()
    # specimen["value"] = specimen["value"].str.replace(r'\s.*','', regex=True)
    specimen["value"] = specimen["value"].str.replace(r'^[^\d]+|(\s.*)','', regex=True)
    specimen["value"] = (
    specimen["value"]
    .str.extract(r'(\d+\.?\d*)', expand=False)
    .fillna("999999")
)

    specimen = specimen[specimen['observation'].isin(required_bloods)]
    
    specimen = specimen.pivot(index="blood test date", columns="observation", values= "value")

    # return specimen


    
    # Create a DataFrame with all required columns, filling missing ones with NaN
    for blood_test in required_bloods:
        if blood_test not in specimen.columns:
            specimen[blood_test] = pd.NA  # Add missing columns with NaN values
    
    # Reorder columns to match required_bloods order
    specimen = specimen[required_bloods]
    
    # Convert 'blood test date' from string back to datetime for proper sorting
    specimen.index = pd.to_datetime(specimen.index, format='%d/%m/%Y')
    
    # Sort the DataFrame by date in descending order
    specimen = specimen.sort_index()
    
    # If you want to display the dates in the original format again
    specimen.index = specimen.index.strftime('%d/%m/%Y')
    
    
    
    # Create a new date range index
    
    start_date = pd.to_datetime(begins, format='%d/%m/%Y')
    end_date = pd.to_datetime(ends, format='%d/%m/%Y')
    new_date_range = pd.date_range(start=start_date, end=end_date)
    
    # Create a new DataFrame with the new date range as index and the same columns
    new_specimen = pd.DataFrame(index=new_date_range, columns=specimen.columns)
    
    # Convert the original specimen index to datetime for merging
    specimen.index = pd.to_datetime(specimen.index, format='%d/%m/%Y')
    
    # Copy data from the original specimen to the new one where dates match
    for date in specimen.index:
        if date in new_date_range:
            new_specimen.loc[date] = specimen.loc[date]
    
    # Format the index back to the desired string format
    new_specimen.index = new_specimen.index.strftime('%d/%m/%Y')
    
    # Replace the original specimen with the new one
    specimen = new_specimen
    
    # Add a column with serial numbers starting from 1
    specimen.insert(0, 'Serial No.', range(1, len(specimen) + 1))
    
    final_specimen = specimen.copy()
    # return final_specimen
    ########################################################################################################################################
    
    # Create a new list to hold the interleaved column names
    new_columns = ['Serial No.', 'Serial No._normal']  # Start with the Serial No. column and its action column
    
    # For each blood test, add both the original column and a new column with "_action" suffix
    for blood_test in required_bloods:
        new_columns.append(blood_test)
        new_columns.append(f"{blood_test}_normal")
        
    # Create a new DataFrame with the interleaved columns
    interleaved_specimen = pd.DataFrame(index=final_specimen.index)
    
    # Copy the Serial No. column
    interleaved_specimen['Serial No.'] = final_specimen['Serial No.']
    interleaved_specimen['Serial No._normal'] = 'Y'
    
    # Fill in the values for each blood test
    for blood_test in required_bloods:
        # Copy the original values
        interleaved_specimen[blood_test] = final_specimen[blood_test]
        # Add the action column with "y" values
        interleaved_specimen[f"{blood_test}_normal"] = 'Y'
    
    # Replace the original final_specimen with the new one
    final_specimen = interleaved_specimen



    # Using a lambda function to apply the condition to the entire column at once
    final_specimen['HB_normal'] = final_specimen['HB'].apply(lambda x: "Y" if pd.notna(x) and 160 >= float(x) >= 115  else "N")
    final_specimen['WCC_normal'] = final_specimen['WCC'].apply(lambda x: "Y" if float(x) <= 11.0 and float(x) >= 4.0  else "N")
    final_specimen['PLT_normal'] = final_specimen['PLT'].apply(lambda x: "Y" if float(x) <= 400 and float(x) >= 150  else "N")
    final_specimen['Sodium_normal'] = final_specimen['Sodium'].apply(lambda x: "Y" if 145 >= float(x) >= 135  else "N")
    final_specimen['Potassium_normal'] = final_specimen['Potassium'].apply(lambda x: "Y" if pd.notna(x) and 5.2 >= float(x) >= 3.5  else "N")
    final_specimen['Chloride_normal'] = final_specimen['Chloride'].apply(lambda x: "Y" if pd.notna(x) and 110 >= float(x) >= 95  else "N")
    final_specimen['Bicarbonate_normal'] = final_specimen['Bicarbonate'].apply(lambda x: "Y" if pd.notna(x) and 32 >= float(x) >= 22  else "N")
    final_specimen['Urea_normal'] = final_specimen['Urea'].apply(lambda x: "Y" if pd.notna(x) and 9.0 >= float(x) >= 4.0  else "N")
    final_specimen['Creatinine_normal'] = final_specimen['Creatinine'].apply(lambda x: "Y" if pd.notna(x) and 110 >= float(x) >= 60  else "N")
    final_specimen['Estimated GFR_normal'] = final_specimen['Estimated GFR'].apply(lambda x: "Y" if pd.notna(x) and float(x) >= 90  else "N")
    final_specimen['Calcium_normal'] = final_specimen['Calcium'].apply(lambda x: "Y" if pd.notna(x) and 2.6 >= float(x) >= 2.1  else "N")
    final_specimen['Corrected Calcium_normal'] = final_specimen['Corrected Calcium'].apply(lambda x: "Y" if pd.notna(x) and 2.6 >= float(x) >= 2.1  else "N")
    final_specimen['Magnesium_normal'] = final_specimen['Magnesium'].apply(lambda x: "Y" if pd.notna(x) and 1.1 >= float(x) >= 0.7  else "N")
    final_specimen['Phosphate_normal'] = final_specimen['Phosphate'].apply(lambda x: "Y" if pd.notna(x) and 1.5 >= float(x) >= 0.75  else "N")
    final_specimen['Bilirubin Total_normal'] = final_specimen['Bilirubin Total'].apply(lambda x: "Y" if pd.notna(x) and 20 >= float(x) >= 1  else "N")
    final_specimen['Albumin_normal'] = final_specimen['Albumin'].apply(lambda x: "Y" if pd.notna(x) and 44 >= float(x) >= 30  else "N")
    final_specimen['ALT_normal'] = final_specimen['ALT'].apply(lambda x: "Y" if pd.notna(x) and 40 >= float(x) >= 5  else "N")
    final_specimen['AST_normal'] = final_specimen['AST'].apply(lambda x: "Y" if pd.notna(x) and 35 >= float(x) >= 5  else "N")
    final_specimen['ALP_normal'] = final_specimen['ALP'].apply(lambda x: "Y" if pd.notna(x) and 110 >= float(x) >= 30  else "N")
    final_specimen['Gamma GT_normal'] = final_specimen['Gamma GT'].apply(lambda x: "Y" if pd.notna(x) and 50 >= float(x) >= 5  else "N")
    final_specimen['C Reactive Protein_normal'] = final_specimen['C Reactive Protein'].apply(lambda x: "Y" if pd.notna(x) and 5 >= float(x) >= 0  else "N")
    final_specimen['INR_normal'] = final_specimen['INR'].apply(lambda x: "Y" if pd.notna(x) and float(x) <= 1.2 and float(x) >= 0.8  else "N")
    final_specimen['APTT_normal'] = final_specimen['APTT'].apply(lambda x: "Y" if pd.notna(x) and 35 >= float(x) >= 25  else "N")
    final_specimen['PT._normal'] = final_specimen['PT.'].apply(lambda x: "Y" if pd.notna(x) and 14 >= float(x) >= 10  else "N")
    
    # final_specimen['WCC_normal'] = final_specimen['WCC'].apply(lambda x: "Y" if float(x) <= 4.0 and float(x) >= 11.0  else "N")

    # final_specimen['HB_normal'] = final_specimen['HB'].apply(lambda x: "Y" if int(x) > 120 else "N")
 
    
    
    ########################################################################################################################################
    
    
    final_specimen.drop(columns="Serial No._normal", inplace=True)
    
    final_specimen.to_excel(file_output)
    return final_specimen

   

