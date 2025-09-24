# 🚀 Kite AI BOT

> Automated web3 interaction solution for efficient crypto farming and multi-account management

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/vonssy/KiteAi-BOT.svg)](https://github.com/vonssy/KiteAi-BOT/stargazers)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Proxy Recommendation](#proxy-recommendation)
- [Support](#support)
- [Contributing](#contributing)

## 🎯 Overview

Kite AI BOT is an automated tool designed to streamline onchain operations across multiple accounts. It provides seamless integration with Kite AI network and offers robust proxy support for enhanced security and reliability.

**🔗 Get Started:** [Register on Kite AI](https://testnet.gokite.ai?referralCode=8SOHH7LG)

> **Important:** Connect new evm wallet.

## ✨ Features

- 🔄 **Automated Account Management** - Retrieve account information automatically
- 🌐 **Flexible Proxy Support** - Run with or without proxy configuration
- 🔀 **Smart Proxy Rotation** - Automatic rotation of invalid proxies
- 💰 **Testnet Token Claims** – Claim testnet tokens automatically
- 📥 **Deposit KITE Tokens** – Deposit KITE tokens seamlessly
- 📤 **Withdraw Tokens** – Withdraw tokens automatically
- 🔓 **Unstake KITE Tokens** – Unstake KITE tokens
- 🔒 **Stake KITE Tokens** – Stake KITE tokens automatically
- 🎁 **Claim Staking Rewards** – Collect rewards from staking instantly
- 📝 **Complete Daily Quiz** – Finish daily quiz tasks automatically
- 🤖 **Interact with Kite AI** Agent – Automated interactions with Kite AI
- 🏦 **Create Multisig Wallet** – Deploy and manage multisig wallets
- 🔄 **Random Swap Transactions** – Perform randomized token swaps
- 🌉 **Random Bridge Transactions** – Execute randomized cross-chain bridges
- 👥 **Multi-Account Support** - Manage multiple accounts simultaneously

## 📋 Requirements

- **Python:** Version 3.9 or higher
- **pip:** Latest version recommended
- **Compatible libraries:** web3, eth-account, eth-utils, eth-abi, cryptography (see requirements.txt)
- **2captcha Key:** For automated captcha turnstile solving

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vonssy/KiteAi-BOT.git
cd KiteAi-BOT
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# or for Python 3 specifically
pip3 install -r requirements.txt
```

### 3. Library Version Management

> ⚠️ **Important:** Ensure library versions match those specified in `requirements.txt`

**Check installed library version:**
```bash
pip show library_name
```

**Uninstall conflicting library:**
```bash
pip uninstall library_name
```

**Install specific library version:**
```bash
pip install library_name==version
```

## ⚙️ Configuration

### 2captcha Key Setup (Optional)

Create or edit `2captcha_key.txt` in the project directory:

```
your_2captcha_key
```

### Config Setup

Create or edit `.env` in the project directory:

```
# Change to 'False' to disable it.

AUTO_CLAIM_FAUCET = True
AUTO_DEPOSIT_TOKEN = True
AUTO_WITHDRAW_TOKEN = True
AUTO_UNSTAKE_TOKEN = True
AUTO_STAKE_TOKEN = True
AUTO_CLAIM_REWARD = True
AUTO_DAILY_QUIZ = True
AUTO_CHAT_AI_AGENT = True
AUTO_BRIDGE_TOKEN = True
AUTO_SWAP_TOKEN = True
```

### Account Setup

Create or edit `accounts.txt` in the project directory:

```
your_private_key_1
your_private_key_2
your_private_key_3
```

### Proxy Configuration (Optional)

Create or edit `proxy.txt` in the project directory:

```
# Simple format (HTTP protocol by default)
192.168.1.1:8080

# With protocol specification
http://192.168.1.1:8080
https://192.168.1.1:8080

# With authentication
http://username:password@192.168.1.1:8080
```

## 🚀 Usage

Run the bot using one of the following commands:

```bash
python bot.py
# or for Python 3 specifically
python3 bot.py
```

### Runtime Options

When starting the bot, you'll be prompted to choose:

1. **Proxy Mode Selection:**
   - Option `1`: Run with proxy
   - Option `2`: Run without proxy

2. **Auto-Rotation:** 
   - `y`: Enable automatic invalid proxy rotation
   - `n`: Disable auto-rotation

## 🌐 Proxy Recommendation

<div align="left">
  <img src="images/banner.png" alt="NST Proxy Banner" width="300">
</div>

For reliable multi-wallet automation and geo-restriction bypass, we recommend **Nstproxy**:

### Why Nstproxy?
- 💰 **Affordable pricing** starting from $0.1/GB
- 🌍 **Global coverage** with multiple locations
- 🔄 **Advanced rotation control**
- 🛡️ **Anti-ban technology**

### Get Started with Nstproxy
- 🔗 **Website:** [Nstproxy.com](https://www.nstproxy.com/?utm_source=vonssy)
- 💬 **Telegram:** [@nstproxy](https://t.me/nstproxy)
- 🎮 **Discord:** [Join Server](https://discord.gg/5jjWCAmvng)
- 📚 **GitHub:** [Nstproxy Repository](https://github.com/Nstproxy)

> 🎁 **Special Offer:** Use code `VONSSY` for **10% OFF** your first purchase!

## 💖 Support the Project

If this project has been helpful to you, consider supporting its development:

### Cryptocurrency Donations

| Network | Address |
|---------|---------|
| **EVM** | `0xe3c9ef9a39e9eb0582e5b147026cae524338521a` |
| **TON** | `UQBEFv58DC4FUrGqinBB5PAQS7TzXSm5c1Fn6nkiet8kmehB` |
| **SOL** | `E1xkaJYmAFEj28NPHKhjbf7GcvfdjKdvXju8d8AeSunf` |
| **SUI** | `0xa03726ecbbe00b31df6a61d7a59d02a7eedc39fe269532ceab97852a04cf3347` |

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. ⭐ **Star this repository** if you find it useful
2. 👥 **Follow** for updates on new features
3. 🐛 **Report issues** via GitHub Issues
4. 💡 **Suggest improvements** or new features
5. 🔧 **Submit pull requests** for bug fixes or enhancements

## 📞 Contact & Support

- **Developer:** vonssy
- **Issues:** [GitHub Issues](https://github.com/vonssy/KiteAi-BOT/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vonssy/KiteAi-BOT/discussions)

---

<div align="center">

**Made with ❤️ by [vonssy](https://github.com/vonssy)**

*Thank you for using Kite AI BOT! Don't forget to ⭐ star this repository.*

</div>