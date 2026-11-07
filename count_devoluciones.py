import psycopg2
import os

env = {}
if os.path.exists('backend/.env'):
    with open('backend/.env') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                env[k] = v

conn = psycopg2.connect(
    dbname=env.get('DB_NAME', 'obras'),
    user=env.get('DB_USER', 'devpoppy'),
    password=env.get('DB_PASSWORD'),
    host=env.get('DB_HOST', '147.15.29.190'),
    port=int(env.get('DB_PORT', 5433)),
    connect_timeout=10
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM comercio.t_devolucion;")
print("Total rows in t_devolucion:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM comercio.t_detalle_devolucion;")
print("Total rows in t_detalle_devolucion:", cur.fetchone()[0])
conn.close()

