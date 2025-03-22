from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import time

def get_rpc_connection():
    return AuthServiceProxy("http://admin:admin@127.0.0.1:18443")

def input_amount(max_amount: Decimal, address_C: str) -> Decimal:
    while True:
        try:
            amount = Decimal(input(f"\nEnter the amount to send from B to C (max {max_amount} BTC): "))
            if amount <= Decimal('0'):
                print("Error: Amount must be greater than 0.")
            elif amount > max_amount:
                print(f"Error: Amount cannot exceed {max_amount} BTC.")
            else:
                return amount
        except InvalidOperation:
            print("Error: Invalid amount. Please enter a numeric value.")

def main():
    wallet = "Synergy_Legacy"
    try:
        conn = get_rpc_connection()
        loaded_wallets = conn.listwallets()
        if wallet not in loaded_wallets:
            conn.loadwallet(wallet)
            print(f"Loaded wallet: {wallet}")
        else:
            print(f"Wallet '{wallet}' is already loaded.")

        conn = get_rpc_connection()  
        address_B = conn.getaddressesbylabel("B")
        address_C = conn.getaddressesbylabel("C")

        if address_B:
            address_B = list(address_B.keys())[0]
        else:
            address_B = conn.getnewaddress("B", "legacy")

        if address_C:
            address_C = list(address_C.keys())[0]
        else:
            address_C = conn.getnewaddress("C", "legacy")

        print(f"\nAddress B: {address_B}\nAddress C: {address_C}")

        conn = get_rpc_connection() 
        print("\nFetching the UTXO list ...")
        utxo_B = conn.listunspent(0, 9999999, [address_B])
        if not utxo_B:
            print(f"No UTXO found for address B: {address_B}")
            return

        utxo_B = utxo_B[0]
        print(f"\nUTXO of B:\nTXID: {utxo_B['txid']}\nVout: {utxo_B['vout']}\nAmount: {utxo_B['amount']} BTC")

        fee = Decimal('0.0001')
        max_amount = utxo_B["amount"] - fee
        amount = input_amount(max_amount, address_C)

        conn = get_rpc_connection() 
        print("\nCreating the transaction from B to C ...")
        inputs = [{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}]
        outputs = {
            address_C: amount,
            address_B: utxo_B["amount"] - amount - fee
        }
        raw_tx = conn.createrawtransaction(inputs, outputs)
        print(f"\nUnsigned raw transaction hex: \n{raw_tx}")

        print("\nSigning the transaction B → C ...")
        signed_tx = conn.signrawtransactionwithwallet(raw_tx)
        print(f"\nSigned transaction hex: \n{signed_tx['hex']}")

        print("\nBroadcasting the transaction B → C ...")
        txid_B_to_C = conn.sendrawtransaction(signed_tx["hex"])
        tx_size = len(signed_tx["hex"]) // 2
        print(f"\nTransaction ID (B → C): {txid_B_to_C}")
        print(f"Transaction size: {tx_size} vbytes")

        conn = get_rpc_connection()  
        print("\nDecoding raw transaction to extract the response script ...")
        decoded_B_to_C = conn.decoderawtransaction(signed_tx["hex"])
        scriptSig = decoded_B_to_C["vin"][0]["scriptSig"]["hex"]
        scriptSig_size = len(scriptSig) // 2
        print(f"\nExtracted ScriptSig:\n{scriptSig}")
        print(f"Script size: {scriptSig_size} vbytes")

    except (JSONRPCException, ConnectionError) as e:
        print(f"Error: {e}. Retrying...")
        time.sleep(1)
        try:
            conn = get_rpc_connection()  
        except Exception as e:
            print(f"Fatal error: {e}")

    finally:
        try:
            conn = get_rpc_connection()
            conn.unloadwallet(wallet)
            print(f"\nUnloaded wallet: {wallet}")
        except Exception as e:
            print(f"Error unloading wallet: {e}")

if __name__ == "__main__":
    main()