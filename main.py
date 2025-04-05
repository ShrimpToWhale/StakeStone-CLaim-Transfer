from web3 import Web3, HTTPProvider
from web3.exceptions import TimeExhausted
from eth_account.messages import encode_defunct
import requests
import json
import time
import random
import re
from tqdm import tqdm
from constants import bsc_rpc_url, bsc_explorer_url, STO_address, claim_address, headers, claim_url
from colorama import Fore, Style, init
init(autoreset=True)

# чтение ABI из файлов
with open('./global_data/STO_TOKEN_ABI.json', 'r', encoding='UTF-8') as file:
    STO_TOKEN_ABI = json.load(file)
with open('./global_data/STO_CLAIM_ABI.json', 'r', encoding='UTF-8') as file:
    STO_CLAIM_ABI = json.load(file)

# инициализвация переменных
w3 = Web3(HTTPProvider(endpoint_uri=bsc_rpc_url))
sto_contract = w3.eth.contract(address=w3.to_checksum_address(STO_address), abi=STO_TOKEN_ABI)
claim_contract = w3.eth.contract(address=w3.to_checksum_address(claim_address), abi=STO_CLAIM_ABI)

# запрос задержек у пользователя
def user_delays_input():
    while True:
        try:
            min_account_delay = int(input('Enter minimum delay between wallets: '))
            max_account_delay = int(input('Enter maximum delay between wallets: '))
            min_action_delay = int(input('Enter minimum delay between actions: '))
            max_action_delay = int(input('Enter maximum delay between actions: '))
            if (max_account_delay > min_account_delay) & (max_action_delay > min_action_delay):
                return min_account_delay, max_account_delay, min_action_delay, max_action_delay
            else:
                print(Fore.RED + f'Maximum delay must be greater than minimum')
        except ValueError:
            print(Fore.RED + f'The value you entered is not an integer digit')


def user_shuffle_input():
    while True:
        shuffle = input('Do you want to shuffle wallets (y/n)? ')
        if shuffle != 'y' and shuffle != 'n':
            print(Fore.RED + 'You entered incorrect answer')
        else:
            if shuffle == 'y':
                return True
            else:
                return False

# проверка корректности подключения к РПС сеть BSC
def check_connection():
    connected = w3.is_connected()
    if not connected:
        raise Exception(Fore.RED + 'Invalid RPC URL')

# чтение файла и формирование списка
def read_file(file_name):
    try:
        with open(f'./user_data/{file_name}.txt', 'r', encoding='UTF-8') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        raise Exception(Fore.RED + f'"{file_name}.txt" file or directory not found')
    
# проверка соответствия длины всех файлов из пользовательсткой информацией
def check_files_length(privates_list, proxies_list, recipients_list):
    if len(privates_list) == len(proxies_list) == len(recipients_list):
        print(Style.BRIGHT + f'Found {len(privates_list)} private keys, proxies and recipient addresses')
    else:
        raise Exception(Fore.RED + "The number of private keys, proxies, and recipient addresses must be the same")

