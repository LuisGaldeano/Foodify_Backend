from models.products import Products
from database.database import session
from models.super import Supermercado
from src.barcode.lectura_barcodes import leer_barcode_foto, leer_barcode_cam


def iniciar_foodify():
    # Inicia el lector
    foodify_generator = leer_barcode_cam()

    for barcode in foodify_generator:
        # Check si el producto está registrado en la BD o no
        check = Products.check_ean_exists(session, barcode)
        if not check:
            print('Hago el registro')
            Products.get_product_and_save(session, barcode)
            # Products.put_in_nevera(session, barcode)

            total_supermarket = ['dia', 'carrefour', 'alcampo']

            for superm in total_supermarket:
                if superm == 'dia':
                    try:
                        dia = Supermercado.extract_price_dia(session, barcode)
                        if dia:
                            try:
                                product = session.query(Products).filter_by(ean=barcode).first()
                                shop_list = product.shop or ''  # Extraer el valor de la columna shop o usar una cadena vacía si es None
                                if shop_list:
                                    shop_list += ', ' + 'dia'  # Agregar el nuevo elemento a la cadena existente, separado por comas
                                else:
                                    shop_list = 'dia'  # Si no hay valores anteriores, usar solo el nuevo elemento
                                product.shop = shop_list
                                session.commit()
                                print('Valor actualizado exitosamente en Dia.')
                            except Exception as e:
                                session.rollback()
                                print(f'Error al actualizar el valor en Dia: {str(e)}')
                    except Exception as e:
                        print(f'Error al extraer el precio de Dia: {str(e)}')
                elif superm == 'carrefour':
                    try:
                        carr = Supermercado.extract_price_carrefour(session, barcode)
                        if carr:
                            try:
                                product = session.query(Products).filter_by(ean=barcode).first()
                                shop_list = product.shop or ''  # Extraer el valor de la columna shop o usar una cadena vacía si es None
                                if shop_list:
                                    shop_list += ', ' + 'carrefour'  # Agregar el nuevo elemento a la cadena existente, separado por comas
                                else:
                                    shop_list = 'carrefour'  # Si no hay valores anteriores, usar solo el nuevo elemento
                                product.shop = shop_list
                                session.commit()
                                print('Valor actualizado exitosamente en carrefour.')
                            except Exception as e:
                                session.rollback()
                                print(f'Error al actualizar el valor en Carrefour: {str(e)}')
                    except Exception as e:
                        print(f'Error al extraer el precio de Carrefour: {str(e)}')

                elif superm == 'alcampo':
                    try:
                        alc = Supermercado.extract_price_alcampo(session, barcode)
                        if alc:
                            try:
                                product = session.query(Products).filter_by(ean=barcode).first()
                                shop_list = product.shop or ''  # Extraer el valor de la columna shop o usar una cadena vacía si es None
                                if shop_list:
                                    shop_list += ', ' + 'alcampo'  # Agregar el nuevo elemento a la cadena existente, separado por comas
                                else:
                                    shop_list = 'alcampo'  # Si no hay valores anteriores, usar solo el nuevo elemento
                                product.shop = shop_list
                                session.commit()
                                print('Valor actualizado exitosamente en Alcampo.')
                            except Exception as e:
                                session.rollback()
                                print(f'Error al actualizar el valor en Alcampo: {str(e)}')
                    except Exception as e:
                        print(f'Error al extraer el precio de Alcampo: {str(e)}')

        else:
            print('Ya está registrado')
            product = session.query(Products).filter(Products.ean == barcode).first()
            if product:
                shop = product.shop
                print(shop)
                if 'dia' in shop:
                    try:
                        Supermercado.extract_price_dia(session, barcode)
                    except Exception:
                        print('Este producto no se vende en Día')
                elif 'carrefour' in shop:
                    try:
                        Supermercado.extract_price_carrefour(session, barcode)
                    except Exception:
                        print('Este producto no se vende en Carrefour')
                elif 'alcampo' in shop:
                    try:
                        Supermercado.extract_price_alcampo(session, barcode)
                    except Exception:
                        print('Este producto no se vende en Alcampo')




