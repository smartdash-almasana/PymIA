# Catálogo de significados empresariales para columnas Excel

Catálogo en formato de lista de términos habituales en archivos Excel de PyMEs.

- **cliente**
  - **Sinónimos habituales:** comprador, contraparte, titular, beneficiario, razón social cliente
  - **Significado empresarial:** Persona o empresa que adquiere bienes o servicios de la empresa.
  - **Tipo de dato:** texto / identificador
  - **Confusiones frecuentes:** Se confunde con *proveedor* o con el nombre del *vendedor* cuando el Excel no aclara el rol de la parte.

- **cliente_id**
  - **Sinónimos habituales:** id_cliente, cod_cliente, customer_id, CUIT, RFC, NIF, RUT
  - **Significado empresarial:** Código único asignado a un cliente para identificarlo en el sistema.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *proveedor_id* o *producto_id* cuando se usa la abreviatura "id" sin prefijo descriptivo.

- **proveedor**
  - **Sinónimos habituales:** suministrador, abastecedor, acreedor, vendor, razón social prov
  - **Significado empresarial:** Persona o empresa que vende mercadería o servicios a la empresa.
  - **Tipo de dato:** texto / identificador
  - **Confusiones frecuentes:** Se confunde con *cliente* en archivos que combinan compras y ventas sin distinguir la contraparte.

- **proveedor_id**
  - **Sinónimos habituales:** id_proveedor, cod_proveedor, CUIT proveedor, RFC proveedor
  - **Significado empresarial:** Código único que identifica a un proveedor en el sistema.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *cliente_id* si ambos coexisten en la misma tabla sin un prefijo claro.

- **producto**
  - **Sinónimos habituales:** artículo, ítem, bien, servicio, sku_description, mercadería
  - **Significado empresarial:** Bien o servicio que se compra, vende o produce.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *código* cuando se usa la descripción como clave principal en lugar del código técnico.

- **producto_id**
  - **Sinónimos habituales:** id_producto, sku, cod_producto, id_articulo, referencia
  - **Significado empresarial:** Código único que identifica a un producto de forma unívoca.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *código* interno o código de barras si ambos existen pero no están normalizados.

- **código**
  - **Sinónimos habituales:** cod, sku, código interno, part number, referencia
  - **Significado empresarial:** Clave alfanumérica de referencia de un artículo, cuenta o comprobante.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *producto_id* cuando uno es legible y el otro es un identificador técnico del sistema.

- **categoría**
  - **Sinónimos habituales:** rubro, familia, línea, tipo, grupo, sector, clase
  - **Significado empresarial:** Clasificación que agrupa productos o servicios con características similares.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *producto* cuando se usa una categoría como si fuera un ítem concreto vendible.

- **servicio**
  - **Sinónimos habituales:** prestación, trabajo, actividad, asistencia, soporte
  - **Significado empresarial:** Actividad intangible que se vende o se ejecuta para un cliente.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *producto* o con *mano_de_obra* cuando se facturan por separado en el mismo archivo.

- **servicio_id**
  - **Sinónimos habituales:** id_servicio, cod_servicio, id_prestación, sku_servicio
  - **Significado empresarial:** Código único que identifica un tipo de servicio.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *producto_id* o *tarea* si no se discrimina entre catálogo de servicios y ejecución.

- **repuesto**
  - **Sinónimos habituales:** pieza, recambio, componente, spare part, accesorio
  - **Significado empresarial:** Pieza individual utilizada para reparar o mantener un equipo o producto.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *producto* cuando el negocio vende tanto repuestos como artículos terminados.

- **repuesto_id**
  - **Sinónimos habituales:** id_repuesto, cod_repuesto, pieza_id, nro_pieza
  - **Significado empresarial:** Código único que identifica a un repuesto en el sistema.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *producto_id* o *insumo_id* si todos los ítems comparten la misma numeración.

- **materia_prima**
  - **Sinónimos habituales:** mp, materia, insumo principal, raw material, insumo productivo
  - **Significado empresarial:** Material básico que se transforma durante el proceso productivo.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *insumo* cuando ambos se registran en la misma columna sin distinguir su rol en la fórmula de producción.

- **materia_prima_id**
  - **Sinónimos habituales:** id_mp, cod_materia, insumo_id, cod_mp
  - **Significado empresarial:** Código único que identifica una materia prima.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *producto_id* o *insumo_id* si el sistema no separa la nomenclatura de insumos y productos terminados.

- **insumo**
  - **Sinónimos habituales:** suministro, material auxiliar, consumible, recurso productivo
  - **Significado empresarial:** Bien o material necesario para la producción o prestación, distinto de la materia prima principal.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *materia_prima* o con *repuesto* según el grado de transformación o uso final.

- **insumo_id**
  - **Sinónimos habituales:** id_insumo, cod_insumo, material_id
  - **Significado empresarial:** Código único que identifica un insumo.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *materia_prima_id* cuando ambos conceptos se registran bajo una misma columna genérica.

- **lote**
  - **Sinónimos habituales:** batch, nro_lote, lote_producción, serie, lote_entrada
  - **Significado empresarial:** Conjunto de unidades producidas, compradas o vendidas bajo una misma identificación de trazabilidad.
  - **Tipo de dato:** identificador / texto
  - **Confusiones frecuentes:** Se confunde con *orden_producción* cuando un lote se asocia a una única orden pero no son lo mismo.

