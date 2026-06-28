# SERVICE_1_QA_CLAIMS_AND_REPRESENTATIVE_DELIVERY_CASE_V1

## Estado

```text
DOCUMENT_TYPE: QA_AND_REPRESENTATIVE_DELIVERY_CASE
SERVICE: SERVICE_1_FULL_ASSISTED_V1
STATUS: CLOSED_WITH_LIMITS
RUNTIME_MODIFIED: NO
TESTS_RUN: NO
NEW_XLSX_CREATED: NO
STAGE_6: NO
AGENT_LLM: NO
```

---

# 1. Qué es este documento

Este documento cierra el control de claims prohibidos y define un caso representativo de entrega final para Servicio 1 Full Assisted V1.

No crea una demo teatral.
No inventa producto nuevo.
No abre runtime.
No agrega agente LLM.
No redefine Servicio 1.

---

# 2. Corrección terminológica

Término prohibido para esta etapa:

```text
caso estrella
```

Término correcto:

```text
caso representativo de entrega final
```

Razón:

```text
El objetivo no es marketing ni demostración escénica.
El objetivo es probar que un caso ya soportado puede entregarse al cliente usando el paquete estándar, sin prometer de más.
```

---

# 3. Caso representativo elegido

```text
CASE_ID: SERVICE_1_REPRESENTATIVE_DELIVERY_CASE_001
CASE_NAME: Revisión inicial de precios, costos y márgenes
SOURCE_FILE: cafeteria_abc.xlsx
PRIMARY_CAPABILITY: precio_margen_basico
CASE_STATUS: SUPPORTED_EXISTING_CASE
DELIVERY_STANDARD: SERVICE_1_PAQUETE_ENTREGA_CLIENTE_ESTANDAR_V1
```

---

# 4. Por qué este caso

Se elige `precio_margen_basico` sobre `cafeteria_abc.xlsx` porque:

```text
- es una familia ya soportada;
- tiene evidencia previa: 15/15 OK;
- no toca caja ni banco;
- no promete conciliación;
- es entendible para dueño PyME;
- permite validar el paquete cliente estándar;
- tiene menor ambigüedad que gastos, caja o proveedores.
```

---

# 5. Frontera sana

Permitido:

```text
- aplicar QA de claims;
- usar un caso existente;
- validar paquete de entrega cliente;
- verificar lenguaje owner-facing;
- declarar evidencia recibida;
- declarar límites;
- declarar próximos pedidos;
- declarar revisión humana requerida.
```

Prohibido:

```text
- inventar producto nuevo;
- abrir runtime nuevo;
- crear demo teatral;
- redefinir Servicio 1;
- meter agente LLM;
- habilitar Stage 6;
- afirmar auditoría;
- afirmar rentabilidad real integral;
- afirmar diagnóstico integral de empresa.
```

---

# 6. Claims prohibidos generales

Servicio 1 no debe prometer:

```text
- diagnóstico integral de empresa;
- auditoría fiscal o contable;
- rentabilidad real garantizada;
- margen real contable definitivo;
- datos correctos o completos;
- ausencia de errores;
- reemplazo del contador;
- autonomía plena;
- chatbot productivo;
- integración automática bancaria/API;
- conciliación bancaria cerrada;
- saldo bancario real confirmado;
- stock físico real confirmado.
```

---

# 7. Lenguaje permitido general

Se permite decir:

```text
- revisión asistida;
- revisión inicial;
- triage operativo;
- cálculo preliminar;
- evidencia declarada;
- según los datos recibidos;
- según la hoja analizada;
- con estas columnas;
- paquete de trabajo para revisión humana;
- salida owner-facing con caveats;
- requiere revisión humana.
```

---

# 8. Claims específicos para precios, costos y márgenes

## Permitido

```text
- margen básico calculado sobre precio y costo declarados;
- productos con margen observable;
- productos con datos faltantes;
- revisión inicial de precios y costos;
- productos que conviene revisar comercialmente;
- resultados válidos según datos recibidos.
```

## Prohibido

```text
- rentabilidad real de la empresa;
- margen contable definitivo;
- precios correctos;
- costos reales confirmados;
- utilidad neta;
- recomendación automática de cambio de precios;
- política comercial óptima;
- diagnóstico financiero integral.
```

---

# 9. Paquete esperado para el caso representativo

Debe poder expresarse bajo esta estructura:

```text
ENTREGA_SERVICIO_1_CAFETERIA_ABC_<FECHA>/
├─ 00_LEEME_PRIMERO.md
├─ 01_RESUMEN_DUENO.md
├─ 02_EVIDENCIA_RECIBIDA.md
├─ 03_HALLAZGOS_Y_ALERTAS.md
├─ 04_LIMITES_CAVEATS_Y_NO_ALCANCE.md
├─ 05_PROXIMOS_PEDIDOS.md
├─ 06_PROXIMAS_ACCIONES_SUGERIDAS.md
├─ outputs/
│  └─ first_aid_001_precio_margen_basico.xlsx
├─ tecnico/
│  ├─ manifest.json
│  ├─ summary.txt
│  └─ operator_report.txt
└─ README_ENTREGA.md
```

