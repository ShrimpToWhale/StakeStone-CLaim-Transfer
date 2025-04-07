#!/usr/bin/env python3
"""
StakeStone Claim and Transfer Application

This application automates the claiming and transferring of StakeStone (STO) 
airdrop allocations, including the transfer of native BNB tokens.
"""
from colorama import init, Style

# Initialize colorama
init(autoreset=True)

# Import configuration and utilities
from src.config.constants import STO_TOKEN_ABI_PATH, STO_CLAIM_ABI_PATH
from src.utils.file_operations import load_wallet_data, load_contract_abi
from src.utils.input_handler import get_user_config, shuffle_wallets_if_needed
from src.services.processor import Processor


def main():
    """Main entry point for the application."""
    try:
        # Get user configuration
        config = get_user_config()
        
        # Load wallet data
        wallets = load_wallet_data()
        
        # Shuffle wallets if requested
        if config.shuffle_wallets:
            wallets = shuffle_wallets_if_needed(wallets, True)
        
        # Load contract ABIs
        sto_token_abi = load_contract_abi(STO_TOKEN_ABI_PATH)
        claim_contract_abi = load_contract_abi(STO_CLAIM_ABI_PATH)
        
        # Create processor and process wallets
        processor = Processor(config, claim_contract_abi, sto_token_abi)
        processor.process_wallets(wallets)
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        print("Please make sure all required files exist.")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    main() 