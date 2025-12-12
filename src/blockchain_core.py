import hashlib
import time
import json
from uuid import uuid4
import os
import base64

# ชื่อไฟล์สำหรับจัดเก็บสถานะ
STATE_FILE = 'blockchain_state.json'
WALLET_FILE = 'wallet_state.json'

def generate_key_pair():
    """สร้าง Private Key และ Public Address (จำลอง)"""
    # Private Key: สุ่ม UUID
    private_key = str(uuid4()).replace('-', '')
    # Public Address: Hash ของ Private Key (จำลองการสร้าง Address)
    public_address = f"0x{hashlib.sha256(private_key.encode()).hexdigest()[:40]}"
    return private_key, public_address

def sign_transaction(private_key, sender, recipient, raw_data):
    """จำลองการเซ็นต์ Transaction ด้วย Private Key"""
    # ในโลกจริง: ใช้ ECDSA เพื่อเซ็นต์
    # ในการจำลอง: ใช้ Private Key เป็น Salt ในการ Hash ข้อมูลเพื่อสร้าง Signature
    payload = f"{sender}|{recipient}|{raw_data}"
    signature = hashlib.sha256((payload + private_key).encode()).hexdigest()
    
    # Payload ที่ถูกเซ็นต์แล้ว
    return {
        'sender': sender,
        'recipient': recipient,
        'data': raw_data,
        'signature': signature,
        'timestamp': time.time()
    }

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = 2
        self.mining_reward = 10 
        self.node_identifier = str(uuid4()).replace('-', '')
        self.load_state() 
        if not self.chain:
            print("Creating Genesis Block...")
            self.create_block(previous_hash='0', nonce=0)

    # ฟังก์ชันหลัก (hash, proof_of_work, save_state, load_state, create_block, get_last_block)
    # ... (ตรรกะ Blockchain เหมือนเดิม) ...

    def create_block(self, previous_hash, nonce):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.pending_transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }
        self.pending_transactions = []
        self.chain.append(block)
        self.save_state()
        return block

    def get_last_block(self):
        return self.chain[-1]

    def hash(self, block):
        block_copy = block.copy()
        # ต้องจัดการ Transactions ที่เป็น dict/list ก่อน hash
        block_copy['transactions'] = json.dumps(block_copy['transactions'], sort_keys=True) 
        encoded_block = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, last_block):
        last_hash = self.hash(last_block)
        nonce = 0
        target_prefix = '0' * self.difficulty
        
        while self.hash({'index': last_block['index']+1, 'transactions': self.pending_transactions, 'nonce': nonce, 'previous_hash': last_hash})[:self.difficulty] != target_prefix:
            nonce += 1
        return nonce

    def add_transaction(self, transaction):
        """เพิ่ม transaction ที่ถูกเซ็นต์แล้ว (จาก Wallet) เข้าสู่ Pool"""
        if transaction.get('sender') and transaction.get('recipient') and transaction.get('signature'):
            self.pending_transactions.append(transaction)
            self.save_state()
            return self.get_last_block()['index'] + 1
        return -1 # Invalid transaction

    def mine(self):
        if not self.pending_transactions:
            return "❌ Cannot mine: No pending transactions to include in the new block."
            
        last_block = self.get_last_block()
        nonce = self.proof_of_work(last_block)
        
        reward_tx = {
            'sender': "THE_NETWORK",
            'recipient': self.node_identifier,
            'data': f"MINING_REWARD_{self.mining_reward}_TOKEN",
            'signature': 'SYSTEM_SIGNATURE',
            'timestamp': time.time()
        }
        self.pending_transactions.insert(0, reward_tx) 

        previous_hash = self.hash(last_block)
        block = self.create_block(previous_hash, nonce)
        
        return (f"✅ Block successfully forged! Index: {block['index']} | Hash: {self.hash(block)[:10]}... "
                f"| Reward ({self.mining_reward}) sent to {self.node_identifier[:10]}...")
            
    def save_state(self, filename=STATE_FILE):
        data = {
            'chain': self.chain,
            'pending_transactions': self.pending_transactions,
            'node_identifier': self.node_identifier
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_state(self, filename=STATE_FILE):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    self.chain = data.get('chain', [])
                    self.pending_transactions = data.get('pending_transactions', [])
                    self.node_identifier = data.get('node_identifier', self.node_identifier)
            except json.JSONDecodeError:
                pass # State file is corrupt, start fresh

    def display_chain(self):
        output = ["\n📜 Full Blockchain Ledger:"]
        if len(self.chain) == 1:
            output.append("   (Only Genesis Block exists)")
        for block in self.chain:
            output.append("--- Block #{} ---".format(block['index']))
            output.append("Timestamp: {}".format(time.ctime(block['timestamp'])))
            output.append("Nonce: {}".format(block['nonce']))
            output.append("Prev. Hash: {}".format(block['previous_hash'][:10] + '...'))
            output.append("Current Hash: {}".format(self.hash(block)[:10] + '...'))
            output.append("Transactions ({} total):".format(len(block['transactions'])))
            for tx in block['transactions']:
                if 'sender' in tx:
                    data_display = tx['data'][:20] + ('...' if len(tx['data']) > 20 else '')
                    output.append(f"  - From: {tx['sender'][:6]}.. To: {tx['recipient'][:6]}.. Data: {data_display}")
            output.append("-------------------------")
        return "\n".join(output)