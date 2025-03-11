
Step1: **1_Ground-truth-generation.py** is to match the type and name of the device based on the device address, saved in the file "groundtruth"  
Step2: **2_Packet Information Extractor.py** is to extract key information from each packet such as time, length, delta time, sequence number, etc. And saved in the folder "Extracted_Dataset"  
Step3: **3_Combine the features.py** is combine the information extracted from the first two steps together, saved in the folder "Raw_dataset"  
Step4: **4_Aggregated_all_the_raw_data.py** is to merge the Raw_dataset files of different topologies under "Idle", "Physical_Interaction", "Scenario", "Web_Interaction" and store them in the "Aggregated_Data" folder.  
Step5: **5_Drop_Unknown_labels.py** is to drop the unknown label data and some key information lost data and store the new dataset in the "Aggregated_Data" folder.  