- **unidad**
  - **Sinónimos habituales:** unidad_de_medida, udm, um, medida, presentación
  - **Significado empresarial:** Forma en que se expresa la cantidad (kg, litros, metros, unidades, horas).
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *cantidad* o con *unidades* cuando la columna contiene valores numéricos en lugar de etiquetas de medida.

- **orden_producción**
  - **Sinónimos habituales:** op, nro_op, o.p., orden de fabricación, of
  - **Significado empresarial:** Documento o código que autoriza y controla un proceso de producción específico.
  - **Tipo de dato:** identificador / texto
  - **Confusiones frecuentes:** Se confunde con *pedido* o con *orden_de_trabajo* cuando la empresa mezcla producción con pedidos de clientes.

- **producción**
  - **Sinónimos habituales:** fabricación, elaboración, output, cantidad_producida
  - **Significado empresarial:** Cantidad o volumen de bienes elaborados en un proceso o período.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *venta* o con *stock* cuando se registra lo fabricado como si ya estuviera vendido o disponible sin descontar mermas.

- **producción_real**
  - **Sinónimos habituales:** producido_real, real_fabricado, output_efectivo
  - **Significado empresarial:** Cantidad efectivamente obtenida de un proceso productivo, incluyendo ajustes.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *producción_estimada* o con *stock_actual* si se asume que todo lo producido ingresó al inventario.

- **producción_estimada**
  - **Sinónimos habituales:** meta_producción, target, objetivo, plan, cantidad_estimada
  - **Significado empresarial:** Cantidad que se espera fabricar según la planificación.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *producción_real* cuando se comparan planificación vs. ejecución sin etiquetar correctamente.

- **formula**
  - **Sinónimos habituales:** receta, bill_of_materials, bom, lista_de_materiales, estructura
  - **Significado empresarial:** Relación de materias primas e insumos necesarios para producir una unidad o lote.
  - **Tipo de dato:** texto / identificador
  - **Confusiones frecuentes:** Se confunde con *producto* cuando la columna contiene el nombre de la fórmula en lugar del código del insumo.

- **tiempo_estimado**
  - **Sinónimos habituales:** tiempo_plan, horas_estimadas, duración_estimada, standard
  - **Significado empresarial:** Cantidad de tiempo prevista para realizar una tarea, operación o producción.
  - **Tipo de dato:** cantidad / días
  - **Confusiones frecuentes:** Se confunde con *tiempo_real* cuando se usa como registro histórico sin aclarar que es una proyección.

- **tiempo_real**
  - **Sinónimos habituales:** tiempo_ejecutado, horas_reales, duración_real, tiempo_invertido
  - **Significado empresarial:** Cantidad de tiempo efectivamente consumida en una tarea, operación o producción.
  - **Tipo de dato:** cantidad / días
  - **Confusiones frecuentes:** Se confunde con *tiempo_estimado* o con *horas_facturables* si se registran todas las horas como cobrables.

- **horas_hombre**
  - **Sinónimos habituales:** hh, horas_persona, horas_operario, mano_de_obra_directa
  - **Significado empresarial:** Tiempo de trabajo humano invertido en una tarea o proceso productivo.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *horas_maquina* o con *horas_facturables* cuando se mezclan costos productivos con precios de venta.

- **horas_maquina**
  - **Sinónimos habituales:** hm, horas_equipo, horas_de_uso, runtime
  - **Significado empresarial:** Tiempo de uso efectivo de una máquina o equipo en una operación.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *horas_hombre* o con *capacidad* si se registran horas disponibles en lugar de horas usadas.

- **desperdicio**
  - **Sinónimos habituales:** merma, scrap, desecho, pérdida, waste
  - **Significado empresarial:** Cantidad de material o producto descartado por defectos o proceso.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *salida* o con *stock* cuando las mermas no se registran por separado del consumo productivo.

- **capacidad**
  - **Sinónimos habituales:** capacidad_teorica, maximo, potencial, rendimiento_esperado
  - **Significado empresarial:** Nivel máximo de producción, almacenamiento o procesamiento disponible.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *producción_real* o con *stock* cuando se usa como registro de volumen físico existente.

- **planta**
  - **Sinónimos habituales:** linea, sector, taller, unidad_productiva, centro_trabajo
  - **Significado empresarial:** Ubicación o unidad física donde se realiza una operación productiva.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *sucursal* o con *bodega* cuando la empresa usa nombres genéricos para todas sus instalaciones.

- **mano_de_obra**
  - **Sinónimos habituales:** mo, mano_obra, labor, jornal, costo_directo_personal
  - **Significado empresarial:** Trabajo humano aplicado a la producción o a un servicio técnico, expresado en dinero o en horas.
  - **Tipo de dato:** importe / cantidad
  - **Confusiones frecuentes:** Se confunde con *servicio* o con *costo* general cuando se mezclan costos de personal con gastos administrativos.

- **horas**
  - **Sinónimos habituales:** cantidad_horas, hrs, tiempo, duración
  - **Significado empresarial:** Medida de tiempo utilizada en una operación, servicio o tarea.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *días* o con *tiempo_estimado* cuando no se especifica si son horas trabajadas, máquina o de plazo.

- **horas_técnicas**
  - **Sinónimos habituales:** horas_facturables, horas_efectivas, horas_dedicadas, billable_hours
  - **Significado empresarial:** Horas de un técnico o profesional que pueden facturarse a un cliente.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *horas* totales o con *tiempo_real* si se incluyen horas no facturables sin separar.

