import hashlib
import json
import requests
from uuid import uuid4
from flask import Flask, jsonify, request
from time import time

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Criação do bloco gênese
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Limpa as transações atuais
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, complete_recipient, amount):
        """
        amount e complete_recipient agora são strings.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'complete_recipient': complete_recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_block):
        last_proof = last_block['proof']
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

app = Flask(__name__)

# Gera um endereço único para este nó
node_identifier = str(uuid4()).replace('-', '')

# Instancia a blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Recompensa pela mineração
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        complete_recipient="Miner Reward",
        amount="1",  # Agora em texto
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Novo Bloco Forjado",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Agora esperamos 4 campos, todos strings
    required = ['sender', 'recipient', 'complete_recipient', 'amount']
    if not all(k in values for k in required):
        return 'Valores ausentes no corpo da requisição', 400

    index = blockchain.new_transaction(
        values['sender'],
        values['recipient'],
        values['complete_recipient'],
        values['amount']
    )

    response = {'message': f'Transação será adicionada ao bloco {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    # Rode com: python nome_do_arquivo.py
    app.run(host='0.0.0.0', port=5000)
