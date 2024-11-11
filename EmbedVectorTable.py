import pyodbc
import numpy as np
from sentence_transformers import SentenceTransformer

# SQL Server connection details
server = 'localhost'
database = 'vectordb120K'
username = 'sa'
password = ''

# SQL connection
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Load SBERT model
model = SentenceTransformer('all-mpnet-base-v2')

# Select ID and DESCRIPTION2 fields from the table
select_query = "EXEC spGetItems"
cursor.execute(select_query)
rows = cursor.fetchall()

# Perform embedding for each row and save to VECTOR768 field using a stored procedure
for row in rows:
 
    item_id = row.ID
    description = row.DESCRIPTION2
    
    # Skip if DESCRIPTION2 is None
    if description is None:
        print(f"DESCRIPTION2 is empty for ID {item_id}, skipping.")
        continue
    
    # Generate embedding for DESCRIPTION2
    embedding = model.encode(description)
    
    # Convert embedding to a comma-separated string
    embedding_str = ','.join(map(str, embedding))
    
    # Call the stored procedure to update the VECTOR768 field
    try:
        cursor.execute("EXEC SP_UPDATEVECTORFIELD_WEBITEMS @ID = ?, @VECTORSTR = ?", (item_id, embedding_str))
        conn.commit()  # Commit to the database after each update
    except Exception as e:
        print(f"Update error for ID {item_id}: {e}")

# Close the connection
cursor.close()
conn.close()

print("Embedding process completed and saved to VECTOR768 field.")
