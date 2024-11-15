import os
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

# Load environment variables from .env file
load_dotenv()

# Configure Alembic
alembic_cfg = Config("alembic.ini")

# Create initial migration
command.revision(alembic_cfg, autogenerate=True, message="Initial migration")

# Apply migrations
command.upgrade(alembic_cfg, "head")
