from web3 import Web3
import json
import datetime
import time

# Get input from the user
http_provider = input("Enter http provider: ")
dex_address = input("Enter dex address: ")
receiver_address = input("Enter receiver address: ")
private_key = input("Enter private key: ")

# Get the contract addresses from the user
token_contract_address = '0xC4ed0A9Ea70d5bCC69f748547650d32cC219D882'
contract_address = '0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9'

# Connect to an Arbitrum node
w3 = Web3(Web3.HTTPProvider(http_provider))

# Load the contract ABI
with open('api.json', 'r') as f:
    contract_abi = json.load(f)
with open('api_token_arb.json', 'r') as f:
    contract_token_abi = json.load(f)

# Create contract objects
token_contract = w3.eth.contract(address=token_contract_address, abi=contract_token_abi)
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set up the transaction parameters
gas_price = w3.to_wei('0.1', 'gwei')
gas_limit = 600000

# Get the current time and the allotted time
allotted_time = datetime.datetime(2023, 3, 23, 14, 0, 0, 0)
current_time = datetime.datetime.utcnow()
print(f'Время сейчас: {current_time}')

# Sleep the program until the allotted time is reached
if current_time < allotted_time:
    print(f'Запустится через {(allotted_time - current_time).total_seconds()}с. +- пару секунд')
if current_time < allotted_time:
    time.sleep((allotted_time - current_time).total_seconds())

# Get the current nonce for the receiver address
nonce = w3.eth.get_transaction_count(receiver_address)

# Build the transaction
transaction = contract.functions.claim().build_transaction({
    'nonce': nonce,
    'gasPrice': gas_price,
    'gas': gas_limit,
})

# Sign the transaction with the receiver's private key
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

print(f'Время сейчас: {current_time}')

# Send the transaction to the network
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Wait for the transaction to be mined
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Check if the transaction was successful
if receipt['status'] == 1:
    # Get the amount of tokens claimed
    claimed_tokens = token_contract.functions.balanceOf(receiver_address).call()
    print(f'{claimed_tokens} tokens were successfully claimed to {receiver_address}.')

    # Set up the transaction parameters for sending tokens
    token_amount = claimed_tokens
    token_transaction = token_contract.functions.transfer(dex_address, token_amount).build_transaction({
        'nonce': nonce + 1,
        'gasPrice': gas_price,
        'gas': gas_limit,
    })

    # Sign the transaction with the receiver's private key
    token_signed_txn = w3.eth.account.sign_transaction(token_transaction, private_key=private_key)

    # Send the token transaction to the network
    token_tx_hash = w3.eth.send_raw_transaction(token_signed_txn.rawTransaction)

    # Wait for the token transaction to be mined
    token_receipt = w3.eth.wait_for_transaction_receipt(token_tx_hash)

    # Check if the token transaction was successful
    if token_receipt['status'] == 1:
        print(f'{token_amount} tokens were successfully sent to {dex_address}.')
    else:
        print(f'Failed to send {token_amount} tokens to {dex_address}.')