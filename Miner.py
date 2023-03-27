import time
import requests
from web3 import Web3

# Set up web3 connection and contract instance
provider_url = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(provider_url))
contract_address = Web3.toChecksumAddress("YOUR_SMART_CONTRACT_ADDRESS")
contract_abi = "YOUR_SMART_CONTRACT_ABI"
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Your wallet address and private key
wallet_address = "YOUR_WALLET_ADDRESS"
wallet_private_key = "YOUR_WALLET_PRIVATE_KEY"

# Token addresses
token_a_address = Web3.toChecksumAddress("TOKEN_A_ADDRESS")
token_b_address = Web3.toChecksumAddress("TOKEN_B_ADDRESS")

# Define your monitoring parameters
min_profit = 100  # Minimum profit in tokenB units
gas_price = 5 * 10**9  # Gas price in Gwei

# PancakeSwap API URL
api_url = "https://api.pancakeswap.info/api/v2/tokens/"

def get_token_price(token_address):
    response = requests.get(api_url + token_address)
    data = response.json()
    return float(data["price"])

def get_arbitrage_opportunity(token_a, token_b):
    # Fetch prices from PancakeSwap API
    token_a_price = get_token_price(token_a)
    token_b_price = get_token_price(token_b)

    # Calculate the arbitrage opportunity, if any
    amount_in = 1
    amount_out = amount_in * token_a_price / token_b_price
    profit = amount_out - amount_in

    return amount_in, profit

while True:
    try:
        amount_in, profit = get_arbitrage_opportunity(token_a_address, token_b_address)

        if profit >= min_profit:
            # Estimate gas cost
            gas_estimate = contract.functions.mineMempool(token_a_address, token_b_address, amount_in, min_profit).estimateGas({"from": wallet_address})
            
            # Build and send the transaction
            transaction = contract.functions.mineMempool(token_a_address, token_b_address, amount_in, min_profit).buildTransaction({
                "from": wallet_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": web3.eth.getTransactionCount(wallet_address),
            })

            signed_transaction = web3.eth.account.signTransaction(transaction, wallet_private_key)
            transaction_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
            print(f"Arbitrage transaction sent: {transaction_hash.hex()}")

        time.sleep(60)  # Sleep for 1 minute before checking again

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
