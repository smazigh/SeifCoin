import hashlib
import json
from time import time
# from textwrap import dedent
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request
import sys


port = int(sys.argv[1])

class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # create a genesis block
        self.new_block(previous_hash=1, proof=15454124)

    def new_block(self, proof, previous_hash=None):
        """

            :param proof:
            :param previous_hash:
            :return:
            """
        # create a new block
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # add a new transaction
        """
            Creates a new transaction to go into the next mined block
            :param sender:
            :param recipient:
            :param amount:
            :return: The index of the block that will hold this transaction
            """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # hashes a block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # get the last block
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        start_time = time()
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        end_time = time()
        print("it took :", end_time-start_time, "seconds")
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:6] == "000000"

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        curr_index = 1
        while curr_index < len(chain):
            block = chain[curr_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n---------------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            curr_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length == max_length and self.valid_chain(chain):
                    last_block = chain[-1]
                    print(last_block['timestamp'])

                    if last_block['timestamp'] < blockchain.last_block['timestamp']:
                        max_length = length
                        new_chain = chain

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')
blockchain = BlockChain()
print(blockchain.chain)


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {

        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Please supply a list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': "new nodes added",
        'total_nodes': list(blockchain.nodes),
    }
    print(blockchain.nodes)
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain is no longer valid',
            'new_chain': blockchain.chain,
        }
    else:
        response = {
            'message': 'Our chain is still valid',
            'chain': blockchain.chain,
        }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
