"""
Network-related utility functions.
"""
import requests
from typing import Optional, Tuple
from colorama import Fore
from web3 import Web3
from web3.exceptions import TimeExhausted

from src.config.constants import BSC_EXPLORER_URL


def check_proxy(proxy: str) -> Optional[str]:
    """
    Test if a proxy is working.
    
    Args:
        proxy: Proxy string in format login:password@host:port
        
    Returns:
        Formatted proxy URL if working, None otherwise
    """
    if not proxy:
        return None
        
    try:
        response = requests.get(
            'https://httpbin.org/ip', 
            proxies={
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }, 
            timeout=10
        )
        
        if response.status_code != 200:
            print(Fore.YELLOW + f'Proxy {proxy} returned status: {response.status_code}, continue without it')
            return None
        else:
            return f'http://{proxy}'
    except Exception as e:
        print(Fore.YELLOW + f'Proxy {proxy} connection failed, continue without it')
        return None


def create_web3_instance(rpc_url: str, proxy: Optional[str] = None) -> Web3:
    """
    Create a Web3 instance with optional proxy.
    
    Args:
        rpc_url: RPC URL to connect to
        proxy: Optional proxy URL
        
    Returns:
        Web3 instance
    """
    if proxy:
        web3 = Web3(Web3.HTTPProvider(
            rpc_url,
            request_kwargs={
                'proxies': {
                    'http': proxy,
                    'https': proxy
                }
            }
        ))
    else:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # Check connection
    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the blockchain RPC endpoint")
    
    return web3


def wait_for_transaction(web3: Web3, tx_hash, operation_type: str) -> bool:
    """
    Wait for a transaction to be confirmed.
    
    Args:
        web3: Web3 instance
        tx_hash: Transaction hash to wait for
        operation_type: Type of operation (for display)
        
    Returns:
        True if transaction was successful, False otherwise
    """
    try:
        print(f'{operation_type} transaction sent, it will take up to 2 minutes to confirm it')
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120, poll_latency=10)
        
        if receipt['status'] == 1:
            print(Fore.GREEN + f'Successful {operation_type.lower()} transaction: {BSC_EXPLORER_URL}tx/{tx_hash.hex()}')
            return True
        else:
            print(Fore.RED + f'{operation_type} transaction failed: {BSC_EXPLORER_URL}tx/{tx_hash.hex()}')
            return False
            
    except TimeExhausted:
        print(Fore.RED + f'{operation_type} transaction was not confirmed within 120 seconds')
        return False
    except Exception as e:
        print(Fore.RED + f'Unexpected error while waiting for confirmation of {operation_type.lower()} transaction: {e}')
        return False 