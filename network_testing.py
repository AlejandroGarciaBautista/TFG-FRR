import subprocess
import time
from datetime import datetime

# Escenarios de tráfico hacia c10-vm1
escenarios = {
    "escenario_1": ["c10-vm3", "c10-vm4"],  # 2 VMs
    "escenario_2": ["c10-vm3", "c10-vm4", "c30-vm1", "c10-vm2"]  # 4 VMs
}
# Destinos para los pings desde c10-vm1
destinos = {
    "c10-vm2": "192.168.10.3",
    "c10-vm3": "192.168.10.4",
    "c30-vm1": "192.168.30.2"
}

# Mapeo namespace → contenedor
ns_to_container = {
    "c10-vm1": "clab-tfg-frr-ansible-h1",
    "c10-vm2": "clab-tfg-frr-ansible-h1",
    "c10-vm3": "clab-tfg-frr-ansible-h20",
    "c10-vm4": "clab-tfg-frr-ansible-h25",
    "c20-vm1": "clab-tfg-frr-ansible-h20",
    "c20-vm2": "clab-tfg-frr-ansible-h25",
    "c30-vm1": "clab-tfg-frr-ansible-h40"
}

# Lanzar ping desde un contenedor y namespace
def lanzar_ping(container, namespace, destino):
    cmd = f"docker exec {container} ip netns exec {namespace} ping -c 50 {destino}"
    print(f"[PING] {namespace} -> {destino}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr

# Generar tráfico hacia c10-vm1 en paralelo
def generar_trafico(vms_generadoras):
    procesos = []
    for ns in vms_generadoras:
        cont = ns_to_container.get(ns)
        if cont:
            cmd = f"docker exec {cont} ip netns exec {ns} ping 192.168.10.2"
            print(f"[TRÁFICO] {ns} → 192.168.10.2")
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            procesos.append(p)
    return procesos

print(f"\n--- Ejecutando escenario_0 ---\n")
# Ejecutar pruebas de ping desde c10-vm1
for nombre_destino, ip_dest in destinos.items():
    nombre_escenario = "escenario_0"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    salida = lanzar_ping(ns_to_container["c10-vm1"], "c10-vm1", ip_dest)
    log_name = f"{nombre_escenario}_{nombre_destino}_{timestamp}.log"
    with open(log_name, "w") as f:
        f.write(salida)
    print(f"[✔] Guardado: {log_name}")

print(f"--- Fin de escenario_0 ---\n")


# Ejecutar experimentos por escenario
for nombre_escenario, vms_generadoras in escenarios.items():
    print(f"\n--- Ejecutando {nombre_escenario} ---\n")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Iniciar tráfico de fondo
    procesos_trafico = generar_trafico(vms_generadoras)
    time.sleep(2)  # Espera para estabilizar el tráfico

    # Ejecutar pruebas de ping desde c10-vm1
    for nombre_destino, ip_dest in destinos.items():
        salida = lanzar_ping(ns_to_container["c10-vm1"], "c10-vm1", ip_dest)
        log_name = f"{nombre_escenario}_{nombre_destino}_{timestamp}.log"
        with open(log_name, "w") as f:
            f.write(salida)
        print(f"[✔] Guardado: {log_name}")

    # Terminar procesos de tráfico
    for p in procesos_trafico:
        p.terminate()
    time.sleep(1)  # Espera breve antes del siguiente escenario

    print(f"--- Fin de {nombre_escenario} ---\n")