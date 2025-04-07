"""
Service for transferring STO tokens and native BNB.
"""
from colorama import Fore, Style
from web3 import Web3

from src.config.constants import STO_TOKEN_ADDRESS
from src.utils.network import wait_for_transaction


class TransferService:
    """Service for transferring tokens."""
    
    def __init__(self, web3: Web3, sto_token_abi: dict):
        """
        Initialize the transfer service.
        
        Args:
            web3: Web3 instance
            sto_token_abi: ABI for the STO token contract
        """
        self.web3 = web3
        self.sto_contract = web3.eth.contract(
            address=web3.to_checksum_address(STO_TOKEN_ADDRESS), 
            abi=sto_token_abi
        )
    
    def transfer_sto(self, sender_address: str, recipient_address: str, sender_private_key: str) -> bool:
        """
        Transfer STO tokens to recipient address.
        
        Args:
            sender_address: Address of the sender
            recipient_address: Address of the recipient
            sender_private_key: Private key of the sender
            
        Returns:
            True if transfer was successful, False otherwise
        """
        try:
            # Check token balance
            token_balance = self.sto_contract.functions.balanceOf(sender_address).call()
            
            if token_balance == 0:
                print(Fore.RED + f'Insufficient token balance to transfer, {sender_address}: {token_balance} STO')
                return False
            
            # Build transaction
            transaction = {
                'chainId': self.web3.eth.chain_id,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'from': sender_address,
                'gasPrice': self.web3.to_wei('1', 'gwei'),
            }
            
            # Create token transfer transaction
            transaction = self.sto_contract.functions.transfer(
                recipient_address, 
                token_balance
            ).build_transaction(transaction)
            
            # Estimate gas
            transaction['gas'] = self.web3.eth.estimate_gas(transaction)
            
            # Sign and send transaction
            return self._sign_and_send_transaction('Transfer STO', transaction, sender_private_key)
            
        except Exception as e:
            print(Fore.RED + f"{sender_address}: error during STO transfer: {e}")
            return False
    
    def transfer_native(self, sender_address: str, recipient_address: str, sender_private_key: str) -> bool:
        """
        Transfer native BNB to recipient address.
        
        Args:
            sender_address: Address of the sender
            recipient_address: Address of the recipient
            sender_private_key: Private key of the sender
            
        Returns:
            True if transfer was successful, False otherwise
        """
        try:
            # Get native balance
            native_balance = self.web3.eth.get_balance(sender_address)
            
            if native_balance == 0:
                print(Fore.RED + f'Insufficient BNB balance to transfer, {sender_address}: 0 BNB')
                return False
            
            # Build transaction
            transaction = {
                'chainId': self.web3.eth.chain_id,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'from': sender_address,
                'to': recipient_address,
                'gasPrice': self.web3.to_wei('1', 'gwei'),
            }
            
            # Estimate gas
            transaction['gas'] = self.web3.eth.estimate_gas(transaction)
            
            # Calculate value to send (total balance - gas cost with safety margin)
            gas_cost = transaction['gas'] * transaction['gasPrice'] * 1.5  # 50% margin for safety
            value_to_send = int(native_balance - gas_cost)
            
            if value_to_send <= 0:
                print(Fore.RED + f'Insufficient BNB balance after gas, {sender_address}')
                return False
                
            transaction['value'] = value_to_send
            
            # Sign and send transaction
            return self._sign_and_send_transaction('Transfer BNB', transaction, sender_private_key)
            
        except Exception as e:
            print(Fore.RED + f"{sender_address}: error during BNB transfer: {e}")
            return False
    
    def _sign_and_send_transaction(self, operation_type: str, transaction: dict, sender_private_key: str) -> bool:
        """
        Sign and send a transaction.
        
        Args:
            operation_type: Type of operation (for display)
            transaction: Transaction to send
            sender_private_key: Private key to sign with
            
        Returns:
            True if transaction was successful, False otherwise
        """
        try:
            # Sign transaction
            raw_transaction = self.web3.eth.account.sign_transaction(transaction, sender_private_key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(raw_transaction.rawTransaction)
            
            # Wait for confirmation
            return wait_for_transaction(self.web3, tx_hash, operation_type)
            
        except Exception as e:
            sender_address = self.web3.eth.account.from_key(sender_private_key).address
            print(Fore.RED + f'{sender_address}: error during {operation_type.lower()} transaction: {e}')
            return False 