- **tiempo_de_instalación**
  - **Sinónimos habituales:** tiempo_reparación, tiempo_de_servicio, duración_ot, tiempo_de_marcha
  - **Significado empresarial:** Tiempo empleado en instalar, reparar o mantener un bien o servicio.
  - **Tipo de dato:** cantidad / días
  - **Confusiones frecuentes:** Se confunde con *tiempo_estimado* o con *horas* generales cuando se registran plazos en lugar de tiempo de ejecución.

- **diagnostico**
  - **Sinónimos habituales:** evaluación, informe_técnico, hallazgo, estado_técnico
  - **Significado empresarial:** Descripción del problema o estado detectado en un equipo, inmueble o situación del cliente.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *garantía* o con *observaciones* cuando se mezcla la descripción técnica con notas comerciales.

- **garantía**
  - **Sinónimos habituales:** garantia, warranty, certificación, cobertura, plazo_de_garantia
  - **Significado empresarial:** Compromiso de reparación o cambio por un período determinado tras la venta o servicio.
  - **Tipo de dato:** texto / días
  - **Confusiones frecuentes:** Se confunde con *vencimiento* o con *plazo* cuando se registra la fecha de fin de garantía como fecha genérica.

- **orden_de_trabajo**
  - **Sinónimos habituales:** ot, nro_ot, o.t., orden_servicio, os, trabajo
  - **Significado empresarial:** Documento o código que autoriza y controla una tarea de servicio, reparación o mantenimiento.
  - **Tipo de dato:** identificador / texto
  - **Confusiones frecuentes:** Se confunde con *pedido*, *factura* o *orden_producción* cuando la empresa usa las mismas abreviaturas para todo.

- **visita**
  - **Sinónimos habituales:** domicilio, asistencia, servicio_a_domicilio, call, appointment
  - **Significado empresarial:** Desplazamiento o atención presencial realizada en la ubicación del cliente.
  - **Tipo de dato:** texto / cantidad
  - **Confusiones frecuentes:** Se confunde con *orden_de_trabajo* o con *tarea* cuando una visita incluye varios trabajos o técnicos.

- **tarea**
  - **Sinónimos habituales:** actividad, sub_tarea, item_de_trabajo, job, trabajo_parcial
  - **Significado empresarial:** Unidad de trabajo individual dentro de un proyecto, orden de trabajo o servicio.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *servicio* o con *proyecto* cuando se usa como sinónimo del conjunto total de trabajo.

- **técnicos**
  - **Sinónimos habituales:** equipo_asignado, operario, personal_técnico, recurso, ejecutor
  - **Significado empresarial:** Persona o grupo que ejecuta una tarea técnica, de producción o de servicio.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *vendedor* o con *empleado* general si el archivo no distingue roles operativos de comerciales.

- **pedido**
  - **Sinónimos habituales:** order, pedido_cliente, nro_pedido, orden_de_compra, oc
  - **Significado empresarial:** Solicitud de productos o servicios que aún no se entregan o facturan.
  - **Tipo de dato:** identificador / texto
  - **Confusiones frecuentes:** Se confunde con *factura* o con *remito* cuando el negocio registra el pedido como venta consumada.

- **remito**
  - **Sinónimos habituales:** rem, remito_de_entrega, albarán, guia_de_remisión, nro_remito
  - **Significado empresarial:** Documento que acredita la entrega física de mercadería sin implicar necesariamente cobro inmediato.
  - **Tipo de dato:** identificador / texto
  - **Confusiones frecuentes:** Se confunde con *factura* o con *comprobante* cuando se usa como único respaldo de la operación.

- **guia**
  - **Sinónimos habituales:** guia_de_transporte, guia_de_envio, nro_guia, carta_de_porte
  - **Significado empresarial:** Documento o código que acompaña y controla el traslado de mercadería por terceros.
  - **Tipo de dato:** identificador / texto
  - **Confusiones frecuentes:** Se confunde con *remito* o con *tracking* cuando la empresa genera y recibe guías sin discriminar origen.

- **costo_de_envío**
  - **Sinónimos habituales:** flete, transporte, gasto_de_envio, shipping_cost, logística
  - **Significado empresarial:** Costo incurridopor el traslado de mercadería al cliente o entre depósitos.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *costo* del producto o con *comisión* cuando se carga al cliente sin discriminar su naturaleza.

- **tracking**
  - **Sinónimos habituales:** nro_seguimiento, seguimiento, tracking_id, código_envío
  - **Significado empresarial:** Código que permite rastrear el estado y ubicación de un envío.
  - **Tipo de dato:** identificador / texto
  - **Confusiones frecuentes:** Se confunde with *guia* o con *pedido_id* cuando el número de seguimiento se usa como identificador principal del pedido.

- **entrega**
  - **Sinónimos habituales:** fecha_entrega, delivery, entrega_real, recepción
  - **Significado empresarial:** Momento o evento en que los bienes o servicios llegan al cliente o destino final.
  - **Tipo de dato:** fecha / texto
  - **Confusiones frecuentes:** Se confunde con *fecha* de emisión o con *vencimiento* si no se especifica si es prometida o efectiva.

- **estado_envío**
  - **Sinónimos habituales:** estado_entrega, situacion_envio, status, etapa_logistica
  - **Significado empresarial:** Condición actual de un envío (pendiente, en tránsito, entregado, devuelto).
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *estado* general del pago o del pedido cuando una sola columna describe todo el proceso.

- **canal**
  - **Sinónimos habituales:** canal_de_venta, medio, origen, marketplace, sucursal_virtual
  - **Significado empresarial:** Vía por la cual se concreta una venta o contacto con el cliente.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *sucursal* o con *medio_de_pago* cuando se agrupan canales físicos con digitales sin separar.

