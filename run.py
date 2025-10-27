import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env once
load_dotenv()

from app import app  # Import after .env is loaded (so app can use env vars if needed)

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    print(f"✅ Running on port {port} | Debug: {debug_mode}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
