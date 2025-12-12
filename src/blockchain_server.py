import cmd
from blockchain_core import Blockchain, STATE_FILE
import os
import json
import time

class ServerCLI(cmd.Cmd):
    intro = ('\n<<< Blockchain Server CLI >>>\n'
             '------------------------------------------------------------------\n'
             'Ready to receive transactions and mine blocks.\n'
             'Type help or ? to list commands.')
    prompt = '(Server) > '
    
    def __init__(self):
        super().__init__()
        self.blockchain = Blockchain()
        print(f"✅ Server Node ID: {self.blockchain.node_identifier[:10]}...")
        print(f"   Loaded {len(self.blockchain.chain)} blocks from state.")
        print("-" * 50)

    # --- Server Commands ---
    
    def do_mine(self, arg):
        'Run Proof-of-Work to create a new block from pending transactions.'
        print("\n⛏️ Starting Proof-of-Work...")
        # โหลด Transaction ที่ Wallet ส่งมาเข้าสู่ Pool ก่อน
        self.blockchain.load_state() 
        
        result = self.blockchain.mine()
        print(result)

    def do_chain(self, arg):
        'Display the full blockchain ledger.'
        self.blockchain.load_state() 
        print(self.blockchain.display_chain())

    def do_pending(self, arg):
        'Show current pending transactions waiting to be mined.'
        self.blockchain.load_state() 
        print("\n⏳ Pending Transactions:")
        if not self.blockchain.pending_transactions:
            print("   (None)")
            return
        for i, tx in enumerate(self.blockchain.pending_transactions):
            sender_id = tx['sender'][:10] + '...'
            recipient_id = tx['recipient'][:10] + '...'
            data_preview = tx['data'][:20] + '...'
            print(f"   [{i+1}] From: {sender_id} | To: {recipient_id} | Data: {data_preview}")

    def do_id(self, arg):
        'Show the current Server Node ID.'
        print(f"\n🆔 Server Node ID: {self.blockchain.node_identifier}")

    def do_exit(self, arg):
        'Exit the Server CLI.'
        print('Server shutting down...')
        return True

if __name__ == '__main__':
    try:
        ServerCLI().cmdloop()
    except Exception as e:
        print(f"An error occurred: {e}")