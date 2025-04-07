# StakeStone (STO) Airdrop Claim & Transfer

Software for automatically claiming and transferring StakeStone (STO) airdrop allocations, including the transfer of native tokens.

## 🔔 Author's Info
- Author: [https://t.me/zero_0x_zero](https://t.me/zero_0x_zero)
- Channel: [https://t.me/shrimp_to_whale](https://t.me/shrimp_to_whale)

## ✨ Features
- 🟢 Airdrop claim
- 🟢 STO token transfer
- 🟢 Native(BnB) token transfer

## 🚀 Installation and Launch

1. Clone the repository:
   ```bash
   git clone https://github.com/ShrimpToWhale/StakeStone-CLaim-Transfer
   ```

2. Navigate to the project directory:
   ```bash
   cd StakeStone-CLaim-Transfer
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Run the script:
   ```bash
   python app.py
   ```

## 📁 Required Files
- `wallets.txt` - private keys of your EVM accounts (with or without '0x')
- `recipients.txt` - addresses where STO and BNB will be deposited
- `proxies.txt` - proxies in the login:password@host:port format

> ⚠️ **Important**: The number of proxies, private keys, and deposit addresses must be the same.
> 
> ⚠️ If a proxy is not working, the software will automatically use the local IP to send requests.

## 🛠️ Workflow and Configuration

Upon launching the software, you'll be prompted to set two types of delays (in seconds):
1. Delay between accounts – how long the script waits before switching to the next account
2. Delay between actions – pauses between claiming, STO and BNB transferring

You'll also be asked whether you want to shuffle the wallets before execution (each private key keeps its original address and proxy pairing).

> **Note**: The software executes claim, STO transfer, and BNB transfer sequentially.
> If a wallet does not have enough funds or is not eligible for the airdrop, the subsequent operations will not be performed.

## 🏗️ Project Structure

The application has been refactored to follow Object-Oriented Programming principles and modular architecture (by pcristin):

```
StakeStone-CLaim-Transfer/
├── main.py                # Main application entry point
├── requirements.txt       # Dependencies
├── README.md              # Documentation
├── src/                   # Source code package
│   ├── config/            # Configuration files
│   │   ├── constants.py   # Application constants
│   ├── models/            # Data models
│   │   ├── wallet.py      # Wallet model
│   ├── services/          # Business logic
│   │   ├── claim_service.py     # Airdrop claiming logic
│   │   ├── transfer_service.py  # Token transfer logic
│   │   ├── processor.py         # Main workflow processor
│   └── utils/             # Utility functions
│       ├── file_operations.py   # File reading/writing
│       ├── input_handler.py     # User input handling
│       └── network.py           # Network operations
├── user_data/             # User data files
│   ├── wallets.txt        # Private keys
│   ├── proxies.txt        # Proxy settings
│   └── recipients.txt     # Recipient addresses
└── global_data/           # Global data
    ├── STO_TOKEN_ABI.json # STO token ABI
    └── STO_CLAIM_ABI.json # Claim contract ABI
```