- **cotización**
  - **Sinónimos habituales:** presupuesto, quote, propuesta, oferta, estimado
  - **Significado empresarial:** Documento o valor que estima el costo de un bien o servicio antes de su confirmación.
  - **Tipo de dato:** importe / identificador
  - **Confusiones frecuentes:** Se confunde con *venta* o con *pedido* cuando el presupuesto aprobado no se transfiere a una columna distinta.

- **venta**
  - **Sinónimos habituales:** operación, ingreso, transacción, movimiento venta, ingreso por venta
  - **Significado empresarial:** Operación comercial de venta individual o ingreso derivado de una venta específica.
  - **Tipo de dato:** importe / texto
  - **Confusiones frecuentes:** Se confunde con *ventas* (plural acumulado) o con *cobrado* si se asume que ya fue pagada.

- **ventas**
  - **Sinónimos habituales:** ingresos por ventas, facturación, revenue, ingresos totales
  - **Significado empresarial:** Total acumulado de operaciones de venta en un período determinado.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *venta_total* de un pedido específico vs. acumulado mensual o anual.

- **venta_total**
  - **Sinónimos habituales:** total_venta, venta_general, venta neta, venta bruta
  - **Significado empresarial:** Monto final agregado de una venta o conjunto de ventas en un documento o corte.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *cobrado* o con *ventas* del período cuando representa solo un subconjunto.

- **cantidad**
  - **Sinónimos habituales:** qty, cant, cantidad_unidades, piezas, uds, unid
  - **Significado empresarial:** Número de unidades de un producto involucradas en una operación.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *unidades* cuando estas últimas representan la unidad de medida y no el volumen.

- **unidades**
  - **Sinónimos habituales:** uds, uni, unid, cantidad
  - **Significado empresarial:** Cantidad de ítems o, en algunos archivos, la unidad de medida (kg, litros, metros).
  - **Tipo de dato:** cantidad / texto
  - **Confusiones frecuentes:** Se confunde con *cantidad* si ambas columnas coexisten sin una diferencia clara en su uso.

- **precio**
  - **Sinónimos habituales:** valor, tarifa, precio de lista, pvp, valor unitario
  - **Significado empresarial:** Valor monetario de referencia de un producto o servicio.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *precio_unitario* cuando en realidad representa un total, o con *costo* si no se aclara el contexto.

- **precio_unitario**
  - **Sinónimos habituales:** p_unit, precio_uni, unit_price, p_unitario
  - **Significado empresarial:** Valor monetario de cada unidad individual de un producto o servicio.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *costo_unitario* o con *precio* total si no se explicita que es "por unidad".

- **importe**
  - **Sinónimos habituales:** monto, valor, suma, amount, valor línea
  - **Significado empresarial:** Resultado monetario de una línea antes de impuestos, descuentos o totales finales.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *total*, *subtotal* o *saldo* según el nivel de agregación de la fila.

- **total**
  - **Sinónimos habituales:** total_linea, importe_total, general, gran total, valor final
  - **Significado empresarial:** Valor monetario final de una operación, línea o documento.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *subtotal* cuando se desconoce si incluye o no impuestos y descuentos.

- **subtotal**
  - **Sinónimos habituales:** sub_total, parcial, neto, total parcial, base imponible
  - **Significado empresarial:** Suma parcial antes de aplicar impuestos, descuentos, envíos o recargos.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *total* o con *importe* neto si el usuario no distingue los niveles de agregación.

- **descuento**
  - **Sinónimos habituales:** dto, bonif, rebaja, discount, desc, bonificación
  - **Significado empresarial:** Reducción aplicada sobre un precio o importe, ya sea por pronto pago, volumen o promoción.
  - **Tipo de dato:** importe / porcentaje
  - **Confusiones frecuentes:** Se confunde con *importe* negativo o con *comisión* cuando se registra como valor absoluto vs. porcentaje.

- **impuesto**
  - **Sinónimos habituales:** tax, tributo, tasa, percepción genérica, retención
  - **Significado empresarial:** Carga fiscal aplicada sobre una operación, distinta del IVA específico o como término agrupador.
  - **Tipo de dato:** importe / porcentaje
  - **Confusiones frecuentes:** Se confunde con *IVA* cuando la columna agrupa varios impuestos sin discriminar.

- **IVA**
  - **Sinónimos habituales:** iva, tax_vat, impuesto al valor agregado, impuesto al valor añadido
  - **Significado empresarial:** Impuesto al valor agregado específico aplicado a la venta o compra de bienes y servicios.
  - **Tipo de dato:** importe / porcentaje
  - **Confusiones frecuentes:** Se confunde con *impuesto* general si el archivo no discrimina otros tributos aplicados.

- **percepción**
  - **Sinónimos habituales:** percepción_ingresos_brutos, percepción_iva, percepción_municipal
  - **Significado empresarial:** Retención anticipada de un impuesto que se practica en la venta o compra y luego se computa.
  - **Tipo de dato:** importe / porcentaje
  - **Confusiones frecuentes:** Se confunde con *impuesto* o con *retención* cuando se agrupan todos los cargos fiscales en una sola columna.

- **retención**
  - **Sinónimos habituales:** retención_iva, retención_ganancias, retención_suss, retención_impuesto
  - **Significado empresarial:** Monto retenido por el cliente o proveedor como pago a cuenta de un tributo.
  - **Tipo de dato:** importe / porcentaje
  - **Confusiones frecuentes:** Se confunde con *descuento* o con *percepción* si se registra como una reducción del importe sin especificar su carácter fiscal.

