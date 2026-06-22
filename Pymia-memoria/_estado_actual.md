# PymIA Memoria — Estado actual

Fecha: 2026-06-22

## Estado operativo actual

Repo principal:

```text
E:\BuenosPasos\smartbridge\PymIA
```

Subcarpeta viva:

```text
PymIA-Live
```

GitHub:

```text
smartdash-almasana/PymIA
```

## Estado git reciente

Último bloque reportado como pusheado:

```text
fe582c1 SERVICE_1_OPERATOR_DELIVERY_PACKAGE_BLOCK_V1
PUSH: SUCCESS
WORKING_TREE: CLEAN
TEST_RESULT: 421 passed
```

Commits relevantes de la cadena Servicio 1 First Aid:

```text
fe582c1 service 1 operator delivery package block
c586e6d test(pymia-live): audit service 1 operator harness outputs
33be021 feat(pymia-live): add service 1 operator harness
bca683e feat(pymia-live): add service 1 first aid pipeline
22e420d docs(pymia): close service 1 first aid manual lane
b3f16b8 feat(pymia-live): add service 1 semi-real first aid case
6b6f6a1 docs(pymia): add service 1 manual operator runbook
017a9a7 feat(pymia-live): add service 1 manual first aid smoke case
0f247fa fix(pymia-live): avoid first aid delivery filename collisions
97f0a5d feat(pymia-live): add service 1 manual first aid delivery flow
496ddff feat(pymia-live): add first aid delivery aggregate
9e03833 feat(pymia-live): add first aid xlsx delivery
eb8b124 docs(pymia): close first aid minimal toolset
368fed4 feat(pymia-live): add first aid stock alerts tool
b436a9e feat(pymia-live): add first aid daily cash triage tool
6ecdce2 feat(pymia-live): add first aid price margin tool
fe7dc79 feat(pymia-live): add first aid tool result contract
```

## Capacidad cerrada actual

```text
SERVICE_1_OPERATOR_DELIVERY_PACKAGE_BLOCK_V1 = CLOSED / PUSHED
```

Cadena operable:

```text
operator harness
→ pipeline explícito
→ tools allowlist
→ FirstAidToolResultV1[]
→ aggregate
→ XLSX por tool
→ summary.txt
→ operator_report.txt
→ README_ENTREGA.md
→ manifest.json
→ hashes + bytes
→ carpeta final entregable
```

Inventario final del paquete:

```text
README_ENTREGA.md
manifest.json
summary.txt
operator_report.txt
first_aid_001_precio_margen_basico.xlsx
first_aid_002_caja_diaria_triage.xlsx
first_aid_003_stock_alertas_basicas.xlsx
```

Evidencia:

```text
421 passed
36 passed en bloque pedido por Codex
41 passed en validación ampliada con audit anterior
```

## Metodología vigente

Se abandona el microciclo archivo-por-archivo.

Cadencia nueva:

```text
1 bloque funcional
→ Codex ejecuta varias piezas relacionadas
→ tests amplios del bloque
→ reporte único
→ auditoría única
→ commit/push único
```

Tamaño sano de bloque:

```text
1 capacidad operable
3–8 archivos
30–100+ tests focales o suite relevante
1 commit
1 push
```

No volver al ping-pong:

```text
pedir permiso por archivo
commit por archivo
push por micro-slice
closeout documental después de cada paso técnico
```

## Servicio 1 First Aid — Estado de producto

Estado:

```text
CAPACIDAD OPERABLE ASISTIDA
NO PRODUCTO FULL
```

Se puede mostrar/probar como:

```text
Servicio asistido manual de primeros auxilios operacionales sobre datos declarados.
Entrega preliminar con XLSX + resumen + manifest.
Revisión rápida de margen, caja diaria y stock crítico.
```

No vender como:

```text
diagnóstico integral de empresa
certificación contable
conciliación bancaria cerrada
validación de saldo bancario real
validación de stock físico real
rentabilidad real confirmada
sistema autónomo
chatbot productivo
pipeline contable completo
```

## Fronteras prohibidas vigentes

```text
No chatbot.
No LLM.
No FSM productiva.
No document_ingestion real.
No Exceland.
No conciliación bancaria.
No Mercado Pago.
No IVA/IIBB.
No asientos contables.
No vertical_slice.py.
No ERP/Odoo.
```

## Próximo foco recomendado

Pasar de capacidad técnica entregable a decisión comercial/piloto:

```text
SERVICE_1_FIRST_AID_PILOT_OFFER_V1
```

Objetivo del próximo bloque:

```text
definir oferta piloto mínima
alcance
precio orientativo
checklist de intake manual
criterios de aceptación del caso
qué recibe el cliente
qué no recibe
script operador/venta
```

Categoría:

```text
A. CAPACIDAD OPERATIVA / PRODUCTIZACIÓN PILOTO
```

No abrir más runtime hasta que exista decisión de piloto real o caso real.
