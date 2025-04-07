"""
Main processor service to handle the StakeStone airdrop claim and transfer workflow.
"""
from typing import List
from colorama import Fore, Style
from tqdm import tqdm
import re

from src.models.wallet import Wallet
from src.utils.network import create_web3_instance, check_proxy
from src.utils.input_handler import UserConfig, sleep_between_actions, sleep_between_accounts
from src.services.claim_service import ClaimService
from src.services.transfer_service import TransferService
from src.config.constants import BSC_RPC_URL


class Processor:
    """Main processor for the StakeStone workflow."""
    
    def __init__(self, config: UserConfig, claim_contract_abi: dict, sto_token_abi: dict):
        """
        Initialize the processor.
        
        Args:
            config: User configuration settings
            claim_contract_abi: ABI for the claim contract
            sto_token_abi: ABI for the STO token contract
        """
        self.config = config
        self.claim_contract_abi = claim_contract_abi
        self.sto_token_abi = sto_token_abi
    
    def process_wallet(self, wallet: Wallet) -> None:
        """
        Process a single wallet through the full workflow.
        
        Args:
            wallet: Wallet to process
        """
        try:
            print()
            # Check if private key is valid format
            if not re.match(r'^(0x)?[a-fA-F0-9]{64}$', wallet.private_key):
                print(Fore.RED + f'Invalid private key format: {wallet.get_hidden_key()}')
                return
                
            print(Style.BRIGHT + f'\nStart work with {wallet.address}')
            
            # Check and validate recipient address
            try:
                recipient_address = Web3().to_checksum_address(wallet.recipient_address)
            except Exception as e:
                print(Fore.RED + f'Invalid recipient address {wallet.recipient_address}. Error: {e}')
                return
                
            # Check proxy and create web3 instance
            proxy_url = check_proxy(wallet.proxy)
            web3 = create_web3_instance(BSC_RPC_URL, proxy_url)
            
            # Create services
            claim_service = ClaimService(web3, self.claim_contract_abi)
            transfer_service = TransferService(web3, self.sto_token_abi)
            
            # Execute claim
            claimed = claim_service.claim(wallet.address, wallet.private_key)
            
            # If claim successful, perform transfers
            if claimed:
                sleep_between_actions(self.config.min_action_delay, self.config.max_action_delay)
                transfer_service.transfer_sto(wallet.address, recipient_address, wallet.private_key)
                
                sleep_between_actions(self.config.min_action_delay, self.config.max_action_delay)
                transfer_service.transfer_native(wallet.address, recipient_address, wallet.private_key)
                
        except Exception as e:
            print(Fore.RED + f'Error processing wallet {wallet.address}: {str(e)}')
        finally:
            print(Style.BRIGHT + f'Finish work with {wallet.address}')
    
    def process_wallets(self, wallets: List[Wallet]) -> None:
        """
        Process all wallets.
        
        Args:
            wallets: List of wallets to process
        """
        print(f'\n{"=" * 100}')
        print(Style.BRIGHT + f'Found {len(wallets)} wallets to process')
        print('=' * 100)
        
        # Process each wallet
        for i, wallet in enumerate(tqdm(wallets, bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}", ncols=100)):
            self.process_wallet(wallet)
            
            # Sleep between accounts (except for the last one)
            if i < len(wallets) - 1:
                sleep_between_accounts(self.config.min_account_delay, self.config.max_account_delay)
        
        print(f'\n{"=" * 100}')
        print(Style.BRIGHT + f'Finished processing all {len(wallets)} wallets')
        print(f'{"=" * 100}\n') 