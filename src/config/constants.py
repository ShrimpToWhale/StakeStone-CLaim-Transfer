"""
Constants and configuration values for the StakeStone claiming and transfer application.
"""

# Network configuration
BSC_RPC_URL = 'https://bsc.meowrpc.com'
BSC_EXPLORER_URL = 'https://bscscan.com/'

# Contract addresses
STO_TOKEN_ADDRESS = '0xdAf1695c41327b61B9b9965Ac6A5843A3198cf07'
CLAIM_CONTRACT_ADDRESS = '0x04bB7043eBbe5EC3f6a08EC45b3De8C36e0628B3'

# API configurations
CLAIM_API_URL = 'https://airdrop.stakestone.io/api/claim-data'
HTTP_HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://airdrop.stakestone.io",
    "Referer": "https://airdrop.stakestone.io/unified",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

# File paths
USER_DATA_DIR = './user_data'
GLOBAL_DATA_DIR = './global_data'

# Contract ABIs file paths
STO_TOKEN_ABI_PATH = f'{GLOBAL_DATA_DIR}/STO_TOKEN_ABI.json'
STO_CLAIM_ABI_PATH = f'{GLOBAL_DATA_DIR}/STO_CLAIM_ABI.json' 