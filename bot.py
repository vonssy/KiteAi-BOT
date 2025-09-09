from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_abi.abi import encode
from eth_utils import to_hex
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from http.cookies import SimpleCookie
from datetime import datetime, timezone
from colorama import *
import asyncio, binascii, random, json, re, os, pytz

load_dotenv()

wib = pytz.timezone('Asia/Jakarta')

class KiteAI:
    def __init__(self) -> None:
        self.auto_claim_faucet = str(os.getenv("AUTO_CLAIM_FAUCET", "FALSE")).strip().lower() == "true"
        self.auto_deposit_token = str(os.getenv("AUTO_DEPOSIT_TOKEN", "FALSE")).strip().lower() == "true"
        self.auto_withdraw_token = str(os.getenv("AUTO_WITHDRAW_TOKEN", "FALSE")).strip().lower() == "true"
        self.auto_unstake_token = str(os.getenv("AUTO_UNSTAKE_TOKEN", "FALSE")).strip().lower() == "true"
        self.auto_stake_token = str(os.getenv("AUTO_STAKE_TOKEN", "FALSE")).strip().lower() == "true"
        self.auto_claim_reward = str(os.getenv("AUTO_CLAIM_REWARD", "FALSE")).strip().lower() == "true"
        self.auto_daily_quiz = str(os.getenv("AUTO_DAILY_QUIZ", "FALSE")).strip().lower() == "true"
        self.auto_chat_ai_agent = str(os.getenv("AUTO_CHAT_AI_AGENT", "FALSE")).strip().lower() == "true"
        self.auto_create_multisig = str(os.getenv("AUTO_CREATE_MULTISIG", "FALSE")).strip().lower() == "true"
        self.auto_swap_token = str(os.getenv("AUTO_SWAP_TOKEN", "FALSE")).strip().lower() == "true"
        self.auto_bridge_token = str(os.getenv("AUTO_BRIDGE_TOKEN", "FALSE")).strip().lower() == "true"

        self.USDT_CONTRACT_ADDRESS = "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63"
        self.WKITE_CONTRACT_ADDRESS = "0x3bC8f037691Ce1d28c0bB224BD33563b49F99dE8"
        self.ZERO_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000000"
        self.SAFE_PROXY_FACTORY_ADDRESS = "0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2"
        self.GNOSIS_SAFE_L2_ADDRESS = "0x3E5c63644E683549055b9Be8653de26E0B4CD36E"
        self.FALLBACK_HANDLER_ADDRESS = "0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4"
        self.BRIDGE_ROUTER_ADDRESS = "0xD1bd49F60A6257dC96B3A040e6a1E17296A51375"
        self.SWAP_ROUTER_ADDRESS = "0x04CfcA82fDf5F4210BC90f06C44EF25Bf743D556"
        self.DEST_BLOCKCHAIN_ID = "0x6715950e0aad8a92efaade30bd427599e88c459c2d8e29ec350fc4bfb371a114"

        self.KITE_AI = {
            "name": "KITE AI",
            "rpc_url": "https://rpc-testnet.gokite.ai/",
            "explorer": "https://testnet.kitescan.ai/tx/",
            "tokens": [
                { "type": "native", "ticker": "KITE", "address": "0x0BBB7293c08dE4e62137a557BC40bc12FA1897d6" },
                { "type": "erc20", "ticker": "ETH", "address": "0x7AEFdb35EEaAD1A15E869a6Ce0409F26BFd31239" },
                { "type": "erc20", "ticker": "USDT", "address": self.USDT_CONTRACT_ADDRESS }
            ],
            "chain_id": 2368
        }

        self.BASE_SEPOLIA = {
            "name": "BASE SEPOLIA",
            "rpc_url": "https://base-sepolia-rpc.publicnode.com/",
            "explorer": "https://sepolia.basescan.org/tx/",
            "tokens": [
                { "type": "native", "ticker": "ETH", "address": "0x226D7950D4d304e749b0015Ccd3e2c7a4979bB7C" },
                { "type": "erc20", "ticker": "KITE", "address": "0xFB9a6AF5C014c32414b4a6e208a89904c6dAe266" },
                { "type": "erc20", "ticker": "USDT", "address": "0xdAD5b9eB32831D54b7f2D8c92ef4E2A68008989C" }
            ],
            "chain_id": 84532
        }

        self.NATIVE_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"send","stateMutability":"payable","inputs":[{"name":"_destChainId","type":"uint256"},{"name":"_recipient","type":"address"},{"name":"_amount","type":"uint256"}],"outputs":[]},
            {
                "type":"function",
                "name":"initiate",
                "stateMutability":"payable",
                "inputs":[
                    {"name":"token","type":"address","internalType":"address"}, 
                    {"name":"amount","type":"uint256","internalType":"uint256"}, 
                    { 
                        "name":"instructions", 
                        "type":"tuple", 
                        "internalType":"struct Instructions",
                        "components":[
                            {"name":"sourceId","type":"uint256","internalType":"uint256"}, 
                            {"name":"receiver","type":"address","internalType":"address"}, 
                            {"name":"payableReceiver","type":"bool","internalType":"bool"}, 
                            {"name":"rollbackReceiver","type":"address","internalType":"address"}, 
                            {"name":"rollbackTeleporterFee","type":"uint256","internalType":"uint256"}, 
                            {"name":"rollbackGasLimit","type":"uint256","internalType":"uint256"}, 
                            {
                                "name":"hops",
                                "type":"tuple[]",
                                "internalType":"struct Hop[]",
                                "components":[
                                    {"name":"action","type":"uint8","internalType":"enum Action"}, 
                                    {"name":"requiredGasLimit","type":"uint256","internalType":"uint256"}, 
                                    {"name":"recipientGasLimit","type":"uint256","internalType":"uint256"}, 
                                    {"name":"trade","type":"bytes","internalType":"bytes"}, 
                                    {
                                        "name":"bridgePath",
                                        "type":"tuple",
                                        "internalType":"struct BridgePath",
                                        "components":[
                                            {"name":"bridgeSourceChain","type":"address","internalType":"address"},
                                            {"name":"sourceBridgeIsNative","type":"bool","internalType":"bool"},
                                            {"name":"bridgeDestinationChain","type":"address","internalType":"address"},
                                            {"name":"cellDestinationChain","type":"address","internalType":"address"},
                                            {"name":"destinationBlockchainID","type":"bytes32","internalType":"bytes32"},
                                            {"name":"teleporterFee","type":"uint256","internalType":"uint256"},
                                            {"name":"secondaryTeleporterFee","type":"uint256","internalType":"uint256"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "outputs":[]
            }
        ]''')
        
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"send","stateMutability":"nonpayable","inputs":[{"name":"_destChainId","type":"uint256"},{"name":"_recipient","type":"address"},{"name":"_amount","type":"uint256"}],"outputs":[]},
            {
                "type":"function",
                "name":"createProxyWithNonce",
                "stateMutability":"nonpayable",
                "inputs":[
                    {"internalType":"address","name":"_singleton","type":"address"}, 
                    {"internalType":"bytes","name":"initializer","type":"bytes"}, 
                    {"internalType":"uint256","name":"saltNonce","type":"uint256"}
                ],
                "outputs": [
                    {"internalType":"contract GnosisSafeProxy","name":"proxy","type":"address"}
                ]
            },
            {
                "type":"function",
                "name":"initiate",
                "stateMutability":"nonpayable",
                "inputs":[
                    {"name":"token","type":"address","internalType":"address"}, 
                    {"name":"amount","type":"uint256","internalType":"uint256"}, 
                    { 
                        "name":"instructions", 
                        "type":"tuple", 
                        "internalType":"struct Instructions",
                        "components":[
                            {"name":"sourceId","type":"uint256","internalType":"uint256"}, 
                            {"name":"receiver","type":"address","internalType":"address"}, 
                            {"name":"payableReceiver","type":"bool","internalType":"bool"}, 
                            {"name":"rollbackReceiver","type":"address","internalType":"address"}, 
                            {"name":"rollbackTeleporterFee","type":"uint256","internalType":"uint256"}, 
                            {"name":"rollbackGasLimit","type":"uint256","internalType":"uint256"}, 
                            {
                                "name":"hops",
                                "type":"tuple[]",
                                "internalType":"struct Hop[]",
                                "components":[
                                    {"name":"action","type":"uint8","internalType":"enum Action"}, 
                                    {"name":"requiredGasLimit","type":"uint256","internalType":"uint256"}, 
                                    {"name":"recipientGasLimit","type":"uint256","internalType":"uint256"}, 
                                    {"name":"trade","type":"bytes","internalType":"bytes"}, 
                                    {
                                        "name":"bridgePath",
                                        "type":"tuple",
                                        "internalType":"struct BridgePath",
                                        "components":[
                                            {"name":"bridgeSourceChain","type":"address","internalType":"address"},
                                            {"name":"sourceBridgeIsNative","type":"bool","internalType":"bool"},
                                            {"name":"bridgeDestinationChain","type":"address","internalType":"address"},
                                            {"name":"cellDestinationChain","type":"address","internalType":"address"},
                                            {"name":"destinationBlockchainID","type":"bytes32","internalType":"bytes32"},
                                            {"name":"teleporterFee","type":"uint256","internalType":"uint256"},
                                            {"name":"secondaryTeleporterFee","type":"uint256","internalType":"uint256"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "outputs":[]
            }
        ]''')

        self.BITMIND_SUBNET = {
            "id": "702",
            "name": "Bitmind",
            "address": "0xda925c81137dd6e44891cdbd5e84bda3b4f81671"
        }

        self.VERONIKA_SUBNET = {
            "id": "699",
            "name": "AI Veronika",
            "address": "0xb20f6f7d85f657c8cb66a7ee80799cf40f1d3533"
        }

        self.KITE_SUBNET = {
            "id": "496",
            "name": "Kite AI Agents",
            "address": "0xb132001567650917d6bd695d1fab55db7986e9a5"
        }

        self.BITTE_SUBNET = {
            "id": "701",
            "name": "Bitte",
            "address": "0x72ce733c9974b180bed20343bd1024a3f855ec0c"
        }
        
        self.FAUCET_API = "https://faucet.gokite.ai"
        self.TESTNET_API = "https://testnet.gokite.ai"
        self.BRIDGE_API = "https://bridge-backend.prod.gokite.ai"
        self.NEO_API = "https://neo.prod.gokite.ai"
        self.OZONE_API = "https://ozone-point-system.prod.gokite.ai"
        self.MULTISIG_API = "https://wallet-client.ash.center/v1"
        self.FAUCET_SITE_KEY = "6LeNaK8qAAAAAHLuyTlCrZD_U1UoFLcCTLoa_69T"
        self.TESTNET_SITE_KEY = "6Lc_VwgrAAAAALtx_UtYQnW-cFg8EPDgJ8QVqkaz"
        self.CAPTCHA_KEY = None
        self.FAUCET_HEADERS = {}
        self.TESTNET_HEADERS = {}
        self.BRIDGE_HEADERS = {}
        self.MULTISIG_HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.auth_tokens = {}
        self.header_cookies = {}
        self.access_tokens = {}
        self.aa_address = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Kite AI Ozone {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_2captcha_key(self):
        try:
            with open("2captcha_key.txt", 'r') as file:
                captcha_key = file.read().strip()

            return captcha_key
        except Exception as e:
            return None
    
    def load_ai_agents(self):
        filename = "agents.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    def generate_auth_token(self, address):
        try:
            key_hex = "6a1c35292b7c5b769ff47d89a17e7bc4f0adfe1b462981d28e0e9f7ff20b8f8a"

            key = bytes.fromhex(key_hex)
            iv = os.urandom(12)

            encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()

            ciphertext = encryptor.update(address.encode()) + encryptor.finalize()
            auth_tag = encryptor.tag

            result = iv + ciphertext + auth_tag
            result_hex = binascii.hexlify(result).decode()

            return result_hex
        except Exception as e:
            return None
    
    def generate_quiz_title(self):
        today = datetime.today().strftime('%Y-%m-%d')
        return f"daily_quiz_{today}"
        
    def setup_ai_agent(self, agents: list):
        agent = random.choice(agents)

        agent_name = agent["agentName"]
        service_id = agent["serviceId"]
        question = random.choice(agent["questionLists"])

        return agent_name, service_id, question
        
    def generate_inference_payload(self, service_id: str, question: str):
        try:
            payload = {
                "service_id": service_id,
                "subnet": "kite_ai_labs",
                "stream": True,
                "body": {
                    "stream": True,
                    "message": question
                }
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Inference Payload Failed: {str(e)}")
        
    def generate_receipt_payload(self, address: str, service_id: str, question: str, answer: str):
        try:
            payload = {
                "address": address,
                "service_id": service_id,
                "input": [
                    { "type":"text/plain", "value":question }
                ],
                "output": [
                    { "type":"text/plain", "value":answer }
                ]
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Receipt Payload Failed: {str(e)}")
        
    def generate_bridge_payload(self, address: str, src_chain_id: int, dest_chain_id: int, src_token: str, dest_token: str, amount: int, tx_hash: str):
        try:
            now_utc = datetime.now(timezone.utc)
            timestamp = now_utc.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            payload = {
                "source_chain_id": src_chain_id,
                "target_chain_id": dest_chain_id,
                "source_token_address": src_token,
                "target_token_address": dest_token,
                "amount": str(amount),
                "source_address": address,
                "target_address": address,
                "tx_hash": tx_hash,
                "initiated_at": timestamp
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    def generate_swap_option(self):
        options = [
            ("native to erc20", "KITE to USDT", self.WKITE_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, "KITE", "native", self.kite_swap_amount),
            ("erc20 to native", "USDT to KITE", self.USDT_CONTRACT_ADDRESS, self.WKITE_CONTRACT_ADDRESS, "USDT", "erc20", self.usdt_swap_amount)
        ]

        swap_type, option, token_in, token_out, ticker, token_type, amount = random.choice(options)

        return swap_type, option, token_in, token_out, ticker, token_type, amount
        
    def generate_bridge_option(self):
        src_chain, dest_chain = random.choice([
            (self.KITE_AI, self.BASE_SEPOLIA),
            (self.BASE_SEPOLIA, self.KITE_AI)
        ])

        src_token = random.choice(src_chain["tokens"])

        dest_token = next(token for token in dest_chain["tokens"] if token["ticker"] == src_token["ticker"])

        if src_token["ticker"] == "KITE":
            amount = self.kite_bridge_amount

        elif src_token["ticker"] == "ETH":
            amount = self.eth_bridge_amount

        elif src_token["ticker"] == "USDT":
            amount = self.usdt_bridge_amount

        return {
            "option": f"{src_chain['name']} to {dest_chain['name']}",
            "rpc_url": src_chain["rpc_url"],
            "explorer": src_chain["explorer"],
            "src_chain_id": src_chain["chain_id"],
            "dest_chain_id": dest_chain["chain_id"],
            "src_token": src_token,
            "dest_token": dest_token,
            "amount": amount
        }
    
    async def get_web3_with_check(self, address: str, rpc_url: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, rpc_url: str, contract_address: str, token_type: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, rpc_url, use_proxy)

            if token_type == "native":
                balance = web3.eth.get_balance(address)
                decimals = 18
            else:
                token_contract = web3.eth.contract(
                    address=web3.to_checksum_address(contract_address),
                    abi=self.ERC20_CONTRACT_ABI
                )
                balance = token_contract.functions.balanceOf(address).call()
                decimals = token_contract.functions.decimals().call()

            token_balance = balance / (10 ** decimals)

            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Message : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
            )
            return None
        
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}] Send TX Error: {str(e)} {Style.RESET_ALL}"
                )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}] Wait for Receipt Error: {str(e)} {Style.RESET_ALL}"
                )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
    
    async def perform_deposit(self, account: str, address: str, receiver: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, self.KITE_AI['rpc_url'], use_proxy)

            amount_to_wei = web3.to_wei(self.deposit_amount, "ether")

            estimated_gas = web3.eth.estimate_gas({
                "from": address,
                "to": web3.to_checksum_address(receiver),
                "value": amount_to_wei
            })

            max_priority_fee = web3.to_wei(0.001, "gwei")
            max_fee = max_priority_fee

            tx = {
                "from": address,
                "to": web3.to_checksum_address(receiver),
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            }

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Message : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
            )
            return None, None
        
    def build_initializer_data(self, address: str):
        try:
            initializer_prefix = bytes.fromhex("b63e800d")
            initializer_bytes = encode(
                [ 'address[]', 'uint256', 'address', 'bytes', 'address', 'address', 'uint256', 'address' ],
                [ 
                    [address], 
                    1, 
                    self.ZERO_CONTRACT_ADDRESS, 
                    b"", 
                    self.FALLBACK_HANDLER_ADDRESS, 
                    self.ZERO_CONTRACT_ADDRESS, 
                    0, 
                    self.ZERO_CONTRACT_ADDRESS,
                ]
            )

            initializer = initializer_prefix + initializer_bytes

            return initializer
        except Exception as e:
            raise Exception(f"Built Initializer Data Failed: {str(e)}")
    
    async def perform_create_proxy(self, account: str, address: str, salt_nonce: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, self.KITE_AI['rpc_url'], use_proxy)

            initializer = self.build_initializer_data(address)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.SAFE_PROXY_FACTORY_ADDRESS), abi=self.ERC20_CONTRACT_ABI)
            create_proxy_data = token_contract.functions.createProxyWithNonce(self.GNOSIS_SAFE_L2_ADDRESS, initializer, salt_nonce)
            
            proxy_address = create_proxy_data.call({"from": address})

            estimated_gas = create_proxy_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(0.001, "gwei")
            max_fee = max_priority_fee

            create_proxy_tx = create_proxy_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, create_proxy_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber

            return tx_hash, block_number, proxy_address
        except Exception as e:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Message : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
            )
            return None, None, None
    
    async def approving_token(self, account: str, address: str, rpc_url: str, spender_address: str, contract_address: str, amount_to_wei: int, explorer: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, rpc_url, use_proxy)
            
            spender = web3.to_checksum_address(spender_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, amount_to_wei)

                estimated_gas = approve_data.estimate_gas({"from": address})
                max_priority_fee = web3.to_wei(0.001, "gwei")
                max_fee = max_priority_fee

                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

                tx_hash = await self.send_raw_transaction_with_retries(account, web3, approve_tx)
                receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
                block_number = receipt.blockNumber
                
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Approve : {Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}                                              "
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Block   : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{block_number}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{explorer}{tx_hash}{Style.RESET_ALL}"
                )
                await self.print_timer("Transactions")
            
            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    def build_instructions_data(self, address: str, swap_type: str, token_in: str, token_out: str):
        try:
            payable_receiver = False if swap_type == "native to erc20" else True
            trade_hex = to_hex(
                encode(
                    ['uint8', 'uint8', 'uint256', 'uint256', 'address', 'address', 'address'],
                    [32, 96, 0, 0, '0x0000000000000000000000000000000000000002', token_in, token_out]
                )
            )

            instructions = (
                1, address, payable_receiver, address, 0, 500000, [
                    (
                        3, 2620000, 2120000, trade_hex, 
                        (
                            self.ZERO_CONTRACT_ADDRESS,
                            False,
                            self.ZERO_CONTRACT_ADDRESS,
                            self.SWAP_ROUTER_ADDRESS,
                            self.DEST_BLOCKCHAIN_ID,
                            0,
                            0
                        )
                    )
                ]
            )

            return instructions
        except Exception as e:
            raise Exception(f"Built Instructions Data Failed: {str(e)}")

    async def perform_swap(self, account: str, address: str, swap_type: str, token_in: str, token_out: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, self.KITE_AI["rpc_url"], use_proxy)

            amount_to_wei = web3.to_wei(amount, "ether")

            if swap_type == "native to erc20":
                token_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.NATIVE_CONTRACT_ABI)

            elif swap_type == "erc20 to native":
                await self.approving_token(
                    account, address, self.KITE_AI["rpc_url"], self.SWAP_ROUTER_ADDRESS, token_in, amount_to_wei, self.KITE_AI["explorer"], use_proxy
                )
                token_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.ERC20_CONTRACT_ABI)

            instructions = self.build_instructions_data(address, swap_type, token_in, token_out)

            token_address = self.ZERO_CONTRACT_ADDRESS if swap_type == "native to erc20" else token_in

            swap_data = token_contract.functions.initiate(token_address, amount_to_wei, instructions)

            max_priority_fee = web3.to_wei(0.001, "gwei")
            max_fee = max_priority_fee

            if swap_type == "native to erc20":
                estimated_gas = swap_data.estimate_gas({"from": address, "value": amount_to_wei})
                swap_tx = swap_data.build_transaction({
                    "from": address,
                    "value": amount_to_wei,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

            elif swap_type == "erc20 to native":
                estimated_gas = swap_data.estimate_gas({"from": address})
                swap_tx = swap_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, swap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Message : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_bridge(self, account: str, address: str, rpc_url: str, dest_chain_id: int, src_address: str, amount: float, token_type: str, explorer: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, rpc_url, use_proxy)

            amount_to_wei = web3.to_wei(amount, "ether")

            if token_type == "native":
                token_contract = web3.eth.contract(address=web3.to_checksum_address(src_address), abi=self.NATIVE_CONTRACT_ABI)

            elif token_type == "erc20":
                token_contract = web3.eth.contract(address=web3.to_checksum_address(src_address), abi=self.ERC20_CONTRACT_ABI)

                if src_address == "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63":
                    await self.approving_token(account, address, rpc_url, self.BRIDGE_ROUTER_ADDRESS, src_address, amount_to_wei, explorer, use_proxy)
                    token_contract = web3.eth.contract(address=web3.to_checksum_address(self.BRIDGE_ROUTER_ADDRESS), abi=self.ERC20_CONTRACT_ABI)

            bridge_data = token_contract.functions.send(dest_chain_id, address, amount_to_wei)

            max_priority_fee = web3.to_wei(0.001, "gwei")
            max_fee = max_priority_fee

            if token_type == "native":
                estimated_gas = bridge_data.estimate_gas({"from": address, "value": amount_to_wei})
                bridge_tx = bridge_data.build_transaction({
                    "from": address,
                    "value": amount_to_wei,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

            elif token_type == "erc20":
                estimated_gas = bridge_data.estimate_gas({"from": address})
                bridge_tx = bridge_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, bridge_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber

            return tx_hash, block_number, amount_to_wei
        except Exception as e:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Message : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
            )
            return None, None, None
        
    async def print_timer(self, message: str):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next {message}...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_deposit_question(self):
        while True:
            try:
                deposit_amount = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Deposit Amount [KITE] -> {Style.RESET_ALL}").strip())
                if deposit_amount > 0:
                    self.deposit_amount = deposit_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Deposit Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

    def print_withdraw_kite_question(self):
        while True:
            try:
                withdraw_kite_amount = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Withdraw Amount [KITE] (Min. 1 KITE) -> {Style.RESET_ALL}").strip())
                if withdraw_kite_amount >= 1:
                    self.withdraw_kite_amount = withdraw_kite_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}KITE Amount must be >= 1.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

    def print_withdraw_usdt_question(self):
        while True:
            try:
                withdraw_usdt_amount = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Withdraw Amount [USDT] (Min. 1 USDT) -> {Style.RESET_ALL}").strip())
                if withdraw_usdt_amount >= 1:
                    self.withdraw_usdt_amount = withdraw_usdt_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}USDT Amount must be >= 1.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
    
    def print_withdraw_options(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Withdraw KITE Token{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Withdraw USDT Token{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Withdraw All Tokens{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Withdraw KITE Token" if option == 1 else 
                        "Withdraw USDT Token" if option == 2 else 
                        "Withdraw All Tokens"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    self.withdraw_option = option

                    if self.withdraw_option in [1, 3]:
                        self.print_withdraw_kite_question()

                    if self.withdraw_option in [2, 3]:
                        self.print_withdraw_usdt_question()

                    if self.withdraw_option == 3:
                        self.print_delay_question()
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, or 3).{Style.RESET_ALL}")

    def print_unstake_question(self):
        while True:
            try:
                unstake_amount = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Unstaking Amount [KITE] (Min. 1 KITE) -> {Style.RESET_ALL}").strip())
                if unstake_amount >= 1:
                    self.unstake_amount = unstake_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}KITE Amount must be >= 1.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
    
    def print_stake_question(self):
        while True:
            try:
                stake_amount = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Staking Amount [KITE] (Min. 1 KITE) -> {Style.RESET_ALL}").strip())
                if stake_amount >= 1:
                    self.stake_amount = stake_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}KITE Amount must be >= 1.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
    
    def print_ai_chat_question(self):
        while True:
            try:
                ai_chat_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter AI Chat Count -> {Style.RESET_ALL}").strip())
                if ai_chat_count > 0:
                    self.ai_chat_count = ai_chat_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}AI Chat Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
    
    def print_multisig_question(self):
        while True:
            try:
                multisig_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Multisig Count -> {Style.RESET_ALL}").strip())
                if multisig_count > 0:
                    self.multisig_count = multisig_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}AI Chat Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

    def print_swap_question(self):
        while True:
            try:
                swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Swap Count -> {Style.RESET_ALL}").strip())
                if swap_count > 0:
                    self.swap_count = swap_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Swap Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                kite_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Swap Amount [KITE] -> {Style.RESET_ALL}").strip())
                if kite_swap_amount > 0:
                    self.kite_swap_amount = kite_swap_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}KITE Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                usdt_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Swap Amount [USDT] -> {Style.RESET_ALL}").strip())
                if usdt_swap_amount > 0:
                    self.usdt_swap_amount = usdt_swap_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}USDT Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

    def print_bridge_question(self):
        while True:
            try:
                bridge_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Bridge Count -> {Style.RESET_ALL}").strip())
                if bridge_count > 0:
                    self.bridge_count = bridge_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Bridge Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                kite_bridge_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Bridge Amount [KITE] -> {Style.RESET_ALL}").strip())
                if kite_bridge_amount > 0:
                    self.kite_bridge_amount = kite_bridge_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}KITE Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                usdt_bridge_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Bridge Amount [USDT]  -> {Style.RESET_ALL}").strip())
                if usdt_bridge_amount > 0:
                    self.usdt_bridge_amount = usdt_bridge_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}USDT Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                eth_bridge_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Bridge Amount [ETH]  -> {Style.RESET_ALL}").strip())
                if eth_bridge_amount > 0:
                    self.eth_bridge_amount = eth_bridge_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}ETH Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

    def print_delay_question(self):
        while True:
            try:
                min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Min Delay -> {Style.RESET_ALL}").strip())
                if min_delay > 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
        
        while True:
            try:
                max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Max Delay -> {Style.RESET_ALL}").strip())
                if max_delay >= self.min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Max Delay must be >= Min Delay.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Claim Faucets{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Deposit KITE Token{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Withdraw Tokens{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}4. Unstake KITE Token{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}5. Stake KITE Token{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}6. Claim Stake Reward{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}7. Complete Daily Quiz{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}8. AI Agent Chat{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}9. Create Multisig{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}10. Random Swap{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}11. Random Bridge{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}12. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3/4/5/6/7/8/9/10/11/12] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                    option_type = (
                        "Claim Faucets" if option == 1 else 
                        "Deposit KITE Token" if option == 2 else 
                        "Withdraw Tokens" if option == 3 else 
                        "Unstake KITE Token" if option == 4 else 
                        "Stake KITE Token" if option == 5 else 
                        "Claim Stake Reward" if option == 6 else 
                        "Complete Daily Quiz" if option == 7 else 
                        "AI Agent Chat" if option == 8 else 
                        "Create Multisig" if option == 9 else 
                        "Random Swap" if option == 10 else 
                        "Random Bridge" if option == 11 else 
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, or 12.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, or 12).{Style.RESET_ALL}")

        if option == 2:
            self.print_deposit_question()

        elif option == 3:
            self.print_withdraw_options()

        elif option == 4:
            self.print_unstake_question()
            self.print_delay_question()

        elif option == 5:
            self.print_stake_question()
            self.print_delay_question()

        elif option == 8:
            self.print_ai_chat_question()
            self.print_delay_question()

        elif option == 9:
            self.print_multisig_question()
            self.print_delay_question()

        elif option == 10:
            self.print_swap_question()
            self.print_delay_question()

        elif option == 11:
            self.print_bridge_question()
            self.print_delay_question()

        else:
            if self.auto_deposit_token:
                self.print_deposit_question()

            if self.auto_withdraw_token:
                self.print_withdraw_options()

            if self.auto_unstake_token:
                self.print_unstake_question()

            if self.auto_stake_token:
                self.print_stake_question()

            if self.auto_chat_ai_agent:
                self.print_ai_chat_question()

            if self.auto_create_multisig:
                self.print_multisig_question()

            if self.auto_swap_token:
                self.print_swap_question()

            if self.auto_bridge_token:
                self.print_bridge_question()
            
            self.print_delay_question()

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return option, proxy_choice, rotate_proxy
    
    async def solve_recaptcha(self, site_key: str, page_url: str, retries=5):
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=60)) as session:
                    
                    if self.CAPTCHA_KEY is None:
                        self.log(
                            f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}2Captcha Key Is None{Style.RESET_ALL}"
                        )
                        return None

                    url = f"http://2captcha.com/in.php?key={self.CAPTCHA_KEY}&method=userrecaptcha&googlekey={site_key}&pageurl={page_url}&json=1"
                    async with session.get(url=url) as response:
                        response.raise_for_status()
                        result = await response.json()

                        if result.get("status") != 1:
                            err_text = result.get("error_text", "Unknown Error")
                            
                            self.log(
                                f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}{err_text}{Style.RESET_ALL}"
                            )
                            await asyncio.sleep(5)
                            continue

                        request_id = result.get("request")
                        self.log(
                            f"{Fore.BLUE + Style.BRIGHT}   Req Id  : {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{request_id}{Style.RESET_ALL}"
                        )

                        for _ in range(30):
                            res_url = f"http://2captcha.com/res.php?key={self.CAPTCHA_KEY}&action=get&id={request_id}&json=1"
                            async with session.get(url=res_url) as res_response:
                                res_response.raise_for_status()
                                res_result = await res_response.json()

                                if res_result.get("status") == 1:
                                    recaptcha_token = res_result.get("request")
                                    return recaptcha_token
                                elif res_result.get("request") == "CAPCHA_NOT_READY":
                                    self.log(
                                        f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}Recaptcha Not Ready{Style.RESET_ALL}"
                                    )
                                    await asyncio.sleep(5)
                                    continue
                                else:
                                    break

            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Recaptcha Unsolved{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                return None
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def user_signin(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.NEO_API}/v2/signin"
        data = json.dumps({"eoa":address})
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": self.auth_tokens[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        result = await response.json()

                        raw_cookies = response.headers.getall('Set-Cookie', [])
                        if raw_cookies:
                            cookie = SimpleCookie()
                            cookie.load("\n".join(raw_cookies))
                            cookie_string = "; ".join([f"{key}={morsel.value}" for key, morsel in cookie.items()])
                            self.header_cookies[address] = cookie_string

                            return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
        
        return None
    
    async def user_data(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.OZONE_API}/me"
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch User Data Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def claim_testnet_faucet(self, address: str, recaptcha_token: str, use_proxy: bool, retries=5):
        url = f"{self.OZONE_API}/blockchain/faucet-transfer"
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length":"2",
            "Content-Type": "application/json",
            "x-recaptcha-token": recaptcha_token
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json={}, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Not Claimed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
    
    async def claim_bridge_faucet(self, address: str, payload: dict, use_proxy: bool, retries=5):
        url = f"{self.FAUCET_API}/api/sendToken"
        data = json.dumps(payload)
        headers = {
            **self.FAUCET_HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        if response.status == 429:
                            result = await response.json()
                            err_msg = result.get("message", "Unknown Error")
                            self.log(
                                f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT}Not Time to Claim{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT}{err_msg}{Style.RESET_ALL}"
                            )
                            return None

                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Not Claimed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
            
    async def token_balance(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.OZONE_API}/me/balance"
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Fetch Token Balance Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
    
    async def withdraw_token(self, address: str, amount: int, token_type: str, use_proxy: bool, retries=5):
        url = f"{self.NEO_API}/v2/transfer?eoa={address}&amount={amount}&type={token_type}"
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address],
            "Content-Length": "2",
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json={}, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Withdraw Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
    
    async def staked_info(self, address: str, subnet_id: str, use_proxy: bool, retries=5):
        url = f"{self.OZONE_API}/subnet/{subnet_id}/staked-info?id={subnet_id}"
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Fetch Staked Balance Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
            
    async def unstake_token(self, address: str, subnet_address: str, unstake_amount: int, use_proxy: bool, retries=5):
        url = f"{self.OZONE_API}/subnet/undelegate"
        data = json.dumps({"subnet_address":subnet_address, "amount":unstake_amount})
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        if response.status == 500:
                            result = await response.json()
                            err_msg = result.get("error", "Unknown Error")

                            if "Staking period too short" in err_msg:
                                self.log(
                                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                                    f"{Fore.RED+Style.BRIGHT}Unstake Failed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.YELLOW+Style.BRIGHT}{err_msg}{Style.RESET_ALL}"
                                )
                                return None

                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Unstake Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
            
    async def stake_token(self, address: str, subnet_address: str, stake_amount: int, use_proxy: bool, retries=5):
        url = f"{self.OZONE_API}/subnet/delegate"
        data = json.dumps({"subnet_address":subnet_address, "amount":stake_amount})
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Stake Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None

    async def claim_stake_rewards(self, address: str, subnet_address: str, use_proxy: bool, retries=5):
        url = f"{self.OZONE_API}/subnet/claim-rewards"
        data = json.dumps({"subnet_address":subnet_address})
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Claim Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
    
    async def create_quiz(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.NEO_API}/v2/quiz/create"
        data = json.dumps({"title":self.generate_quiz_title(), "num":1, "eoa":address})
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Fetch Today Quiz Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
        
    async def get_quiz(self, address: str, quiz_id: int, use_proxy: bool, retries=5):
        url = f"{self.NEO_API}/v2/quiz/get?id={quiz_id}&eoa={address}"
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Fetch Question & Answer Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
            
    async def submit_quiz(self, address: str, quiz_id: int, question_id: int, quiz_answer: str, use_proxy: bool, retries=5):
        url = f"{self.NEO_API}/v2/quiz/submit"
        data = json.dumps({"quiz_id":quiz_id, "question_id":question_id, "answer":quiz_answer, "finish":True, "eoa":address})
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Submit Answer Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
            
    async def agent_inference(self, address: str, service_id: str, question: str, use_proxy: bool, retries=5):
        url = f"{self.OZONE_API}/agent/inference"
        data = json.dumps(self.generate_inference_payload(service_id, question))
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        if response.status == 429:
                            result = await response.json()
                            err_msg = result.get("error", "Unknown Error")

                            self.log(
                                f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT}Agents Didn't Respond{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT}{err_msg}{Style.RESET_ALL}"
                            )
                            return None
                        
                        response.raise_for_status()
                        result = ""

                        async for line in response.content:
                            line = line.decode("utf-8").strip()
                            if not line.startswith("data:"):
                                continue

                            if line == "data: [DONE]":
                                return result.strip()

                            try:
                                json_data = json.loads(line[len("data:"):].strip())
                                delta = json_data.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    result += content
                            except json.JSONDecodeError:
                                continue

                        return result.strip()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Agents Didn't Respond{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
            
    async def submit_receipt(self, address: str, service_id: str, question: str, answer: str, use_proxy: bool, retries=5):
        url = f"{self.NEO_API}/v2/submit_receipt"
        data = json.dumps(self.generate_receipt_payload(self.aa_address[address], service_id, question, answer))
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Submit Receipt Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
            
    async def get_inference(self, address: str, inference_id: str, use_proxy: bool, retries=5):
        url = f"{self.NEO_API}/v1/inference?id={inference_id}"
        headers = {
            **self.TESTNET_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        result = await response.json()

                        tx_hash = result.get("data", {}).get("tx_hash", "")
                        if tx_hash == "":
                            raise Exception("Tx Hash Is None")

                        return tx_hash
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Fetch Inference Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
    
    async def owner_safes_wallet(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.MULTISIG_API}/chains/2368/owners/{address}/safes"
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.MULTISIG_HEADERS[address], proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Message : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Fetch Salt Nonce Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
    
    async def submit_bridge_transfer(self, address: str, src_chain_id: int, dest_chain_id: int, src_address: str, dest_address: str, amount_to_wei: int, tx_hash: str, use_proxy: bool, retries=5):
        url = f"{self.BRIDGE_API}/bridge-transfer"
        data = json.dumps(self.generate_bridge_payload(address, src_chain_id, dest_chain_id, src_address, dest_address, amount_to_wei, tx_hash))
        headers = {
            **self.BRIDGE_HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Submit  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
    
    async def process_perform_deposit(self, account: str, address: str, receiver: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_deposit(account, address, receiver, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}                                              "
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Block   : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{block_number}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
            )

        else:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Perform On-Chain Failed{Style.RESET_ALL}"
            )

    async def process_perform_withdraw(self, address: str, withdraw_amount: int, token_type: str, use_proxy: bool):
        withdraw = await self.withdraw_token(address, withdraw_amount, token_type, use_proxy)
        if withdraw:
            tx_hash = withdraw.get("data", {}).get("receipt", {}).get("transactionHash")
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}                                              "
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
            )

    async def process_perform_create_proxy(self, account: str, address: str, salt_nonce: int, use_proxy: bool):
        tx_hash, block_number, proxy_address = await self.perform_create_proxy(account, address, salt_nonce, use_proxy)
        if tx_hash and block_number and proxy_address:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}                                              "
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Address : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{proxy_address}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Block   : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{block_number}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Perform On-Chain Failed{Style.RESET_ALL}"
            )

    async def process_perform_swap(self, account: str, address: str, swap_type: str, token_in: str, token_out: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_swap(account, address, swap_type, token_in, token_out, amount, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}                                              "
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Block   : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{block_number}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Perform On-Chain Failed{Style.RESET_ALL}"
            )
    
    async def process_perform_bridge(self, account: str, address: str, rpc_url: str, src_chain_id: int, dest_chain_id: int, src_address: str, dest_address: str, amount: float, token_type: str, explorer: str, use_proxy: bool):
        tx_hash, block_number, amount_to_wei = await self.perform_bridge(account, address, rpc_url, dest_chain_id, src_address, amount, token_type, explorer, use_proxy)
        if tx_hash and block_number and amount_to_wei:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}                                              "
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Block   : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{block_number}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{explorer}{tx_hash}{Style.RESET_ALL}"
            )

            submit = await self.submit_bridge_transfer(address, src_chain_id, dest_chain_id, src_address, dest_address, amount_to_wei, tx_hash, use_proxy)
            if submit:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Submit  : {Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}"
                )

        else:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Perform On-Chain Failed{Style.RESET_ALL}"
            )

    async def process_option_1(self, address: str, user: dict, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}")
        self.log(
            f"{Fore.BLUE + Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT}Testnet Faucet{Style.RESET_ALL}"
        )

        is_claimable = user.get("data", {}).get("faucet_claimable", False)
        if is_claimable:
            self.log(f"{Fore.YELLOW + Style.BRIGHT}   Solving Recaptcha...{Style.RESET_ALL}")

            recaptcha_token = await self.solve_recaptcha(self.TESTNET_SITE_KEY, self.TESTNET_API)
            if recaptcha_token:
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}Recaptcha Solved Successfully{Style.RESET_ALL}"
                )

                claim = await self.claim_testnet_faucet(address, recaptcha_token, use_proxy)
                if claim:
                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                    )

        else:
            self.log(
                f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Not Time to Claim{Style.RESET_ALL}"
            )

        for token_type in ["KITE", "USDT"]:
            self.log(
                f"{Fore.BLUE + Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}{token_type} Bridge Faucet{Style.RESET_ALL}                                              "
            )

            self.log(f"{Fore.YELLOW + Style.BRIGHT}   Solving Recaptcha... {Style.RESET_ALL}")

            recaptcha_token = await self.solve_recaptcha(self.FAUCET_SITE_KEY, self.FAUCET_API)
            if recaptcha_token:
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Message : {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}Recaptcha Solved Successfully{Style.RESET_ALL}"
                )

                if token_type == "KITE":
                    payload = {"address":address, "token":"", "v2Token":recaptcha_token, "chain":"KITE", "couponId":""}
                else:
                    payload = {"address":address, "token":"", "v2Token":recaptcha_token, "chain":"KITE", "erc20":token_type, "couponId":""}

                claim = await self.claim_bridge_faucet(address, payload, use_proxy)
                if claim:
                    tx_hash = claim.get("txHash")

                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                    )
                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
                    )
                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
                    )

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Deposit   :{Style.RESET_ALL}                                              ")

        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Receiver: {Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT}{self.aa_address[address]}{Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT}{self.deposit_amount} KITE{Style.RESET_ALL}"
        )

        balance = await self.get_token_balance(address, self.KITE_AI['rpc_url'], "", "native", use_proxy)
        self.log(
            f"{Fore.BLUE+Style.BRIGHT}   Balance : {Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT}{balance} KITE{Style.RESET_ALL}"
        )

        if not balance or balance <= self.deposit_amount:
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT}Insufficient KITE Token Balance{Style.RESET_ALL}"
            )
            return

        await self.process_perform_deposit(account, address, self.aa_address[address], use_proxy)

    async def process_option_3(self, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Withdraw  :{Style.RESET_ALL}                                              ")

        balance = await self.token_balance(address, use_proxy)
        if not balance: return

        kite_balance = balance.get("data", {}).get("balances", {}).get("kite", 0)
        usdt_balance = balance.get("data", {}).get("balances", {}).get("usdt", 0)

        if self.withdraw_option == 1:
            self.log(
                f"{Fore.BLUE + Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}KITE{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.withdraw_kite_amount} KITE{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Balance : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{kite_balance} KITE{Style.RESET_ALL}"
            )

            if kite_balance < self.withdraw_kite_amount:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}Insufficient KITE Token Balance{Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_withdraw(address, self.withdraw_kite_amount, "native", use_proxy)

        elif self.withdraw_option == 2:
            self.log(
                f"{Fore.BLUE + Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}USDT{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.withdraw_usdt_amount} USDT{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Balance : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{usdt_balance} USDT{Style.RESET_ALL}"
            )

            if usdt_balance < self.withdraw_usdt_amount:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}Insufficient USDT Token Balance{Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_withdraw(address, self.withdraw_usdt_amount, "erc20", use_proxy)

        elif self.withdraw_option == 3:
            for token in ["KITE", "USDT"]:

                if token == "KITE":
                    withdraw_amount = self.withdraw_kite_amount
                    token_balance = kite_balance
                    token_type = "native"

                elif token == "USDT":
                    withdraw_amount = self.withdraw_usdt_amount
                    token_balance = usdt_balance
                    token_type = "erc20"


                self.log(
                    f"{Fore.BLUE + Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}{token}{Style.RESET_ALL}                                              "
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{withdraw_amount} {token}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Balance : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{token_balance} {token}{Style.RESET_ALL}"
                )

                if token_balance < withdraw_amount:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Insufficient {token} Token Balance{Style.RESET_ALL}"
                    )
                    continue
                
                await self.process_perform_withdraw(address, withdraw_amount, token_type, use_proxy)
                await self.print_timer("Transactions")

    async def process_option_4(self, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Unstaking :{Style.RESET_ALL}                                              ")

        for subnet in [self.BITMIND_SUBNET, self.VERONIKA_SUBNET, self.KITE_SUBNET, self.BITTE_SUBNET]:
            subnet_id = subnet["id"]
            subnet_name = subnet["name"]
            subnet_address = subnet["address"]

            self.log(
                f"{Fore.BLUE + Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}{subnet_name}{Style.RESET_ALL}                                              "
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.unstake_amount} KITE{Style.RESET_ALL}"
            )

            staked = await self.staked_info(address, subnet_id, use_proxy)
            if not staked: continue

            staked_balance = staked.get("data", {}).get("my_staked_amount", 0)

            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Staked  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{staked_balance} KITE{Style.RESET_ALL}"
            )

            if staked_balance < self.unstake_amount:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}Insufficient KITE Token Staked Balance in {subnet_name} Subnet{Style.RESET_ALL}"
                )
                continue
            
            unstake = await self.unstake_token(address, subnet_address, self.unstake_amount, use_proxy)
            if unstake:
                staked_balance = unstake.get("data", {}).get("my_staked_amount")
                tx_hash = unstake.get("data", {}).get("tx_hash")

                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
                )

            await self.print_timer("Transactions")

    async def process_option_5(self, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Staking   :{Style.RESET_ALL}                                              ")

        balance = await self.token_balance(address, use_proxy)
        if not balance: return

        kite_balance = balance.get("data", {}).get("balances", {}).get("kite", 0)
        
        for subnet in [self.BITMIND_SUBNET, self.VERONIKA_SUBNET, self.KITE_SUBNET, self.BITTE_SUBNET]:
            subnet_id = subnet["id"]
            subnet_name = subnet["name"]
            subnet_address = subnet["address"]

            self.log(
                f"{Fore.BLUE + Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}{subnet_name}{Style.RESET_ALL}                                              "
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.stake_amount} KITE{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Balance : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{kite_balance} KITE{Style.RESET_ALL}"
            )

            if kite_balance < self.stake_amount:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}Insufficient KITE Token Balance{Style.RESET_ALL}"
                )
                return
            
            stake = await self.stake_token(address, subnet_address, self.stake_amount, use_proxy)
            if stake:
                tx_hash = stake.get("data", {}).get("tx_hash")
                
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT}Success{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
                )

                kite_balance -= self.stake_amount

            await self.print_timer("Transactions")

    async def process_option_6(self, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Reward    :{Style.RESET_ALL}                                              ")

        for subnet in [self.BITMIND_SUBNET, self.VERONIKA_SUBNET, self.KITE_SUBNET, self.BITTE_SUBNET]:
            subnet_id = subnet["id"]
            subnet_name = subnet["name"]
            subnet_address = subnet["address"]

            self.log(
                f"{Fore.BLUE + Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}{subnet_name}{Style.RESET_ALL}                                              "
            )

            claim = await self.claim_stake_rewards(address, subnet_address, use_proxy)
            if claim:
                amount = claim.get("data", {}).get("claim_amount")
                tx_hash = claim.get("data", {}).get("tx_hash")

                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{amount} USDT{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
                )

            await self.print_timer("Transactions")

    async def process_option_7(self, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Daily Quiz:{Style.RESET_ALL}                                              ")

        create = await self.create_quiz(address, use_proxy)
        if not create: return

        quiz_id = create.get("data", {}).get("quiz_id")
        status = create.get("data", {}).get("status")

        self.log(
            f"{Fore.BLUE + Style.BRIGHT}   Quiz Id : {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{quiz_id}{Style.RESET_ALL}"
        )

        if status != 0:
            self.log(
                f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Already Answered Today{Style.RESET_ALL}"
            )
            return
        
        quiz = await self.get_quiz(address, quiz_id, use_proxy)
        if not quiz: return

        questions = quiz.get("data", {}).get("question", [])

        for question in questions:
            if question:
                question_id = question.get("question_id")
                quiz_content = question.get("content")
                quiz_answer = question.get("answer")

                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Question: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{quiz_content}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Answer  : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{quiz_answer}{Style.RESET_ALL}"
                )

                submit_quiz = await self.submit_quiz(address, quiz_id, question_id, quiz_answer, use_proxy)
                if not submit_quiz: return

                result = submit_quiz.get("data", {}).get("result")

                if result == "RIGHT":
                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT}Correct{Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Wrong{Style.RESET_ALL}"
                    )

    async def process_option_8(self, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}AI Agent  :{Style.RESET_ALL}                                              ")

        used_questions_per_agent = {}

        for i in range(self.ai_chat_count):
            self.log(
                f"{Fore.BLUE+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Chat{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.ai_chat_count} {Style.RESET_ALL}                                              "
            )

            agent = random.choice(self.agent_lists)
            agent_name = agent["agentName"]
            service_id = agent["serviceId"]
            questions = agent["questionLists"]

            if agent_name not in used_questions_per_agent:
                used_questions_per_agent[agent_name] = set()

            used_questions = used_questions_per_agent[agent_name]
            available_questions = [q for q in questions if q not in used_questions]

            question = random.choice(available_questions)

            self.log(
                f"{Fore.BLUE + Style.BRIGHT}   Agent   : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{agent_name}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE + Style.BRIGHT}   Question: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{question}{Style.RESET_ALL}"
            )

            answer = await self.agent_inference(address, service_id, question, use_proxy)
            if not answer:
                continue

            self.log(
                f"{Fore.BLUE + Style.BRIGHT}   Answer  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{answer}{Style.RESET_ALL}"
            )

            submit = await self.submit_receipt(address, service_id, question, answer, use_proxy)
            if submit:
                inference_id = submit.get("data", {}).get("id")

                self.log(
                    f"{Fore.BLUE + Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}Receipt Submited Successfully{Style.RESET_ALL}"
                )

                tx_hash = await self.get_inference(address, inference_id, use_proxy)
                if tx_hash:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Tx Hash : {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{tx_hash}{Style.RESET_ALL}"
                    )
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Explorer: {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{self.KITE_AI['explorer']}{tx_hash}{Style.RESET_ALL}"
                    )

            used_questions.add(question)

            await self.print_timer("Interactions")

    async def process_option_9(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Multisig  :{Style.RESET_ALL}                                              ")

        for i in range(self.multisig_count):
            self.log(
                f"{Fore.BLUE+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Create{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.multisig_count} {Style.RESET_ALL}                                              "
            )

            safes = await self.owner_safes_wallet(address, use_proxy)
            if not safes: continue

            salt_nonce = len(safes.get("safes", []))

            await self.process_perform_create_proxy(account, address, salt_nonce, use_proxy)
            await self.print_timer("Transactions")

    async def process_option_10(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Swap      :{Style.RESET_ALL}                                              ")

        for i in range(self.swap_count):
            self.log(
                f"{Fore.BLUE+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Swap{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.swap_count} {Style.RESET_ALL}                                              "
            )

            swap_type, option, token_in, token_out, ticker, token_type, amount = self.generate_swap_option()

            balance = await self.get_token_balance(address, self.KITE_AI['rpc_url'], token_in, token_type, use_proxy)

            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Options : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{option}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Balance : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{balance} {ticker}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{amount} {ticker}{Style.RESET_ALL}"
            )

            if not balance or balance <= amount:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}Insufficient {ticker} Token Balance{Style.RESET_ALL}"
                )
                continue

            await self.process_perform_swap(account, address, swap_type, token_in, token_out, amount, use_proxy)
            await self.print_timer("Transactions")

    async def process_option_11(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Bridge    :{Style.RESET_ALL}                                              ")

        for i in range(self.bridge_count):
            self.log(
                f"{Fore.BLUE+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Bridge{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.bridge_count} {Style.RESET_ALL}                                              "
            )

            bridge_data = self.generate_bridge_option()
            option = bridge_data["option"]
            rpc_url = bridge_data["rpc_url"]
            explorer = bridge_data["explorer"]
            amount = bridge_data["amount"]
            src_chain_id = bridge_data["src_chain_id"]
            dest_chain_id = bridge_data["dest_chain_id"]
            token_type = bridge_data["src_token"]["type"]
            src_ticker = bridge_data["src_token"]["ticker"]
            src_address = bridge_data["src_token"]["address"]
            dest_address = bridge_data["dest_token"]["address"]

            balance = await self.get_token_balance(address, rpc_url, src_address, token_type, use_proxy)

            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Option  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{option}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Balance : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{balance} {src_ticker}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Amount  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{amount} {src_ticker}{Style.RESET_ALL}"
            )

            if not balance or balance <= amount:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  : {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}Insufficient {src_ticker} Token Balance{Style.RESET_ALL}"
                )
                continue

            await self.process_perform_bridge(account, address, rpc_url, src_chain_id, dest_chain_id, src_address, dest_address, amount, token_type, explorer, use_proxy)
            await self.print_timer("Transactions")

    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    await asyncio.sleep(1)
                    continue

                return False

            return True
        
    async def process_user_signin(self, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            
            signin = await self.user_signin(address, use_proxy)
            if signin:
                self.access_tokens[address] = signin["data"]["access_token"]
                self.aa_address[address] = signin["data"]["aa_address"]

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )
                return True

            return False
        
    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        signed = await self.process_user_signin(address, use_proxy, rotate_proxy)
        if signed:

            user = await self.user_data(address, use_proxy)
            if not user: return
            
            username = user.get("data", {}).get("profile", {}).get("username", "Unknown")
            sa_address = user.get("data", {}).get("profile", {}).get("smart_account_address", "Undifined")
            v1_xp = user.get("data", {}).get("profile", {}).get("total_v1_xp_points", 0)
            v2_xp = user.get("data", {}).get("profile", {}).get("total_xp_points", 0)
            rank = user.get("data", {}).get("profile", {}).get("rank", 0)
            
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Username  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {username} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}SA Address:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(sa_address)} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}V1 Points :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {v1_xp} XP {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}V2 Points :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {v2_xp} XP {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Ranking   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {rank} {Style.RESET_ALL}"
            )
            
            if option == 1:
                await self.process_option_1(address, user, use_proxy)

            elif option == 2:
                await self.process_option_2(account, address, use_proxy)

            elif option == 3:
                await self.process_option_3(address, use_proxy)

            elif option == 4:
                await self.process_option_4(address, use_proxy)

            elif option == 5:
                await self.process_option_5(address, use_proxy)

            elif option == 6:
                await self.process_option_6(address, use_proxy)

            elif option == 7:
                await self.process_option_7(address, use_proxy)

            elif option == 8:
                await self.process_option_8(address, use_proxy)

            elif option == 9:
                await self.process_option_9(account, address, use_proxy)

            elif option == 10:
                await self.process_option_10(account, address, use_proxy)

            elif option == 11:
                await self.process_option_11(account, address, use_proxy)

            else:
                if self.auto_claim_faucet:
                    await self.process_option_1(address, user, use_proxy)

                if self.auto_deposit_token:
                    await self.process_option_2(account, address, use_proxy)

                if self.auto_withdraw_token:
                    await self.process_option_3(address, use_proxy)

                if self.auto_unstake_token:
                    await self.process_option_4(address, use_proxy)

                if self.auto_stake_token:
                    await self.process_option_5(address, use_proxy)

                if self.auto_claim_reward:
                    await self.process_option_6(address, use_proxy)

                if self.auto_daily_quiz:
                    await self.process_option_7(address, use_proxy)

                if self.auto_chat_ai_agent:
                    await self.process_option_8(address, use_proxy)

                if self.auto_create_multisig:
                    await self.process_option_9(account, address, use_proxy)

                if self.auto_swap_token:
                    await self.process_option_10(account, address, use_proxy)

                if self.auto_bridge_token:
                    await self.process_option_11(account, address, use_proxy)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            captcha_key = self.load_2captcha_key()
            if captcha_key:
                self.CAPTCHA_KEY = captcha_key

            agents = self.load_ai_agents()
            if not agents:
                self.log(f"{Fore.RED + Style.BRIGHT}No Agents Loaded.{Style.RESET_ALL}")
                return
            
            self.agent_lists = agents
            
            option, proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = True if proxy_choice == 1 else False

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies()
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Invalid Private Key or Libraries Version Not Supported {Style.RESET_ALL}"
                            )
                            continue
                        
                        auth_token = self.generate_auth_token(address)
                        if not auth_token:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Generate Auth Token Failed, Check Your Cryptography Library {Style.RESET_ALL}                  "
                            )
                            continue

                        user_agent = FakeUserAgent().random

                        self.FAUCET_HEADERS[address] = {
                            "Accept-Language": "application/json, text/plain, */*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://faucet.gokite.ai",
                            "Referer": "https://faucet.gokite.ai/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "User-Agent": user_agent
                        }

                        self.TESTNET_HEADERS[address] = {
                            "Accept-Language": "application/json, text/plain, */*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://testnet.gokite.ai",
                            "Referer": "https://testnet.gokite.ai/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": user_agent
                        }

                        self.BRIDGE_HEADERS[address] = {
                            "Accept-Language": "application/json, text/plain, */*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://bridge.prod.gokite.ai",
                            "Referer": "https://bridge.prod.gokite.ai/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": user_agent
                        }

                        self.MULTISIG_HEADERS[address] = {
                            "Accept-Language": "*/*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://wallet.ash.center",
                            "Referer": "https://wallet.ash.center/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": user_agent
                        }
                        
                        self.auth_tokens[address] = auth_token
                        
                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except ( Exception, ValueError ) as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = KiteAI()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Kite AI Ozone - BOT{Style.RESET_ALL}                                       "                              
        )
