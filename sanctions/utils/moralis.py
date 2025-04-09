# moralis.py

from moralis import evm_api
import os

api_key = os.getenv("MORALIS_API_KEY")

def get_wallet_token_balances(address: str, chain: str = "eth"):
    try:
        params = {
            "address": address,
            "chain": chain,  # for single chain
            "exclude_spam": True,
        }
        result = evm_api.wallets.get_wallet_token_balances_price(api_key=api_key, params=params)
        return result.get("result", [])
    except Exception as e:
        return {"error": str(e)}

def get_wallet_net_worth(address: str, chain: str = "eth"):
    """
    Uses Moralis' /wallets/:address/net-worth endpoint
    which expects 'chains=[chain]' in query params (array),
    plus recommended filters for better accuracy.
    The doc says 'total_networth_usd' is the top-level net worth.
    """
    try:
        params = {
            "address": address,
            "chains": [chain],                 # <--- The endpoint expects an array
            "exclude_spam": True,
            "exclude_unverified_contracts": True,
            "max_token_inactivity": 1,
            "min_pair_side_liquidity_usd": 1000,
        }

        result = evm_api.wallets.get_wallet_net_worth(api_key=api_key, params=params)
        # result shape:
        # {
        #   "total_networth_usd": "3879851.41",
        #   "chains": [
        #       {
        #         "chain": "eth",
        #         "networth_usd": "3879851.41",
        #         ...
        #       }
        #   ]
        # }
        return result  # We'll parse it in the view or front-end
    except Exception as e:
        return {"error": str(e)}
