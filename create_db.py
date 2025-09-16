from miso_api.database import engine, Base
from miso_api.models import db_models

print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('Database tables created successfully.')
