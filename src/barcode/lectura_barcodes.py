import cv2
from pyzbar import pyzbar


def leer_barcode_cam():
    # Inicialización de la cámara
    cap = cv2.VideoCapture(0)

    # Carga del archivo de audio
    # REVISAR EL POR QUE NO SOY CAPAZ DE DARLE PERMISOS PARA QUE ACCEDA A TEMP Y ME CARGE EL AUDIO
    # song = pydub.AudioSegment.from_wav('./beep-01a.wav')

    # Variable de bandera para indicar si se ha detectado un código de barras
    barcode_detected = False

    while cap.isOpened():
        # Captura de un fotograma de la cámara
        success, frame = cap.read()

        # Voltea el fotograma horizontalmente
        frame = cv2.flip(frame, 1)

        # Detecta los códigos de barras en el fotograma
        detected_barcodes = pyzbar.decode(frame)

        # Verifica si se detectaron códigos de barras
        if detected_barcodes:
            # Itera sobre cada código de barras detectado
            for barcode in detected_barcodes:
                # Verifica si el código de barras no está vacío
                if barcode.data != "":
                    # Marca el código de barras en el fotograma y le añade un rectángulo
                    x, y, width, height = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 2)  # Pinta el rectángulo
                    cv2.putText(frame, str(barcode.data), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255),
                                2)  # Pinta el código

                    # Establece la bandera de detección de código de barras en True
                    barcode_detected = True

        # Muestra el fotograma en una ventana
        cv2.imshow('scanner', frame)

        # Espera la pulsación de una tecla
        key = cv2.waitKey(1)

        # Si la tecla es 'q' sale del bucle
        if key == ord('q'):
            break

        # Si la tecla es enter, guarda la imagen
        if barcode_detected and key == 13:
            # cv2.imwrite(output_filename, frame)
            yield barcode.data.decode("utf-8")  # Genera un barcode cada vez que le doy a enter
            # Reproduce el sonido de beep
            # play(song)
            print("Imagen guardada")

            # Restablece la bandera de detección de código de barras a False
            barcode_detected = False

    cap.release()
    cv2.destroyAllWindows()


def leer_barcode_foto():
    # Cargar la imagen
    imagen = cv2.imread('../img/aquabona.jpg')

    # Convertir la imagen a escala de grises
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Detectar los códigos de barras en la imagen
    codigos_barras = pyzbar.decode(imagen_gris)

    # Verificar si se encontraron códigos de barras
    if len(codigos_barras) > 0:
        # Iterar sobre los códigos de barras encontrados
        for codigo in codigos_barras:
            # Extraer el contenido del código de barras
            contenido = codigo.data.decode("utf-8")

            return contenido
    else:
        print("No se encontraron códigos de barras en la imagen.")
