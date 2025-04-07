"""
Service for claiming StakeStone tokens.
"""
from typing import Tuple, Optional
import requests
from colorama import Fore, Style
from web3 import Web3
from eth_account.messages import encode_defunct

from src.config.constants import CLAIM_API_URL, HTTP_HEADERS, CLAIM_CONTRACT_ADDRESS
from src.utils.network import wait_for_transaction


class ClaimService:
    """Service for claiming StakeStone tokens."""
    
    def __init__(self, web3: Web3, claim_contract_abi: dict):
        """
        Initialize the claim service.
        
        Args:
            web3: Web3 instance
            claim_contract_abi: ABI for the claim contract
        """
        self.web3 = web3
        self.claim_contract = web3.eth.contract(
            address=web3.to_checksum_address(CLAIM_CONTRACT_ADDRESS), 
            abi=claim_contract_abi
        )

    def claim(self, sender_address: str, sender_private_key: str) -> bool:
        """
        Claim tokens for the wallet.
        
        Args:
            sender_address: Address of the sender
            sender_private_key: Private key of the sender
            
        Returns:
            True if claim was successful, False otherwise
        """
        try:
            # Sign message to prove ownership
            message = encode_defunct(text=self._get_claim_message(sender_address))
            signed_message = self.web3.eth.account.sign_message(
                message, 
                sender_private_key
            ).signature.hex()
            
            # Get claim data
            try:
                proof, allocation, signature = self._get_claim_data(sender_address, signed_message)
            except Exception as e:
                print(Fore.RED + f"{sender_address}: {str(e)}")
                return False
            
            # Build transaction
            transaction = {
                'chainId': self.web3.eth.chain_id,
                'nonce': self.web3.eth.get_transaction_count(sender_address),
                'from': sender_address,
                'gasPrice': self.web3.to_wei('1', 'gwei'),
                'value': self.web3.to_wei('0.000830371674361444', 'ether')
            }
            
            # Check for existing claim or insufficient funds
            try:
                transaction = self.claim_contract.functions.claim(
                    proof, 
                    signature, 
                    int(allocation) * 10**18, 
                    sender_address
                ).build_transaction(transaction)
                transaction['gas'] = self.web3.eth.estimate_gas(transaction)
            except Exception as e:
                if '0x646cf558' in str(e):
                    print(Fore.YELLOW + f'{sender_address}: already claimed the airdrop')
                    return True
                elif 'insufficient funds for transfer' in str(e):
                    print(Fore.RED + f'{sender_address}: insufficient funds for claim')
                    return False
                else:
                    print(Fore.RED + f'{sender_address}: error creating claim transaction. Error: {e}')
                    return False
            
            # Sign and send transaction
            return self._sign_and_send_transaction('Claim', transaction, sender_private_key)
            
        except Exception as e:
            print(Fore.RED + f"{sender_address}: unexpected error during claim: {e}")
            return False
    
    def _get_claim_message(self, address: str) -> str:
        """Generate the claim message that needs to be signed."""
        return (f' I hereby authorize this message as confirmation of ownership for the wallet address: {address}. '
                f'By signing, I acknowledge that I have read and accepted the Airdrop Terms of Service and Privacy Policy. '
                f'The SHA-256 hash of the referenced terms and policy is: '
                f'0x676b7efc9a6eb2e90331c7c06a27499ffbcfcce4a16f3414080ad8ffc5da6b20')
    
    def _get_claim_data(self, sender_address: str, signed_message: str) -> Tuple[list, str, str]:
        """
        Get claim data from the StakeStone API.
        
        Args:
            sender_address: Wallet address
            signed_message: Signed message proving ownership
            
        Returns:
            Tuple of (proof, allocation, signature)
            
        Raises:
            Exception: If the address is not eligible or there's an API issue
        """
        data = {
            "walletAddress": sender_address,
            "batchId": "0",
            "signature": str(signed_message)
        }
        
        for attempt in range(5):
            try:
                response = requests.post(
                    url=CLAIM_API_URL,
                    headers=HTTP_HEADERS, 
                    json=data
                ).json()
                
                if 'error' in response:
                    if response['error'] == 'Address not found':
                        raise ValueError(f'{sender_address} is not eligible to claim the drop')
                    elif response['error'] == 'Invalid signature':
                        if attempt < 4:
                            print(Fore.YELLOW + f'{sender_address}: Invalid signature, retrying... ({attempt + 1}/5)')
                            continue
                        else:
                            raise ValueError(f'Failed after 5 attempts due to invalid signature')
                    else:
                        raise ValueError(f'Unexpected API error: {response.get("error")}')
                
                proof = response['claimData']['proof']
                allocation = response['claimData']['allocation']
                signature = response['claimData']['signature']
                return proof, allocation, signature
                
            except KeyError as e:
                if attempt == 4:
                    raise ValueError(f'Unexpected API response format: {str(e)}')
    
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