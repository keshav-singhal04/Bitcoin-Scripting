from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import time

def get_rpc_connection():
    return AuthServiceProxy("http://admin:admin@127.0.0.1:18443")

def input_amount(max_amount: Decimal, address_B: str) -> Decimal:
    while True:
        try:
            amount = Decimal(input(f"\nEnter the amount to send from A to B (max {max_amount} BTC): "))
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
        try:
            conn.loadwallet(wallet)
            print(f"Loaded wallet: {wallet}")
        except JSONRPCException:
            conn.createwallet(wallet)
            print(f"Created wallet: {wallet}")

        conn = get_rpc_connection()
        address_A = conn.getnewaddress("A", "legacy")
        address_B = conn.getnewaddress("B", "legacy")
        address_C = conn.getnewaddress("C", "legacy")
        print(f"\nLegacy Addresses:\nA: {address_A}\nB: {address_B}\nC: {address_C}")

        print("\nMining some initial blocks to fund address A ...\n")
        conn.generatetoaddress(101, address_A)
        print(f"Balance of A: {conn.getbalance()} BTC")

        conn = get_rpc_connection()
        utxo_A = conn.listunspent(1, 9999999, [address_A])[0]
        print(f"UTXO of A: {utxo_A['amount']} BTC")

        fee = Decimal('0.0001')
        max_amount = utxo_A["amount"] - fee
        amount = input_amount(max_amount, address_B)

        print("\nCreating a raw transaction from A to B ...")
        conn = get_rpc_connection()
        inputs = [{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}]
        outputs = {
            address_B: amount,
            address_A: utxo_A["amount"] - amount - fee
        }
        raw_tx = conn.createrawtransaction(inputs, outputs)
        print(f"\nUnsigned raw transaction hex: \n{raw_tx}")

        print("\nDecoding raw transaction to extract the challenge script ... ")
        decoded_tx = conn.decoderawtransaction(raw_tx)
        scriptPubKey = decoded_tx["vout"][0]["scriptPubKey"]["hex"]
        script_size = len(scriptPubKey) // 2
        print(f"\nExtracted ScriptPubKey: {scriptPubKey}")
        print(f"Script size: {script_size} vbytes")

        print("\nSigning the transaction A → B ...")
        signed_tx = conn.signrawtransactionwithwallet(raw_tx)
        print(f"\nSigned transaction hex: \n{signed_tx['hex']}")

        print("\nBroadcasting the transaction A → B ...")
        txid_A_to_B = conn.sendrawtransaction(signed_tx["hex"])
        tx_size = len(signed_tx["hex"]) // 2
        print(f"\nTransaction ID (A → B): {txid_A_to_B}")
        print(f"Transaction size: {tx_size} vbytes")

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