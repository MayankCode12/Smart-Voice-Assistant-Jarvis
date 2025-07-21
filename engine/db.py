import csv
import sqlite3

# Connect to SQLite
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Create contacts table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    mobile_no VARCHAR(255),
    email VARCHAR(255) NULL
)
''')

# Open and read CSV file
with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)  # Skip the header row

    for row in csvreader:
        try:
            first_name = row[0].strip()
            last_name = row[2].strip()
            phone = row[18].strip()  # "Phone 1 - Value"

            if not phone:
                continue  # Skip empty phone numbers

            full_name = f"{first_name} {last_name}".strip()

            cursor.execute('''
                INSERT INTO contacts (name, mobile_no)
                VALUES (?, ?)
            ''', (full_name, phone))

        except IndexError:
            print(f"[WARNING] Skipped incomplete row: {row}")
        except Exception as e:
            print(f"[ERROR] Failed to insert row: {e}")

# Commit and close the connection
conn.commit()

# Query for the contact
query = 'krrish Bhai'
query = query.strip().lower()

# Execute the query using the cursor
cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))

# Fetch and print the results
results = cursor.fetchall()
if results:
    print(results[0][0])
else:
    print("No matching contact found.")

# Close the connection
query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

#query = "INSERT INTO web_command VALUES (null,'wikipedia', 'https://www.wikipedia.org/')"
#cursor.execute(query) 
#conn.commit()

query = "INSERT INTO web_command VALUES (null,'whatsapp', 'https://web.whatsapp.com/')"
cursor.execute(query) 
conn.commit()
conn.close()