- **costo**
  - **Sinónimos habituales:** cost, gasto, erogación, valor de compra, costo de adquisición
  - **Significado empresarial:** Desembolso necesario para adquirir o producir lo que se vende, a veces usado en sentido amplio.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *precio* o *venta* cuando el archivo no aclara si es compra o venta; también con *costo de ventas*.

- **costo_unitario**
  - **Sinónimos habituales:** c_unit, costo_uni, unit_cost, costo promedio
  - **Significado empresarial:** Costo de una sola unidad de producto, materia prima o servicio directo.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *precio_unitario* (venta) o con *costo_total* mal dividido por la cantidad.

- **costo_total**
  - **Sinónimos habituales:** costo_tot, total_cost, costo de bienes vendidos, costo lote
  - **Significado empresarial:** Suma completa de los costos de una línea, pedido o período.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *costo_unitario* si se usa el mismo nombre para valores agregados y unitarios.

- **compra**
  - **Sinónimos habituales:** compras, adquisición, provisión, ingreso_mercaderia
  - **Significado empresarial:** Operación de adquisición de bienes o servicios para la empresa.
  - **Tipo de dato:** importe / texto
  - **Confusiones frecuentes:** Se confunde with *costo* o con *entrada* cuando se registra el documento sin discriminar el hecho económico del movimiento físico.

- **compra_total**
  - **Sinónimos habituales:** total_compra, compra_general, adquisición_total
  - **Significado empresarial:** Monto final agregado de una compra o conjunto de compras en un documento o corte.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *pagado* o con *costo_total* si se asume que lo comprado ya fue pagado o producido.

- **stock**
  - **Sinónimos habituales:** inventario, existencia, unidades en depósito, activo físico, disponible
  - **Significado empresarial:** Cantidad de bienes que la empresa tiene para la operación, ya sea total o disponible.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *stock_disponible* si incluye reservas, mercadería en tránsito o dañada.

- **stock_actual**
  - **Sinónimos habituales:** existencia_actual, inventario hoy, saldo físico, stock hoy
  - **Significado empresarial:** Cantidad real que se encuentra en este momento en el depósito o local.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *stock_disponible* cuando hay lotes bloqueados, comprometidos o en revisión.

- **stock_disponible**
  - **Sinónimos habituales:** libre, stock para venta, unidades disponibles, stock usable
  - **Significado empresarial:** Cantidad que puede comprometerse o venderse inmediatamente sin afectar otros pedidos.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *stock_actual* si el sistema no descuenta reservas ni fallas de calidad.

- **stock_mínimo**
  - **Sinónimos habituales:** mínimo, stock_seguridad, punto de pedido, min, stock crítico
  - **Significado empresarial:** Cantidad mínima que debe mantenerse para no romper el abastecimiento o perder ventas.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *stock_actual* si se usa como referencia de pedido sin actualizar el inventario real.

- **entrada**
  - **Sinónimos habituales:** ingreso, recepción, compra física, +stock, ingreso a bodega
  - **Significado empresarial:** Movimiento que aumenta el inventario físico por compra, producción o devolución.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *compra* cuando se registra el documento y no el movimiento físico real.

- **salida**
  - **Sinónimos habituales:** egreso, despacho, consumo, entrega, -stock, merma
  - **Significado empresarial:** Movimiento que reduce el inventario físico por venta, uso interno, merma o robo.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *venta* si incluye donaciones, usos internos o mermas no facturadas.

- **comprobante**
  - **Sinónimos habituales:** comp, nro_comp, documento, voucher, nro_documento
  - **Significado empresarial:** Soporte físico o digital que acredita una operación comercial o contable.
  - **Tipo de dato:** texto / identificador
  - **Confusiones frecuentes:** Se confunde con *factura* cuando la columna agrupa tickets, remitos, notas de crédito y recibos.

- **factura**
  - **Sinónimos habituales:** fac, invoice, nro_factura, ticket, folio
  - **Significado empresarial:** Documento fiscal que detalla una venta o compra y suele tener validez tributaria.
  - **Tipo de dato:** texto / identificador
  - **Confusiones frecuentes:** Se confunde con *comprobante* si la columna incluye otros documentos que no son facturas propiamente dichas.

- **cobrado**
  - **Sinónimos habituales:** recaudado, ingreso efectivo, cobros, recibido, efectivo
  - **Significado empresarial:** Importe efectivamente ingresado por ventas o deudas de clientes.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *venta* cuando se registra lo facturado como si fuera dinero ya recibido.

- **cobranza**
  - **Sinónimos habituales:** cobro, recaudación, gestión de cobro, ingreso, cobranza realizada
  - **Significado empresarial:** Acción, área o monto correspondiente a la recaudación de créditos de clientes.
  - **Tipo de dato:** importe / texto
  - **Confusiones frecuentes:** Se confunde con *cobrado* porque en algunos archivos se usa como sinónimo del monto recaudado.

- **pagado**
  - **Sinónimos habituales:** erogado, desembolsado, liquidado, egreso, abonado
  - **Significado empresarial:** Importe efectivamente entregado a proveedores o terceros por una obligación.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *deuda* o con *pago* si se anota una deuda pendiente como si ya hubiera sido pagada.

- **pago**
  - **Sinónimos habituales:** abono, liquidación, transferencia, cheque, egreso
  - **Significado empresarial:** Acción, documento o evento que acredita una entrega de dinero.
  - **Tipo de dato:** importe / texto
  - **Confusiones frecuentes:** Se confunde con *pagado* cuando la columna representa un compromiso y no un hecho realizado.