def iniciar_foodify_con_imagen():
    # Inicia el lector
    barcode = leer_barcode_foto()
    check = Products.check_ean_exists(session, barcode)
    if not check:
        print('Hago el registro')
        Products.get_product_and_save(session, barcode)
        # Products.put_in_nevera(session, barcode)

        total_supermarket = ['dia', 'carrefour', 'alcampo']

        for superm in total_supermarket:
            if superm == 'dia':
                try:
                    dia = Supermercado.extract_price_dia(session, barcode)
                    if dia:
                        try:
                            product = session.query(Products).filter_by(ean=barcode).first()
                            shop_list = product.shop or ''  # Extraer el valor de la columna shop o usar una cadena vacía si es None
                            if shop_list:
                                shop_list += ', ' + 'dia'  # Agregar el nuevo elemento a la cadena existente, separado por comas
                            else:
                                shop_list = 'dia'  # Si no hay valores anteriores, usar solo el nuevo elemento
                            product.shop = shop_list
                            session.commit()
                            print('Valor actualizado exitosamente en Dia.')
                        except Exception as e:
                            session.rollback()
                            print(f'Error al actualizar el valor en Dia: {str(e)}')
                except Exception as e:
                    print(f'Error al extraer el precio de Dia: {str(e)}')
            elif superm == 'carrefour':
                try:
                    carr = Supermercado.extract_price_carrefour(session, barcode)
                    if carr:
                        try:
                            product = session.query(Products).filter_by(ean=barcode).first()
                            shop_list = product.shop or ''  # Extraer el valor de la columna shop o usar una cadena vacía si es None
                            if shop_list:
                                shop_list += ', ' + 'carrefour'  # Agregar el nuevo elemento a la cadena existente, separado por comas
                            else:
                                shop_list = 'carrefour'  # Si no hay valores anteriores, usar solo el nuevo elemento
                            product.shop = shop_list
                            session.commit()
                            print('Valor actualizado exitosamente en carrefour.')
                        except Exception as e:
                            session.rollback()
                            print(f'Error al actualizar el valor en Carrefour: {str(e)}')
                except Exception as e:
                    print(f'Error al extraer el precio de Carrefour: {str(e)}')

            elif superm == 'alcampo':
                try:
                    alc = Supermercado.extract_price_alcampo(session, barcode)
                    if alc:
                        try:
                            product = session.query(Products).filter_by(ean=barcode).first()
                            shop_list = product.shop or ''  # Extraer el valor de la columna shop o usar una cadena vacía si es None
                            if shop_list:
                                shop_list += ', ' + 'alcampo'  # Agregar el nuevo elemento a la cadena existente, separado por comas
                            else:
                                shop_list = 'alcampo'  # Si no hay valores anteriores, usar solo el nuevo elemento
                            product.shop = shop_list
                            session.commit()
                            print('Valor actualizado exitosamente en Alcampo.')
                        except Exception as e:
                            session.rollback()
                            print(f'Error al actualizar el valor en Alcampo: {str(e)}')
                except Exception as e:
                    print(f'Error al extraer el precio de Alcampo: {str(e)}')

    else:
        print('Ya está registrado')
        product = session.query(Products).filter(Products.ean == barcode).first()
        if product:
            shop = product.shop
            print(shop)
            if 'dia' in shop:
                try:
                    Supermercado.extract_price_dia(session, barcode)
                except Exception:
                    print('Este producto no se vende en Día')
            elif 'carrefour' in shop:
                try:
                    Supermercado.extract_price_carrefour(session, barcode)
                except Exception:
                    print('Este producto no se vende en Carrefour')
            elif 'alcampo' in shop:
                try:
                    Supermercado.extract_price_alcampo(session, barcode)
                except Exception:
                    print('Este producto no se vende en Alcampo')