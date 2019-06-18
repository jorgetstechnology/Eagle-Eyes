import sqlite3


def update_db(use_latest, ip, port, module_ports):
  conn = sqlite3.connect('Settings.db')
  c = conn.cursor()

  # Save changes to DB
  if use_latest is False:
    try:
      c.execute("""CREATE TABLE settings (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        port INTEGER,
        module_ports TEXT
      )""")
      conn.commit()
    except:
      c.execute("UPDATE settings SET ip=?, port=?, module_ports=? WHERE ID=1;", (ip, port, module_ports))
      conn.commit()
      c.execute("SELECT * FROM settings WHERE ID=1")			
      conn.commit()
      db_data = c.fetchone()
    else:
      c.execute("INSERT INTO settings (ip, port, module_ports) VALUES (?, ?, ?);", (ip, port, module_ports))
      conn.commit()
      c.execute("SELECT * FROM settings WHERE ID=1")			
      conn.commit()
      db_data = c.fetchone()
  
  conn.close()


def get_module_data():
  conn = sqlite3.connect('Settings.db')
  c = conn.cursor()

  c.execute("SELECT * FROM settings WHERE ID=1")
  conn.commit()
  db_data = c.fetchone()
  conn.close()

  return db_data