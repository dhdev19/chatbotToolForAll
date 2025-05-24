# from app import app
# if __name__ == '__main__':
#     app.run(debug=True)

from app import app
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
print("\n=== ROUTES ===")
for rule in app.url_map.iter_rules():
    print(rule)
if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
