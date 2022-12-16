# store_top_ethereum_addresses
A python script to store ethereum address into database using Web3.py library.

In this python project, I have store ethereum addresses to PostgreSQL DB. I have filtered the addresses whose have a balance and transactions in Ethereum network.

### Requirements

* Python >= 3.1
* Python Libraries: `psycopg2` `web3`

### Steps to Follow

1. Install Python on your system and then install PIP For Python.
2. Install Python libraries using following commands:
    ```bash
    pip install web3
    pip install psycopg2
    ```
3. Create a new database named `ethereum_top_addresses` in PostgreSQL.
4. Create new table in 'ethereum_top_addresses' database by running following queries:
    ```sql
    CREATE SEQUENCE ethereum_address_id_seq;
    CREATE TABLE "public"."ethereum_address" (
    "id" int8 NOT NULL DEFAULT nextval('ethereum_address_id_seq'::regclass),
    "wallet_address" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
    "wallet_balance" numeric(40,18),
    "block_number" int8 NOT NULL,
    "updated_at" timestamptz(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "ethereum_address_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "ethereum_address_wallet_address_key" UNIQUE ("wallet_address")
    );
    ```
5. Save the block number you want to start from in the `block.txt` file.
6. In the store_top_ethereum_address.py file:
	update the node url.
	set db connection related variables - `db_host`, `db_port`, `db_name`, `db_user` and `db_pass`.
8. Run the script using `python store_top_ethereum_address.py`
9. To stop the script type: <kbd>Ctrl</kbd> + <kbd>C</kbd> or <kbd>Fn</kbd> + <kbd>Ctrl</kbd> + <kbd>B</kbd>