No es obligatorio que estén presentes los XLSX de caja, stock, gastos o proveedores si no fueron parte del caso.

---

# 10. Contenido mínimo del caso

## 00_LEEME_PRIMERO.md

Debe decir:

```text
Esta entrega contiene una revisión inicial de precios, costos y márgenes sobre el archivo recibido.
Debe leerse como primeros auxilios operativos sobre datos declarados.
No es auditoría, certificación, diagnóstico integral ni cálculo contable definitivo.
```

## 01_RESUMEN_DUENO.md

Debe incluir:

```text
- archivo recibido: cafeteria_abc.xlsx;
- área revisada: precios, costos y margen básico;
- herramienta aplicada: precio_margen_basico;
- resultados válidos: 15;
- datos inválidos: 0;
- datos faltantes: 0;
- estado: DELIVERED_WITH_CAVEATS;
- próxima acción segura.
```

## 02_EVIDENCIA_RECIBIDA.md

Debe incluir:

```text
EVIDENCIA_DECLARADA:
- archivo cafeteria_abc.xlsx;
- hoja de productos;
- columnas equivalentes a producto, precio y costo.

EVIDENCIA_FALTANTE:
- impuestos, descuentos, comisiones, logística, financiación y otros costos no declarados si no figuran en el archivo.
```

## 03_HALLAZGOS_Y_ALERTAS.md

Debe describir hallazgos sin exagerar:

```text
HALLAZGO:
Los productos procesados tienen margen básico calculable según precio y costo declarados.

EVIDENCIA:
15 resultados válidos sobre los datos recibidos.

IMPACTO POSIBLE:
Permite revisar consistencia comercial inicial.

LIMITE:
No confirma rentabilidad real integral ni margen contable definitivo.

PROXIMO PASO:
Contrastar con costos completos, descuentos, impuestos y política comercial.
```

## 04_LIMITES_CAVEATS_Y_NO_ALCANCE.md

Debe incluir:

```text
No valida impuestos.
No confirma costos reales completos.
No confirma utilidad neta.
No decide precios.
No reemplaza revisión humana ni contable.
No diagnostica integralmente la empresa.
```

## 05_PROXIMOS_PEDIDOS.md

Debe pedir evidencia concreta:

```text
- costos actualizados si hay costos no cargados;
- descuentos reales si existen;
- impuestos o comisiones si afectan precio final;
- lista de productos vigentes si el archivo no está actualizado;
- criterio comercial esperado por margen.
```

## 06_PROXIMAS_ACCIONES_SUGERIDAS.md

Debe sugerir acciones seguras:

```text
- revisar productos con margen bajo o atípico;
- confirmar costos declarados;
- agregar costos faltantes antes de decidir precios;
- repetir corrida con evidencia ampliada;
- usar el archivo como base para conversación con contador o responsable comercial.
```

---

# 11. Checklist QA de claims

Antes de entregar el caso representativo:

```text
[ ] No aparece “caso estrella”.
[ ] No aparece “demo estrella”.
[ ] No aparece “auditoría”.
[ ] No aparece “certificación”.
[ ] No aparece “rentabilidad real”.
[ ] No aparece “margen contable definitivo”.
[ ] No aparece “datos correctos”.
[ ] No aparece “sin errores”.
[ ] No aparece “diagnóstico integral”.
[ ] No aparece “reemplaza al contador”.
[ ] No aparece “la IA resolvió automáticamente”.
[ ] Sí aparece “según datos declarados”.
[ ] Sí aparece “revisión inicial”.
[ ] Sí aparece “requiere revisión humana”.
[ ] Sí aparecen caveats.
[ ] Sí aparecen próximos pedidos.
```

---

# 12. Estado de cierre

```text
QA_CLAIMS: CLOSED_WITH_LIMITS
REPRESENTATIVE_DELIVERY_CASE: SELECTED
CASE_SELECTED: precio_margen_basico sobre cafeteria_abc.xlsx
RUNTIME_REQUIRED: NO
NEXT_FRONT: ensayo operativo del paquete estándar o declaración final SERVICE_1_FULL_ASSISTED_V1
```

---

# 13. Cierre

Servicio 1 puede usar `precio_margen_basico` sobre `cafeteria_abc.xlsx` como caso representativo de entrega final, siempre que se entregue bajo el estándar cliente y con claims conservadores.

Este documento no habilita V2 ni autonomía. Sólo cierra QA de lenguaje y selección segura de caso representativo.
