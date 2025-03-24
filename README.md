# ZBIOT-2025

## Step 1-3: Data Preparation

<p align="center">
  <img src="Flow_Chart/Step1-3.png" width="600">
</p>

Step1: **1_Ground-truth-generation.py** maps devices according to addresses, saving device-related metadata into `"1-Groundtruth"`.

Step2: **2_Packet-information-extractor.py** extracts key packet details (time, length, sequence number, etc.), storing them in `"2-Information_From_PCAP"`.

Step3: **3_Combine-groundtruth-information.py** merges `"1-Groundtruth"` and `"2-Information_From_PCAP"`, saving results in `"3-Combined_dataset"`.

---

## Two Methods for Generating Sequence Data

We propose two methods:
- **Method A:** Considers communication between devices and the coordinator.
- **Method B:** Focuses only on devices, excluding coordinator packets.

<p align="center">
  <img src="Flow_Chart/A&B_method.png" width="600">
</p>

---

## **Method A: Communication-Based Sequence Data**
<p align="center">
  <img src="Flow_Chart/Method A.png" width="600">
</p>

Step 4: **A_4_Group-combined-dataset.py** groups packets by devices and removes unrelated data.

Step 5: **A_5_1_Create-sequence-data-fix-packets.py** extracts statistical features from a **fixed number of packets** in a sliding window.

Step 5: **A_5_2-Create-sequence-data-fix-duration.py** extracts features using a **fixed duration (1s)** sliding window.

Step 6: **A_6-Merge-and-drop-unknown.py** merges data across different scenarios and removes missing values.

---

## **Method B: Device-Only Sequence Data**
<p align="center">
  <img src="Flow_Chart/Method B.png" width="600">
</p>

Step 4: **B_4_Sort-clear-combined-dataset.py** removes `Coordinator` data and sorts packets by device and time.

Step 5: **B_5_1_Create-sequence-data-fix-packets.py** extracts features using a **fixed packet count sliding window**.

Step 5: **B_5_2-Create-sequence-data-fix-duration.py** extracts features using a **fixed duration (1s) sliding window**.

Step 6: **B_6-Merge-and-drop-unknown.py** merges data across scenarios and removes missing values.

---

## **Classification & Identification**
Step 8: **8-1_Same_topology.ipynb** performs device classification within the same topology (`Train A → Test A`, `Train B → Test B`).

Step 8: **8-2_Different_topology.ipynb** performs cross-topology classification (`Train A → Test B`, `Train B → Test A`).

---