- **deuda**
  - **Sinónimos habituales:** obligación, adeudo, monto adeudado, pasivo corto plazo, lo que debo/deben
  - **Significado empresarial:** Monto que se debe a un tercero o que un tercero debe a la empresa.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *saldo* si no se distingue entre deuda total histórica y saldo pendiente actual.

- **saldo**
  - **Sinónimos habituales:** remanente, resto, balance, posición, saldo pendiente
  - **Significado empresarial:** Diferencia entre débitos y créditos; cantidad remanente en una cuenta o documento.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *deuda* cuando representa lo pendiente, o con *stock* si se usa como saldo físico.

- **cuenta**
  - **Sinónimos habituales:** cuenta_contable, cuenta_corriente, cuenta_bancaria, cc, cta
  - **Significado empresarial:** Registro contable, relación de crédito/debito o identificador de una cuenta bancaria.
  - **Tipo de dato:** texto / identificador
  - **Confusiones frecuentes:** Se confunde con *banco* o con *cliente_id* si se usa "cuenta" como sinónimo de cliente.

- **banco**
  - **Sinónimos habituales:** entidad_financiera, institución, banco_emisor, banco receptor
  - **Significado empresarial:** Entidad donde se custodia, transfiere o recibe dinero.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *cuenta* o con *medio_de_pago* si se anota el banco como método de cobro.

- **medio_de_pago**
  - **Sinónimos habituales:** forma_pago, mp, método, instrumento, tarjeta/efectivo/transferencia
  - **Significado empresarial:** Instrumento utilizado para pagar o cobrar una operación.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *banco* o con *pago* cuando se describe la entidad y no el instrumento.

- **comisión**
  - **Sinónimos habituales:** fee, commission, gasto_corredor, cobro por servicio, gasto administrativo
  - **Significado empresarial:** Retribución o costo por intermediación en una operación financiera o comercial.
  - **Tipo de dato:** importe / porcentaje
  - **Confusiones frecuentes:** Se confunde con *impuesto* o con *descuento* si se carga al cliente sin discriminar su naturaleza.

- **ganancia**
  - **Sinónimos habituales:** beneficio, lucro, excedente, earnings, resultado positivo
  - **Significado empresarial:** Diferencia positiva entre ingresos y costos de una operación, antes o después de gastos.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *venta*, *utilidad* o *flujo de caja* según si se consideran todos los gastos o solo los directos.

- **utilidad**
  - **Sinónimos habituales:** profit, resultado, utilidad neta/bruta, earning, beneficio
  - **Significado empresarial:** Excedente después de deducir costos y gastos operativos; puede ser bruta, operativa o neta.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *ganancia* porque en la práctica PyME se usan indistintamente.

- **margen**
  - **Sinónimos habituales:** margen_bruto, margen_contribución, spread, markup, diferencia
  - **Significado empresarial:** Diferencia entre precio de venta y costo, expresada en dinero o como proporción.
  - **Tipo de dato:** importe / porcentaje
  - **Confusiones frecuentes:** Se confunde con *margen_porcentaje* o con *utilidad* cuando el nombre de la columna es ambiguo.

- **margen_porcentaje**
  - **Sinónimos habituales:** %margen, margen %, rentabilidad bruta %, margen sobre venta/costo
  - **Significado empresarial:** Relación porcentual entre la utilidad y el precio de venta o el costo.
  - **Tipo de dato:** porcentaje
  - **Confusiones frecuentes:** Se confunde con *rentabilidad* o con *descuento* porcentual si no se explicita la base de cálculo.

- **rentabilidad**
  - **Sinónimos habituales:** roi, retorno, rendimiento, %rentabilidad, rentabilidad sobre ventas
  - **Significado empresarial:** Capacidad de generar ganancia respecto a una inversión, venta o costo total.
  - **Tipo de dato:** porcentaje / importe
  - **Confusiones frecuentes:** Se confunde con *margen* cuando ambos se calculan sobre bases distintas (ventas vs. inversión).

- **fecha**
  - **Sinónimos habituales:** fecha_emisión, fecha_operación, dia, date, fecha movimiento
  - **Significado empresarial:** Día en que se registra o produce un evento comercial específico.
  - **Tipo de dato:** fecha
  - **Confusiones frecuentes:** Se confunde con *período* o con *vencimiento* si la columna no especifica a qué evento corresponde.

- **período**
  - **Sinónimos habituales:** mes, ejercicio, año-mes, bimestre, trimestre, semana
  - **Significado empresarial:** Intervalo de tiempo contable o de reporte para agrupar operaciones.
  - **Tipo de dato:** texto / fecha
  - **Confusiones frecuentes:** Se confunde con *fecha* cuando se anota una fecha puntual en lugar de un rango o etiqueta de período.

- **vencimiento**
  - **Sinónimos habituales:** fecha_vto, venc, fecha de caducidad, vto, fecha límite
  - **Significado empresarial:** Fecha límite para el pago de una deuda, el cobro de un crédito o el uso de un producto.
  - **Tipo de dato:** fecha
  - **Confusiones frecuentes:** Se confunde con *fecha* de emisión o con *plazo* si se anota en días en vez de fecha calendario.

- **plazo**
  - **Sinónimos habituales:** término, lapso, financiación, condición de pago, crédito
  - **Significado empresarial:** Tiempo acordado para cumplir una obligación de pago o entrega.
  - **Tipo de dato:** días / texto
  - **Confusiones frecuentes:** Se confunde con *vencimiento* cuando se usa como fecha exacta y no como duración en días.

