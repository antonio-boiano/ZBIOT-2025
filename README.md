# ZBIOT-2025

Step1: **1_Ground-truth-generation.py** is to match the type and name of the device based on the device address, saved in the file "groundtruth"  
Step2: **2_Packet Information Extractor.py** is to extract key information from each packet such as time, length, delta time, sequence number, etc. And saved in the folder "Extracted_Dataset"  
Step3: **3_Combine the features.py** is combine the information extracted from the first two steps together, saved in the folder "Raw_dataset"  
Step4: **4_Aggregated_all_the_raw_data.py** is to merge the Raw_dataset files of different topologies under "Idle", "Physical_Interaction", "Scenario", "Web_Interaction" and store them in the "Aggregated_Data" folder.  
Step5: **5_Create_Sequence_data_fix_packets.py** is to generate a new sequential dataset by fixing the number of consecutive packets(3 packets) in a sliding window approach, extracting statistical features (e.g., average packet length, sequence number, etc.), and adding device information to generate a new feature datasheet.It is used for subsequent data analysis.The results are stored in the folder "Sequence_Data".  
Step6: **6_Create_Sequence_data_fix_durations.py**is to generate a new sequential dataset by fixing the duration of consecutive packets(0.5 seconds) in a sliding window approach. The results are stored in the folder "Sequence_Data".  
Step7: **7_Drop_Unknown_labels.py** is to deletes rows containing missing values and the device name "Unknown". The results are stored in the folder "Sequence_Data" and there is "_known" in the end of name.  
Step8: **8-1_Same_topology.ipynb** is to do the device type classification and name identification of the same topology like train A test A & train B test B including the two type of dataset, one for packets fixed and another for duration fixed.  
Step8: **8-2_Different_topology.ipynb** is to do the device type classification and name identification of the different topologies like train A test B & train B test A including the two type of dataset, one for packets fixed and another for duration fixed.  
