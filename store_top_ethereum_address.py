import logging
import psycopg2
import sys
from web3 import Web3
from concurrent.futures import ThreadPoolExecutor


# Ethereum node
node = 'http://xxx.xxx.xxx.xxx:8545'
w3 = Web3(Web3.HTTPProvider(node))
db_host = "localhost"
db_port = 5432
db_name = "ethereum_top_addresses"
db_user = "postgres"
db_pass = "paSSwoRD"


# Database connection
db_conn = psycopg2.connect(
    host=db_host,
    port=db_port,
    database=db_name,
    user=db_user,
    password=db_pass
)
db_cursor = db_conn.cursor()


# Logger settings
log_file = "processing_log.log"
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)


# Method to insert batch data into db.
def push_records_to_db(queries: list):
    for q in queries:
        try:
            db_cursor.execute(query=q)
            db_conn.commit()
        except Exception as e:
            db_cursor.execute("ROLLBACK")
            db_conn.commit()

# Checking from and to address of each transaction of a block 
def parse_transaction_data(tx: dict) -> dict:
    values = []
    sql = '''INSERT INTO ethereum_address (wallet_address, wallet_balance, block_number) VALUES('{address}', {balance}, {last_block})'''

    # Processing from address data
    address_from = Web3.toChecksumAddress(tx['from'])
    balance_of_from = float(w3.eth.get_balance(address_from, 'latest')) / (10 ** 18)
    tx_count_of_from = w3.eth.get_transaction_count(address_from, 'latest')

    if tx_count_of_from >= 10 and balance_of_from >= 1:
        values.append(sql.format(address=address_from, balance=balance_of_from, last_block=tx['blockNumber']))

    # Processing to address data
    address_to = Web3.toChecksumAddress(tx['to'])
    balance_of_to = float(w3.eth.get_balance(address_to, 'latest')) / (10 ** 18)
    tx_count_of_to = w3.eth.get_transaction_count(address_to, 'latest')

    if tx_count_of_to >= 10 and balance_of_to >= 1:
        values.append(sql.format(address=address_to, balance=balance_of_to, last_block=tx['blockNumber']))

    if len(values) > 0:
        push_records_to_db(values)

# Fetch all transactions block by block
def fetch_wallet_address(limit: int = None) -> None:
    """
    This method fetches a block from ethereum chain and calls parse_transaction_data() 
    to process transaction.
    """
    previous_block = 0
    end = w3.eth.get_block_number()
    with open('block.txt', "r") as block_number_file:
        previous_block = int(block_number_file.read())
    current_block_number = previous_block

    if limit:
        end = current_block_number + (limit - 1)

    while (current_block_number <= end):
        try:
            block = w3.eth.get_block(
                block_identifier=current_block_number, full_transactions=True)
            if block:
                logging.info(
                    f"current_block: {current_block_number}, transactions: {len(block.transactions)}")
                txs = [tx for tx in block.transactions]
                worker = 10 if (len(txs) > 10) else len(txs)
                with ThreadPoolExecutor(max_workers=worker) as executor:
                    executor.map(parse_transaction_data, txs)
                    executor.shutdown(wait=True)
        except KeyboardInterrupt:
            sys.exit('Keyboard Interrupt to exit.')
        except Exception as e:
            print(str(e))
            logging.error(str(e))
        finally:
            current_block_number = current_block_number + 1
            block_number_file = open('block.txt', 'w')
            block_number_file.write(str(current_block_number))
            block_number_file.close()


if __name__ == "__main__":
    fetch_wallet_address()
