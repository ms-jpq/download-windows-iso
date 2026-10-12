# Guía Didáctica: descarga de imagen ISO de Windows

## Resumen

El script `download-windows-iso` automatiza la descarga de un archivo ISO de Windows 10 o Windows 11 desde el sitio web de Microsoft. Utiliza una combinación de Bash, Docker y Playwright (una biblioteca de automatización de navegadores) para:

1. Construir una imagen Docker con Playwright instalado.
2. Lanzar un navegador headless para visitar la página de descarga de Windows 10/11 de Microsoft.
3. Seleccionar la edición deseada del producto (por ejemplo, Windows 10 o Windows 11) y el idioma.
4. Extraer el vínculo de descarga directo para el ISO.
5. Usar `wget` para descargar el ISO al directorio local `tmp/`.

## Cómo Funciona

### Paso 1: Construcción de la Imagen Docker

El script comienza construyendo una imagen Docker llamada `download-windows-iso-2026-bindows` usando el `Dockerfile` del proyecto. El `Dockerfile`:

- Parte de la imagen oficial `mcr.microsoft.com/playwright/python:latest`, que incluye Playwright y Chromium.
- Copia `requirements.txt` e instala las dependencias de Python (actualmente `playwright`).
- Ejecuta `playwright install` para descargar el ejecutable del navegador Chromium.
- Copia el directorio local `scripts/` dentro de la imagen.
- Establece el punto de entrada para ejecutar el módulo Python `srv` con los argumentos `--language` y `--windows-version`.

### Paso 2: Ejecutar la Aplicación Python

El script ejecuta `docker compose build` y `docker run` para iniciar el contenedor. El contenedor ejecuta una aplicación Python (`scripts/play.py`) que:

- Lanzamiento de Chromium en modo headless.
- Navega a `https://www.microsoft.com/software-download/windows{10/11}` (depende del argumento `-w`).
- Descarta cualquier banner de consentimiento de cookies si está presente.
- Selecciona la edición del producto según la versión de Windows seleccionada.
- Haz clic en el botón "Submit" para continuar.
- Espera a que el selector de idioma se vuelva visible.
- Selecciona el idioma especificado mediante el argumento `-l` o `--language` (predeterminado: "English International").
- Haz clic en "Submit" nuevamente para proceder a la página de descarga.
- Espera a que aparezca el vínculo de descarga `<a class="product-download-type">`.
- Extrae el atributo `href` (la URL de descarga directa).
- El script Bash captura esta URL desde la salida estándar del contenedor.
- Nota: El sitio web de Microsoft puede requerir completar la descarga manualmente debido a medidas anti-bot.

### Paso 3: Descargar el ISO

Una vez obtenida la URL de la página de descarga directa del script:

- Crea el directorio `tmp/` si no existe.
- Cambia al directorio `tmp/`.
- El usuario puede ejecutar `wget --content-disposition <URL>` para descargar el archivo ISO, preservando el nombre de archivo original.
- Nota: El sitio web de Microsoft puede requerir completar la descarga manualmente debido a medidas anti-bot.

### Paso 4: Uso

```bash
# Predeterminado: Windows 11, Inglés Internacional
./download.sh

# Descargar Windows 10, Inglés Internacional
./download.sh -l "Inglés Internacional" -w 10

# Descargar Windows 11, Español
./download.sh -l "Español" -w 11

# Los idiomas disponibles dependen del sitio web de Microsoft; valores comunes incluyen:
# - "English International"
# - "Español"
# - "Français"
# - etc.
```

### Advertencias Importantes para Windows 10

Al descargar Windows 10:

- **Soporte principal finalizado**: 14 de octubre de 2025
- **ESU (Actualizaciones de Soporte Extendido) finaliza**: 12 de octubre de 2027
  (Programa de pago de 3 años para recibir actualizaciones críticas e importantes de seguridad)
- **Microsoft puede retirar las descargas de ISOS en cualquier momento** - el vínculo de descarga puede volverse sin aviso previo
- Considere usar Windows 11 para recibir actualizaciones de seguridad continuadas y soporte

## Correcciones Recientes

- Agregado `playwright install` al `Dockerfile` para asegurar que el ejecutable de Chromium esté disponible.
- Agregado `wait_for_load_state("networkidle")` después de la navegación de página para asegurar que los recursos estén cargados.
- Agregado lógica de descarte del banner de consentimiento de cookies.
- Agregado esperas explícitas para la visibilidad de elementos para mejorar la fiabilidad.
- Agregado soporte de selección de versión Windows 10/11.

## Solución de Problemas

Si el script falla:

- Asegúrese de que Docker esté en ejecución y accesible.
- Verifique que el argumento de idioma coincida exactamente con lo que muestra Microsoft (mayúscul/minúscul).
- Verifique que el argumento de versión de Windows sea ya sea "10" o "11".
- El script puede fallar si Microsoft cambia el diseño de su sitio web; en ese caso, los selectores de Playwright pueden necesitar actualizarse.