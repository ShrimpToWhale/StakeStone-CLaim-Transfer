"""
Wallet model to encapsulate wallet information and operations.
"""
from dataclasses import dataclass
from web3 import Web3


@dataclass
class Wallet:
    """Class representing a wallet with its private key and corresponding details."""
    private_key: str
    proxy: str = None
    recipient_address: str = None
    _address: str = None
    
    @property
    def address(self) -> str:
        """Get the wallet address from the private key."""
        if not self._address:
            try:
                w3 = Web3()
                account = w3.eth.account.from_key(self.private_key)
                self._address = account.address
            except Exception as e:
                raise ValueError(f"Invalid private key. Error: {e}")
        return self._address
    
    @property
    def checksum_address(self) -> str:
        """Get the checksum address."""
        return Web3().to_checksum_address(self.address)
    
    def get_hidden_key(self) -> str:
        """Return a hidden version of the private key for display."""
        return f"{self.private_key[:10]}*****"
    
    def __repr__(self) -> str:
        """String representation of the wallet."""
        return f"Wallet(address={self.address}, recipient={self.recipient_address})" 