import aevopy
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

if __name__ == "__main__":
    client = aevopy.AevoClient()
    positions = client.get_positions()
    print(f"positions: {positions}")