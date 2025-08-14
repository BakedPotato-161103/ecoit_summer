import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import hydra
from omegaconf import DictConfig

# Database connection parameters
db_password_encoded = quote_plus(cfg.credentials.db_password)  # Encode password for URL
# Create SQLAlchemy engine
engine = create_engine(f'postgresql+psycopg2://{cfg.credentials.db_user}:{db_password_encoded}@{cfg.credentials.db_host}:{cfg.credentials.db_port}/{cfg.credentials.db_name}')

# Create a dummy DataFrame
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, 40, 45]
}
df = pd.DataFrame(data)
df.to_sql('HN_dummy', engine, if_exists='replace', index=False)

print(f"Dummy data inserted successfully to {cfg.credentials.db_name}!")