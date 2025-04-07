"""
Utility functions for file operations.
"""
import os
from typing import List, Dict
from src.config.constants import USER_DATA_DIR
from src.models.wallet import Wallet
from colorama import Fore


def read_file(file_name: str) -> List[str]:
    """
    Read a file and return its contents as a list of lines.
    
    Args:
        file_name: Name of the file to read (without extension)
        
    Returns:
        List of lines from the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    file_path = os.path.join(USER_DATA_DIR, f"{file_name}.txt")
    try:
        with open(file_path, 'r', encoding='UTF-8') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        raise FileNotFoundError(f'"{file_name}.txt" file or directory not found')


def load_wallet_data() -> List[Wallet]:
    """
    Load wallet data from files and create Wallet objects.
    
    Returns:
        List of Wallet objects with data from the files
        
    Raises:
        Exception: If the files have different lengths
    """
    # Read data from files
    private_keys = read_file('wallets')
    proxies = read_file('proxies')
    recipients = read_file('recipients')
    
    # Check that all files have the same length
    if not (len(private_keys) == len(proxies) == len(recipients)):
        raise ValueError("The number of private keys, proxies, and recipient addresses must be the same")
    
    # Create Wallet objects
    wallets = []
    for i, private_key in enumerate(private_keys):
        wallet = Wallet(
            private_key=private_key,
            proxy=proxies[i],
            recipient_address=recipients[i]
        )
        wallets.append(wallet)
    
    return wallets


def load_contract_abi(file_path: str) -> dict:
    """
    Load a contract ABI from a JSON file.
    
    Args:
        file_path: Path to the ABI JSON file
        
    Returns:
        Contract ABI as a dictionary
    """
    import json
    try:
        with open(file_path, 'r', encoding='UTF-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Contract ABI file not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in ABI file: {file_path}") 