- **días**
  - **Sinónimos habituales:** cant_dias, dias_plazo, duración, antigüedad, días transcurridos
  - **Significado empresarial:** Cantidad de días asociada a un plazo, un retraso, una permanencia o una antigüedad.
  - **Tipo de dato:** días
  - **Confusiones frecuentes:** Se confunde con *cantidad* general si no se especifica que representa una medida de tiempo.

- **fecha_entrega**
  - **Sinónimos habituales:** entrega_estimada, fecha_de_envio, fecha_prometida, delivery_date
  - **Significado empresarial:** Fecha en que se espera o se efectivizó la entrega de un pedido o servicio.
  - **Tipo de dato:** fecha
  - **Confusiones frecuentes:** Se confunde con *fecha* de emisión, con *vencimiento* o con *fecha_pago* si no se aclara el evento.

- **fecha_emisión**
  - **Sinónimos habituales:** fecha_de_alta, fecha_de_registro, fecha_doc, emision
  - **Significado empresarial:** Fecha en que se genera un documento, comprobante o registro.
  - **Tipo de dato:** fecha
  - **Confusiones frecuentes:** Se confunde con *fecha* genérica o con *fecha_entrega* cuando el documento y la entrega son simultáneos.

- **fecha_pago**
  - **Sinónimos habituales:** fecha_de_cobro, fecha_liquidación, fecha_abono, fecha_compromiso
  - **Significado empresarial:** Fecha en que se efectiviza o se compromete el pago de una obligación.
  - **Tipo de dato:** fecha
  - **Confusiones frecuentes:** Se confunde con *vencimiento* cuando se registra la fecha límite como si fuera la fecha de pago real.

- **proyecto**
  - **Sinónimos habituales:** proyecto_id, obra, contrato, job, assignment
  - **Significado empresarial:** Conjunto de tareas y recursos orientados a un objetivo específico de servicio o construcción.
  - **Tipo de dato:** texto / identificador
  - **Confusiones frecuentes:** Se confunde con *orden_de_trabajo* o con *pedido* cuando un proyecto se gestiona como una única venta.

- **proyecto_id**
  - **Sinónimos habituales:** id_proyecto, cod_proyecto, nro_proyecto, cod_obra
  - **Significado empresarial:** Código único que identifica un proyecto.
  - **Tipo de dato:** identificador
  - **Confusiones frecuentes:** Se confunde con *pedido_id* o con *cliente_id* si la numeración de proyectos sigue la de clientes.

- **etapa**
  - **Sinónimos habituales:** hito, milestone, fase, subproyecto, etapa_proyecto
  - **Significado empresarial:** Periodo o parte definida dentro de un proyecto.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *tarea* o con *proyecto* cuando las etapas se nombran como si fueran proyectos independientes.

- **consultor**
  - **Sinónimos habituales:** recurso, profesional, ejecutor, responsable, asignado
  - **Significado empresarial:** Persona que presta un servicio profesional o especializado dentro de un proyecto.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde with *vendedor* o con *técnicos* cuando el mismo personal cumple roles comerciales y de ejecución.

- **horas_contratadas**
  - **Sinónimos habituales:** horas_presupuestadas, horas_comprometidas, horas_proyecto
  - **Significado empresarial:** Cantidad de horas acordadas con el cliente para la ejecución de un servicio o proyecto.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *horas_ejecutadas* o con *horas_facturables* si se registran como horas ya trabajadas.

- **horas_ejecutadas**
  - **Sinónimos habituales:** horas_realizadas, horas_invertidas, horas_cargadas, horas_imputadas
  - **Significado empresarial:** Cantidad de horas efectivamente dedicadas a un proyecto o tarea.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *horas_facturables* cuando se incluyen horas no cobrables o de capacitación.

- **tarifa_horaria**
  - **Sinónimos habituales:** precio_hora, rate, valor_hora, costo_hora_profesional
  - **Significado empresarial:** Valor monetario de una hora de servicio profesional o técnico.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *costo_hora* (costo interno) o con *precio_unitario* cuando se vende por unidades de tiempo.

- **costo_hora**
  - **Sinónimos habituales:** costo_por_hora, costo_recurso, costo_técnico, costo_directo_hora
  - **Significado empresarial:** Costo interno de una hora de trabajo de un empleado o consultor.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *tarifa_horaria* (precio de venta) o con *mano_de_obra* si se expresa en dinero acumulado.

- **sucursal**
  - **Sinónimos habituales:** branch, filial, depósito, punto de venta, local, bodega
  - **Significado empresarial:** Unidad operativa o física donde se realiza una operación, venta o almacenamiento.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *vendedor* o con *planta* si se usan indistintamente en archivos centralizados.

- **vendedor**
  - **Sinónimos habituales:** seller, comercial, representante, agente, cobrador, promotor
  - **Significado empresarial:** Persona responsable de concretar la venta o atender al cliente.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *empleado* general o con *cobranza* si también realiza la gestión de cobro.

- **empleado**
  - **Sinónimos habituales:** personal, colaborador, staff, trabajador, recurso humano, operario
  - **Significado empresarial:** Persona contratada por la empresa para desarrollar tareas operativas, administrativas o comerciales.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *vendedor* cuando todos los empleados registrados pertenecen al área comercial.

- **centro_de_distribución**
  - **Sinónimos habituales:** cd, depósito, almacén, bodega, hub_logístico
  - **Significado empresarial:** Instalación desde la cual se almacena y distribuye mercadería.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *sucursal* o con *planta* cuando todos los locales se registran con nombres genéricos.

