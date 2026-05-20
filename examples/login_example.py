import os
import sys
import logging

# Ensure the parent directory is in the python path so we can import betnacional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from betnacional import BetnacionalClient
from betnacional.exceptions import BetnacionalException

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("login_example")

def main():
    logger.info("Initializing Betnacional Python Client...")
    
    # In a production script, you can specify custom user agents or proxy
    client = BetnacionalClient()

    try:
        logger.info("Attempting authentication...")
        # Authenticates using CPF and Password loaded from .env automatically
        success = client.login()
        
        if success:
            logger.info("=" * 50)
            logger.info("SUCCESS: Login completed successfully!")
            
            cookies = client.get_session_cookies()
            logger.info("Active Session Cookies:")
            for name, val in cookies.items():
                # Obfuscate sensitive session keys for safety
                visible_len = min(6, len(val))
                obfuscated_val = val[:visible_len] + "*" * (len(val) - visible_len)
                logger.info(f" - {name}: {obfuscated_val}")
                
            logger.info("=" * 50)
            
            # Fetch and print full user profile and balance details
            try:
                profile = client.get_profile()
                logger.info("User Profile Details:")
                logger.info(f" - ID: {profile.id}")
                logger.info(f" - Name: {profile.name}")
                logger.info(f" - CPF: {profile.cpf}")
                logger.info(f" - Balance: R$ {profile.balance:.2f}")
            except Exception as e:
                logger.error(f"Failed to retrieve user profile or balance: {e}")
                
        else:
            logger.error("Authentication failed (no exception raised, but login returned False).")

    except BetnacionalException as e:
        logger.error(f"Betnacional error occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
