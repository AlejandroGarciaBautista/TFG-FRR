import yaml
import subprocess

# Cargar el fichero topology.yml
with open("topology.yml", "r") as file:
    data = yaml.safe_load(file)

links = data['topology']['links']

uplink_delay = "0.5ms"
access_delay = "0.5ms"

for link in links:
    ep1, ep2 = link['endpoints']
    
    node1, iface1 = ep1.split(":")
    node2, iface2 = ep2.split(":")
    
    # Determinar tipo de enlace
    if node1.startswith("spine") or node2.startswith("spine"):
        delay = uplink_delay
    elif (node1.startswith("leaf") and node2.startswith("h")) or (node2.startswith("leaf") and node1.startswith("h")):
        delay = access_delay
    else:
        continue  # Ignorar enlaces que no son uplink o acceso

    cmd1 = [
    "containerlab", "tools", "netem", "set",
    "-n", f"clab-tfg-frr-ansible-{node1}",
    "-i", iface1,
    "--delay", delay
    ]

    print(f"Ejecutando: {' '.join(cmd1)}")
    subprocess.run(cmd1)
