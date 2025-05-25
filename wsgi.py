import sys
import os
from dotenv import load_dotenv

project_home = '/home/smartpotato86/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

load_dotenv(os.path.join(project_home, '.env'))

from app import create_app

config = os.getenv('FLASK_ENV') or 'development'

application = create_app(config)
