## ​Software for automatically claiming and transferring StakeStone (STO) airdrop allocations, including the transfer of native tokens.

**Author's info**
- 💬 Author: [https://t.me/zero_0x_zero](https://t.me/zero_0x_zero)
- 🔔 CHANNEL: [https://t.me/shrimp_to_whale](https://t.me/shrimp_to_whale)

**Features**
- 🟢 Airdrop claim
- 🟢 STO token transfer
- 🟢 Native(BnB) token transfer

**Installation and launch**
1. git clone [https://github.com/ShrimpToWhale/StakeStone-CLaim-Transfer](https://github.com/ShrimpToWhale/StakeStone-CLaim-Transfer)
2. cd StakeStone-CLaim-Transfer
3. pip install -r requirements.txt
4. python main.py

**Files that need to be filled out**
- `wallets.txt` - private keys of your EVM accounts (with or without '0x')
- `recipients.txt` - addresses where STO and BNB will be deposited
- `proxies.txt` - proxies in the login:password@host:port format
  
❗ **The number of proxies, private keys, and deposit addresses must be the same**

❗**If a proxy is not working, the software will automatically use the local IP to send requests.**

**Workflow and Configuration**
Upon launching the software, you’ll be prompted to set two types of delays:
1. Delay between accounts – how long the script waits before switching to the next account
2. Delay between actions – pauses between claiming, STO and BNB transfering

You’ll also be asked whether you want to shuffle the wallets before execution(the private key, deposit address, and proxy will remain correctly paired, although proxies will still be used in their original order.
