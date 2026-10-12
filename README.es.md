# Descarga de imagen ISO de Windows

Guion bash para descargar la imagen ISO de Windows desde el sitio web de Microsoft usando Docker y Playwright.

## Requisitos

1. Tener `docker`
2. Tener `bash`
3. Tener `wget`

## Instalación

### En Windows

1. Descargue Docker Desktop desde: https://www.docker.com/products/docker-desktop
2. Ejecute el instalador y siga el asistente de configuración
3. Una vez instalado, abra Docker Desktop menú de inicio
4. Crear una cuenta Docker o inicie sesión si ya tiene una
5. Docker se iniciará automáticamente y verá el ícono de la ballena en la bandeja del sistema
6. Verifique la instalación ejecutando `docker --version` en PowerShell o Símbolo del sistema

### En Linux (Ubuntu/Debian)

```bash
# Actualizar el índice de paquetes
sudo apt-get update

# Instalar prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Agregar la clave GPG oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Configurar el repositorio
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Motor de Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verificar la instalación
sudo docker run --rm hello-world
```

### En Linux (Otras distribuciones)

Consulte la documentación oficial de Docker para su distribución específica:
https://docs.docker.com/engine/install/

## Uso

### Paso 1

```
# Predeterminado a `Windows 11, Inglés Internacional`
./download.sh [-l IDIOMA] [-w VERSION_WINDOWS]

# Descargar Windows 10, Inglés Internacional
./download.sh -l "Inglés Internacional" -w 10

# Descargar Windows 11, Español
./download.sh -l "Español" -w 11
```

### Paso 2

Verifique `./tmp/` para la ISO descargada.

### Paso 3

El script realizará las siguientes acciones:

1. Construirá una imagen Docker con Playwright instalado
2. Ejecutará un navegador para navegar a la página de descarga de Windows {10/11} de Microsoft
3. Mostrará advertencias de fin de soporte
4. Seleccionará la edición del producto y el idioma
5. Salida la página de URL de descarga directa
6.Nota: El sitio web de Microsoft puede requerir completar la descarga manualmente
   debido a medidas anti-bot. La URL de salida se puede usar con wget o un explorador.

### Advertencias Importantes

Al descargar Windows 10:

- **Soporte principal finalizado**: 14 de octubre de 2025
- **ESU (Actualizaciones de Soporte Extendido) finaliza**: 12 de octubre de 2027
  (Programa de pago de 3 años para recibir actualizaciones críticas e importantes de seguridad)
- **Microsoft puede retirar las descargas de ISOS en cualquier momento** - el vínculo de descarga puede volverse sin aviso previo
- Considere usar Windows 11 para recibir actualizaciones de seguridad continuadas y soporte

### Paso 4

El script salida una URL de página de descarga. Puede usar esta URL con wget o un explorador:

```bash
# Usando wget (puede requerir opciones adicionales para el sitio de Microsoft):
wget --content-disposition "URL_OUTPUT"

# O simplemente abra la URL en un explorador y haga clic en el botón de descarga:
# La URL se mostrará después de ejecutar el script
```