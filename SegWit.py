from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import os
import shutil

def get_rpc_connection(wallet_name: str = None):
    base_url = "http://admin:admin@127.0.0.1:18443"
    if wallet_name:
        return AuthServiceProxy(f"{base_url}/wallet/{wallet_name}")
    return AuthServiceProxy(base_url)

def input_amount(max_amount: Decimal, recipient: str) -> Decimal:
    while True:
        try:
            amount = Decimal(input(f"\nEnter the amount to send from {recipient[0]} to {recipient[1]} (max {max_amount} BTC): "))
            if amount <= Decimal('0'):
                print("Error: Amount must be greater than 0.")
            elif amount > max_amount:
                print(f"Error: Amount cannot exceed {max_amount} BTC.")
            else:
                return amount
        except InvalidOperation:
            print("Error: Invalid amount. Please enter a numeric value.")

def main():
    wallet = "Synergy_SegWit"
    root_conn = get_rpc_connection()
    
    try:
        if wallet in root_conn.listwallets():
            root_conn.loadwallet(wallet)
            print(f"Loaded wallet: {wallet}")
        else:
            root_conn.createwallet(wallet)
            print(f"Created wallet: {wallet}")

        conn = get_rpc_connection(wallet)
        address_A = conn.getnewaddress("A", "p2sh-segwit")
        address_B = conn.getnewaddress("B", "p2sh-segwit")
        address_C = conn.getnewaddress("C", "p2sh-segwit")
        print(f"\nSegWit Addresses:\nA: {address_A}\nB: {address_B}\nC: {address_C}")

        print("\nMining some initial blocks to fund address A ...")
        get_rpc_connection(wallet).generatetoaddress(101, address_A)
        
        conn = get_rpc_connection(wallet)
        utxo_A = conn.listunspent(1, 9999999, [address_A])[0]
        print(f"\nBalance of A: {conn.getbalance()} BTC")
        print(f"UTXO of A: {utxo_A['amount']} BTC")

        fee = Decimal('0.0001')
        max_amount = utxo_A["amount"] - fee
        amount = input_amount(max_amount, ("A", "B"))

        print("\nCreating a raw transaction from A to B ...")
        conn = get_rpc_connection(wallet)
        inputs = [{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}]
        outputs = {address_B: amount, address_A: utxo_A["amount"] - amount - fee}
        raw_tx_AB = conn.createrawtransaction(inputs, outputs)
        print(f"\nUnsigned raw transaction hex: \n{raw_tx_AB}")

        print("\nDecoding the transaction A → B to extract challenge script ...")
        conn = get_rpc_connection(wallet)
        decoded_AB = conn.decoderawtransaction(raw_tx_AB)
        scriptPubKey_B = decoded_AB["vout"][0]["scriptPubKey"]["hex"]
        script_size = len(scriptPubKey_B) // 2
        print(f"\nExtracted ScriptPubKey: {scriptPubKey_B}")
        print(f"Script size: {script_size} vbytes")

        print("\nSigning the transaction A → B ...")
        conn = get_rpc_connection(wallet)
        signed_AB = conn.signrawtransactionwithwallet(raw_tx_AB)
        print(f"\nSigned transaction hex: \n{signed_AB['hex']}")

        print("\nBrodcasting the transaction A → B ...")
        conn = get_rpc_connection(wallet)
        txid_AB = conn.sendrawtransaction(signed_AB["hex"])
        decoded_signed_AB = conn.decoderawtransaction(signed_AB["hex"], True)
        tx_vsize = decoded_signed_AB["vsize"]
        print(f"\nTransaction ID (A → B): {txid_AB}")
        print(f"Transaction size: {tx_vsize} vbytes")
        
        get_rpc_connection(wallet).generatetoaddress(1, address_A)

        print("\nFetching the UTXO list  ...")
        conn = get_rpc_connection(wallet)
        utxo_B = conn.listunspent(1, 9999999, [address_B])[0]
        print(f"\nUTXO of B:\nTXID: {utxo_B['txid']}\nVout: {utxo_B['vout']}\nAmount: {utxo_B['amount']} BTC")

        max_amount = utxo_B["amount"] - fee
        amount = input_amount(max_amount, ("B", "C"))

        print("\nCreating the transacation from B to C ...")
        conn = get_rpc_connection(wallet)
        inputs = [{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}]
        outputs = {address_C: amount, address_B: utxo_B["amount"] - amount - fee}
        raw_tx_BC = conn.createrawtransaction(inputs, outputs)
        print(f"\nUnsigned raw transaction hex: \n{raw_tx_BC}")

        print("\nSigning the transaction B → C ...")
        conn = get_rpc_connection(wallet)
        signed_BC = conn.signrawtransactionwithwallet(raw_tx_BC)
        print(f"\nSigned transaction hex: \n{signed_BC['hex']}")

        print("\nBrodcasting the transaction B → C ...")
        conn = get_rpc_connection(wallet)
        txid_BC = conn.sendrawtransaction(signed_BC["hex"])
        decoded_signed_BC = conn.decoderawtransaction(signed_BC["hex"], True)
        tx_vsize = decoded_signed_BC["vsize"]
        print(f"\nTransaction ID (B → C): {txid_BC}")
        print(f"Transaction size: {tx_vsize} vbytes")

        print("\nDecoding the transaction B → C to extract response script ...")
        conn = get_rpc_connection(wallet)
        decoded_BC_signed = conn.decoderawtransaction(signed_BC["hex"])
        scriptSig = decoded_BC_signed["vin"][0]["scriptSig"]["hex"]
        scriptSig_size = len(scriptSig) // 2
        print(f"\nExtracted ScriptSig: {scriptSig}")
        print(f"Script size: {scriptSig_size} vbytes")

    except JSONRPCException as e:
        print(f"Error: {e}")
    finally:
        try:
            root_conn.unloadwallet(wallet)
            print(f"\nUnloaded wallet: {wallet}")
            
            wallet_path = os.path.join(
                os.getenv('APPDATA'),
                'Bitcoin',
                'regtest',
                'wallets',
                wallet
            )
            if os.path.exists(wallet_path):
                shutil.rmtree(wallet_path)
        except:
            print()

if __name__ == "__main__":
    main()