


# Bitcoin Scripting
## Team Details

**Team Name**: Synergy

**Team Members**:
- Kartik Hiranandani (230001037)
- Keshav Singhal (230001039)
- Kumar Prince (230008019)

---
## Overview
This repository contains a Python implementation of  the process of creating and validating Bitcoin transactions using Legacy (P2PKH) and SegWit (P2SH-P2WPKH) address formats in order to compare the transaction sizes and explain the key differences between the two address formats.
  

---
## Implementation 

The source code will perform the following operations:
1. Create a new wallet (or load existing wallet) and generate 3 addresses A, B and C.
3. Mine some initial blocks in order to fund address A and display the UTXO balance of A once it is funded.
5. Ask the user the amount to be transferred from A to B, satisfying the condition   `0 < Amount ≤ UTXO(A)-Mining fee  `

4. Create a raw transaction transferring coins from A to B and decode it to extract the challenge script  `ScriptPubKey` and also display its size (in vbytes).
5. Sign the transaction `A → B` using private key of A and broadcast it on the network. 	Display the transaction ID and transaction size (in vbytes).
6. Fetch and display the UTXO details of B from the transaction `A → B`
7. Create a new transaction `B → C` funded by this UTXO balance by following the same procedure as that for the transaction `A → B` and display its transaction ID and transaction size (in vbytes).
8. Decode the transaction `B → C` to extract the response script `ScriptSig` and also display its size (in vbytes).
9. Unload the wallet at the end.

---
## Customizations
### 1. User Credentials
The `bitcoin.conf` file contains the user credentials which are set to user = `admin` and password = `admin` by default. In order to adjust the credentials, update the `rpcuser` and `rpcpassword` fields inside `bitcoin.conf` file and also update the credentials inside `get_rpc_connection()` function in the Python codes.  

### 2. Number of Initial Blocks Mined
The program mines a number of initial blocks in order to fund the address A. This number is set to `101` blocks by default. It can be adjusted by altering the         `conn.generatetoaddress(101, address_A)` operation in the Python codes.

### 3. Transaction Fee 
The program assumes a transaction fee of `0.00001 BTC` by default. This fee is charged from the transactions `A → B` and `B → C` created by the Python codes. This transaction fee can be adjusted via the `fee` variable in the Python codes.

---
## How to Run the Python Codes ?
1. The programs require you to have Bitcoin Core software and Python IDLE package installed on your device.
2. Install and configure `bitcoind` on your system.
3. For a Windows device, open File Explorer and go to the location `C:\Users\<username>\AppData\Roaming\Bitcoin` ( Replace `<username>` with your actual username ).
4. Store the given `bitcoin.conf` file in this Bitcoin directory.
5. Open Command Prompt and enter the following commands to launch Bitcoin Core in regtest mode:
   
	```
	cd "C:\Program Files\Bitcoin\daemon"
	bitcoind.exe -regtest
	```
7. Run the `Legacy_1.py` code in a code editor or Python IDLE to create the transaction `A → B` and extract the challenge script `ScriptPubKey`.
8. After that, run the `Legacy_2.py` code to create the transaction `B → C` and extract the response script `ScriptSig`.
9. Before proceeding to execute the `SegWit.py` code, it is recommended to delete the transactions data stored during execution of Legacy codes to avoid any interference with SegWit code execution.
10. To delete that data, first close the Command Prompt window and then delete the `regtest` directory from inside the `Bitcoin` directory (location provided in step 3). After that, repeat step 5.
11. Now, run the `SegWit.py` code to create similar transactions and scripts in SegWit address format.

## How To Validate The Extracted Scripts ?
1. Open  Command Prompt and execute the following command to connect to the Bitcoin Debugger server:
   
	```
	ssh guest@10.206.4.201
	```
3. Enter the password `root1234` to complete the connection.
4. Execute the following command to check if the extracted scripts are valid or not:
   
	```
	btcdeb -v '<ScriptSig><ScriptPubKey'
	```
	Here, replace `<ScriptSig>` with the response script and `<ScriptPubKey>` with the challenge script, and put the concatenated string (without any spaces in between) inside the single quotes.
6. If the output contains the clause `valid script`, then the challenge and response scripts are valid. If it contains the clause `invalid script`, then the scripts are invalid.
	


---
## Acknowledgement  
- Prof. Subhra Mazumdar, for the project idea and concepts of Bitcoin scripting & adressing formats.  
- A very helpful documentation of Bitcoind access with Python on [Github](https://github.com/BlockchainCommons/Learning-Bitcoin-from-the-Command-Line/blob/master/18_4_Accessing_Bitcoind_with_Python.md).  