# проверка корректности приватного ключа и извлечение публичного ключа
def address_extract(private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        address = account.address
        return address
    except Exception as e:
        hidden_key = private_key[:10]
        print(Fore.RED + f'Invalid private key {hidden_key}*****. Error: {e}')
        raise

# проверка работоспособности прокси
def check_proxy(proxy):
    try:
        response = requests.get('https://httpbin.org/ip', proxies={
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'}, timeout=10)
        if response.status_code != 200:
            print(Fore.YELLOW + f'Proxy {proxy} returned status: {response.status_code}, continue without it')
            return None
        else:
            return f'http://{proxy}'
    except Exception as e:
        print(Fore.YELLOW + f'Proxy {proxy} connection failed, continue without it')
        return None

# проверка корректности адреса получателя и приведение его к чексум формату
def check_address(address):
    try:
        return w3.to_checksum_address(address)
    except Exception as e:
        print(Fore.RED + f'Invalid recipient address {address}. Error: {e}')
        raise


def claim(w3, sender_address, sender_private_key):
    message = encode_defunct(text= f' I hereby authorize this message as confirmation of ownership for the wallet address: {sender_address}. By signing, I acknowledge that I have read and accepted the Airdrop Terms of Service and Privacy Policy. The SHA-256 hash of the referenced terms and policy is: 0x676b7efc9a6eb2e90331c7c06a27499ffbcfcce4a16f3414080ad8ffc5da6b20')
    signed_message = ((w3.eth.account.sign_message(message, sender_private_key)).signature).hex()
    proof, allocation, signature = get_claim_data(sender_address, signed_message)

    transaction = {
        'chainId': w3.eth.chain_id,
        'nonce': w3.eth.get_transaction_count(sender_address),
        'from': sender_address,
        'gasPrice': w3.to_wei('1', 'gwei'),
        'value': w3.to_wei('0.000830371674361444', 'ether')}

    try:
        transaction = claim_contract.functions.claim(proof, signature, int(allocation) * 10**18, sender_address).build_transaction(transaction)
        transaction['gas'] = w3.eth.estimate_gas(transaction)
    except Exception as e:
        if '0x646cf558' in str(e):
            print(Fore.YELLOW + f'{sender_address}: already claimed the airdrop')
            return True
        elif 'insufficient funds for transfer' in str(e):
            print(Fore.RED + f'{sender_address}: insufficient funds for claim')
            return False

        else:
            print(Fore.RED + f'{sender_address}: some custom error diring creating claim transaction. Error: {e}')
            return False

    sign_and_send_transaction(w3, 'Claim', transaction, sender_private_key)
    return True

# апи запрос для получения proof, размера аллокации и подписи
def get_claim_data(sender_address, signed_message):
    data = {
    "walletAddress": sender_address,
    "batchId": "0",
    "signature": str(signed_message)
}   
    for attempt in range(5):
        try:
            response = (requests.post(url=claim_url,headers=headers, json=data)).json()
            proof = response['claimData']['proof']
            allocation = response['claimData']['allocation']
            signature = response['claimData']['signature']
            return proof, allocation, signature

        except KeyError as e:
            if response['error'] == 'Address not found':
                print(Fore.RED + f'{sender_address} is not eligible to claim the drop')
                raise

            elif response['error'] == 'Invalid signature':
                print(Fore.RED + f'{sender_address}: Invalid signature, retrying... ({attempt + 1}/5)')
                if attempt == 4:
                   print(Fore.RED + f'{sender_address}: Failed after 3 attempts due to invalid signature')
                time.sleep(2)

            else:
                print(Fore.RED + f'Unexpected response from server: {e}')
                raise


# универсальная подпись и отправка транзакции
def sign_and_send_transaction(w3, type, transaction, sender_private_key):
    try:
        raw_transaction = w3.eth.account.sign_transaction(transaction, sender_private_key)
        transaction_hash = w3.eth.send_raw_transaction(raw_transaction.rawTransaction)
        print(f'{type} transaction sent, it will take up to 2 minutes to confirm it')
        wait_transaction_confiration(type, transaction_hash)
    except Exception as e:
        print(Fore.RED + f'{(w3.eth.account.from_key).address}: unexpected error occured during signing or sending {type.lower()} transaction. Error: {e}')
        raise

# универсальное ожидание результата транзакции
def wait_transaction_confiration(type, transaction_hash):
    try:
        receipt = w3.eth.wait_for_transaction_receipt(transaction_hash,timeout=120,poll_latency=10)
        if receipt['status'] == 1:
            print(Fore.GREEN + f'Successfull {type.lower()} transaction: {bsc_explorer_url}tx/{transaction_hash.hex()}')
        else:
            print(Fore.RED + f'{type} transaction failed: {bsc_explorer_url}tx/{transaction_hash.hex()}')
            raise
    except TimeExhausted:
        print(Fore.RED + f'{type} transaction was not confirmed within 120 seconds')
        raise
    except Exception as e:
        print(Fore.RED + f'Unexpected error while waiting for confirmation of {type.lower()} transaction: {e}')
        raise

# отправка токенов StakeStone на адрес получателя
def transfer_sto(w3, sender_address, recipient_address, sender_private_key):
    token_balance = sto_contract.functions.balanceOf(sender_address).call()
    if token_balance == 0:
        print(Fore.RED + f'Insufficient token balance to transfer, {sender_address}: {token_balance} STO')
    else:
        transaction = {
        'chainId': w3.eth.chain_id,
        'nonce': w3.eth.get_transaction_count(sender_address),
        'from': sender_address,
        'gasPrice': w3.to_wei('1', 'gwei'),
        }
        transaction['gas'] = w3.eth.estimate_gas(transaction)
        transaction = sto_contract.functions.transfer(recipient_address, token_balance).build_transaction(transaction)
        sign_and_send_transaction(w3, 'Transfer STO', transaction, sender_private_key)

# получение баланса нативного токена BNB
def get_native_balance(w3, sender_address):
    return w3.eth.get_balance(sender_address)

# отправка нативного токена BNB на адрес получателя
def transfer_native(w3, sender_address, recipient_address, sender_private_key):
    transaction = {
    'chainId': w3.eth.chain_id,
    'nonce': w3.eth.get_transaction_count(sender_address),
    'from': sender_address,
    'gasPrice': w3.to_wei('1', 'gwei'),
}
    transaction['to'] = recipient_address
    transaction['gas'] = w3.eth.estimate_gas(transaction)
    transaction['value'] = int(get_native_balance(w3, sender_address) - (transaction['gas'] * transaction['gasPrice'] * 1.5))

    sign_and_send_transaction(w3, 'Transfer BNB', transaction, sender_private_key)

# рандомная генерация задержек между аккаунтами
def sleep_between_actions(min_delay, max_delay):
    delay = random.randint(min_delay, max_delay)
    print(f'Sleep for {delay} seconds between actions')
    time.sleep(delay)

# рандомная генерация задержек между аккаунтами
def sleep_between_accounts(min_delay, max_delay):
    delay = random.randint(min_delay, max_delay)
    print(f'Sleep for {delay} seconds between accounts')
    time.sleep(delay)


def main():
    min_account_delay, max_account_delay, min_action_delay, max_action_delay = user_delays_input()
    shuffle = user_shuffle_input()
    check_connection()

    # формирование списков приватных ключей, прокси и адресов получателя
    privates_list = read_file('wallets')
    proxies_list = read_file('proxies')
    recipients_list = read_file('recipients')

    print(f'\n{"=" * 100}')
    check_files_length(privates_list, proxies_list, recipients_list)
    print('=' * 100)

    # формирование двух словарей с приватным ключом в качестве ключа и прокси/адреса депозита в качестве значения соответственно
    privates_proxies_list = dict(zip(privates_list, proxies_list))
    privates_recipients_list = dict(zip(privates_list, recipients_list))

    if shuffle:
        shuffled_pairs = list(privates_proxies_list.items())
        random.shuffle(shuffled_pairs)
        privates_proxies_list = dict(shuffled_pairs)

    for private_key, proxy in tqdm(privates_proxies_list.items(), bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}", ncols=100):
        print()
        try:
            if not re.match(r'^(0x)?[a-fA-F0-9]{64}$', private_key):
                sender_address = f'{private_key[:10]}*****'
            sender_address = address_extract(private_key)
            print(Style.BRIGHT + f'\nStart work with {sender_address}')
            recipient_address = check_address(privates_recipients_list[private_key])
            proxy = check_proxy(proxy)

            # инициализация переменной w3 с использованием прокси
            w3 = Web3(HTTPProvider(
                bsc_rpc_url,
                request_kwargs={'proxies': {'http': proxy,'https': proxy}}))
            
            claimed = claim(w3,sender_address, private_key)
            if claimed:
                sleep_between_actions(min_action_delay, max_action_delay)
                transfer_sto(w3, sender_address, recipient_address, private_key)
                sleep_between_actions(min_action_delay, max_action_delay)
                transfer_native(w3, sender_address, recipient_address, private_key)
        except Exception as e:
            continue
        finally:
            print(Style.BRIGHT + f'Finish work with {sender_address}')
            sleep_between_accounts(min_account_delay, max_account_delay)

    print(f'\n{"=" * 100}')
    print(Style.BRIGHT + f'Finish work with all {len(proxies_list)} wallets')
    print(f'{'=' * 100}\n')

if __name__ == '__main__':        
    main()