- **zona**
  - **Sinónimos habituales:** ruta, área, territorio, región, distrito, barrio
  - **Significado empresarial:** Segmento geográfico o comercial para organizar ventas, cobros o entregas.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *ruta* o con *sucursal* cuando se asignan clientes a zonas que en realidad son puntos de venta.

- **ruta**
  - **Sinónimos habituales:** ruta_de_entrega, ruta_de_cobro, itinerario, circuito
  - **Significado empresarial:** Camino o secuencia definida para realizar entregas o visitas comerciales.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *zona* o con *transporte* cuando se usa como sinónimo de área geográfica o vehículo.

- **transporte**
  - **Sinónimos habituales:** vehiculo, flota, unidad_de_transporte, camión, movilidad
  - **Significado empresarial:** Medio utilizado para el traslado de mercadería o personal.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *costo_de_envío* o con *guia* cuando se anota el nombre del vehículo como gasto de logística.

- **peso**
  - **Sinónimos habituales:** peso_total, peso_bruto, peso_neto, kg, gramos
  - **Significado empresarial:** Masa de la mercadería transportada o almacenada.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *cantidad* o con *volumen* cuando se usa como proxy de cantidad sin conversión.

- **volumen**
  - **Sinónimos habituales:** m3, volumen_total, capacidad_ocupada, espacio
  - **Significado empresarial:** Espacio físico ocupado por la mercadería transportada o almacenada.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *peso* o con *cantidad* cuando se usa para calcular cargas sin distinción de densidad.

- **bultos**
  - **Sinónimos habituales:** cantidad_bultos, paquetes, cajas, pallets, unidades_de_carga
  - **Significado empresarial:** Cantidad de envases o agrupaciones físicas de mercadería.
  - **Tipo de dato:** cantidad
  - **Confusiones frecuentes:** Se confunde con *cantidad* de unidades internas cuando un bulto contiene varias piezas.

- **estado**
  - **Sinónimos habituales:** situación, condición, status, etapa, flag
  - **Significado empresarial:** Descriptor del estado de un proceso, documento o ítem (activo, pendiente, anulado, entregado).
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *estado_envío* o con *condición* de pago cuando una sola columna resume todo el proceso.

- **moneda**
  - **Sinónimos habituales:** divisa, tipo_moneda, currency, pesos, euros, dolares
  - **Significado empresarial:** Unidad monetaria en la que se expresa un importe.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *tipo_de_cambio* cuando se usa el símbolo de moneda como si fuera una tasa de conversión.

- **tipo_de_cambio**
  - **Sinónimos habituales:** tc, cotización, exchange_rate, valor_moneda, factor_conversion
  - **Significado empresarial:** Relación de equivalencia entre dos monedas en una fecha determinada.
  - **Tipo de dato:** importe
  - **Confusiones frecuentes:** Se confunde con *moneda* o con *precio* cuando se usa para convertir valores sin aclarar la moneda origen.

- **condicion_de_pago**
  - **Sinónimos habituales:** cond_pago, términos_de_pago, forma_de_pago, política_de_pago
  - **Significado empresarial:** Reglas acordadas para el pago de una operación (contado, 30 días, etc.).
  - **Tipo de dato:** texto / días
  - **Confusiones frecuentes:** Se confunde con *medio_de_pago* o con *plazo* cuando se anota el instrumento en lugar de la condición.

- **observaciones**
  - **Sinónimos habituales:** notas, glosa, comentarios, detalle, referencia_adicional
  - **Significado empresarial:** Texto libre que complementa la información de una operación sin alterar su valor contable.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *diagnostico* o con *garantía* cuando las notas técnicas se mezclan con notas administrativas.

- **contacto**
  - **Sinónimos habituales:** interlocutor, persona_de_contacto, referente, atención
  - **Significado empresarial:** Persona dentro de la organización del cliente o proveedor con quien se trata una operación.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *cliente* o con *vendedor* cuando se usa el nombre del contacto como identificador principal de la empresa.

- **direccion**
  - **Sinónimos habituales:** domicilio, ubicación, calle, dirección_fiscal, dirección_entrega
  - **Significado empresarial:** Ubicación física asociada a un cliente, proveedor o punto de operación.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *sucursal* o con *zona* cuando se usa la dirección como agrupador geográfico.

- **localidad**
  - **Sinónimos habituales:** ciudad, municipio, provincia, departamento, estado, país
  - **Significado empresarial:** División geográfica administrativa asociada a una dirección o zona de operación.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *zona* comercial o con *sucursal* cuando las localidades se usan como centros de responsabilidad.

- **codigo_postal**
  - **Sinónimos habituales:** cp, zip, postal_code, zip_code
  - **Significado empresarial:** Código oficial de identificación de una zona geográfica para envíos o ubicación.
  - **Tipo de dato:** identificador / texto
  - **Confusiones frecuentes:** Se confunde con *cliente_id* o con *zona* cuando se usa como clave de agrupación de clientes.

- **telefono**
  - **Sinónimos habituales:** tel, celular, whatsapp, contacto_telefonico, linea
  - **Significado empresarial:** Número de contacto telefónico de un cliente, proveedor o empleado.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *cliente_id* cuando se usa como identificador único en pequeñas bases informales.

- **email**
  - **Sinónimos habituales:** correo, e-mail, mail, direccion_de_correo
  - **Significado empresarial:** Dirección de correo electrónico de contacto.
  - **Tipo de dato:** texto
  - **Confusiones frecuentes:** Se confunde con *cliente_id* o con *contacto* cuando se usa como clave principal de una persona.
