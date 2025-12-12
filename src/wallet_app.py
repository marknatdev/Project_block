import cmd
from blockchain_core import generate_key_pair, sign_transaction, STATE_FILE, WALLET_FILE
import os
import json
import time

# --- Helper functions for Wallet state management ---
def load_wallet_state(filename=WALLET_FILE):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("❌ Error loading wallet state. The file might be corrupted.")
            return None
    return None

def save_wallet_state(wallet, filename=WALLET_FILE):
    if wallet:
        with open(filename, 'w') as f:
            json.dump(wallet, f, indent=4)

# --- CLI for Wallet App ---
class WalletCLI(cmd.Cmd):
    intro = ('\n<<< Decentralized Wallet CLI >>>\n'
             '------------------------------------------------------------------\n'
             'Use this app to manage your keys and send transactions.\n'
             'Type help or ? to list commands.')
    prompt = '(Wallet) > '
    
    def __init__(self):
        super().__init__()
        self.active_wallet = load_wallet_state()
        print("-" * 50)
        if self.active_wallet:
            print(f"💰 Active Wallet Loaded (Address: {self.active_wallet['address'][:10]}...)")
        else:
            print("💡 No active wallet found. Use 'new' to create one.")
        print("-" * 50)

    # --- Wallet Commands ---
    def do_new(self, arg):
        'Generate a new key pair and set it as active: new'
        private_key, address = generate_key_pair()
        self.active_wallet = {
            'private_key': private_key,
            'address': address
        }
        save_wallet_state(self.active_wallet)
        print("\n✅ New Wallet Created and Set as Active:")
        print(f"   Address: {address}")
        print(f"   Private Key: {private_key} (!!! KEEP THIS SECRET !!!)")
        
    def do_show(self, arg):
        'Display the active wallet address and private key: show'
        if self.active_wallet:
            print("\n⚠️ WARNING: Never show your private key in public!")
            print(f"   Address: {self.active_wallet['address']}")
            print(f"   Private Key: {self.active_wallet['private_key']}")
        else:
            print("❌ No active wallet. Use 'new' to create one.")


    # --- Transaction Command (Interacts with Server) ---
    def do_tx(self, arg):
        'Create and sign a transaction, then send it to the Server: tx <recipient_address> <data>'
        
        if not self.active_wallet:
            print("❌ Error: No active wallet found. Please use 'new' first.")
            return
            
        try:
            recipient, raw_data = arg.split(maxsplit=1)
            sender = self.active_wallet['address']
            private_key = self.active_wallet['private_key']
            
            # 1. Sign the Transaction (Wallet Responsibility)
            signed_transaction = sign_transaction(private_key, sender, recipient, raw_data)

            # 2. Send the Transaction to the Server (Mimicking API Call via File Access)
            
            # ต้องโหลดสถานะปัจจุบันของ Blockchain เพื่อเพิ่ม Transaction ลงใน pending_transactions
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r+') as f:
                    data = json.load(f)
                    data['pending_transactions'].append(signed_transaction)
                    
                    # รีเซ็ตตัวชี้ไฟล์และเขียนทับ
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                
                print(f"\n📧 Transaction successfully signed and broadcasted (written to {STATE_FILE}).")
                print(f"   > Sender (Active Wallet): {sender[:10]}...")
                print(f"   > Recipient: {recipient[:10]}...")
                print(f"   > Data: {raw_data}")
                print("\n💡 Now, switch to the **Server CLI** and run the 'mine' command to process it!")

            else:
                print(f"❌ Cannot connect to Server: {STATE_FILE} not found. Ensure Server CLI is running first.")
            
        except ValueError:
            print("❌ Invalid arguments. Usage: tx <recipient_address> <data>")
        except Exception as e:
            print(f"❌ An error occurred while sending transaction: {e}")

    def do_exit(self, arg):
        'Exit the Wallet CLI.'
        print('Wallet closing...')
        return True


if __name__ == '__main__':
    try:
        WalletCLI().cmdloop()
    except Exception as e:
        print(f"An error occurred: {e}")