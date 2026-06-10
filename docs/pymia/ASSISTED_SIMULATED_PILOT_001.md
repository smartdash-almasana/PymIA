# ASSISTED_SIMULATED_PILOT_001

Fecha: 2026-06-10
Estado: READY_TO_RUN
Tipo: simulación operativa controlada

## 1. Veredicto

Este documento abre una simulación asistida del flujo SmartPyme.

No es piloto real.
No valida mercado.
No valida disposición a pagar.
No cierra TD-004.

Sirve para ensayar el flujo integrado actual y medir fricción operativa antes de tener un caso real.

## 2. Objetivo

Simular un caso PyME completo usando el estado actual de PymIA:

```text
F1 primer contacto
→ ficha inicial
→ evidencia simulada
→ bridge + OwnerFacingReport
→ owner_questions_bundle
→ respuesta simulada del dueño
→ reporte actualizado
```

## 3. Restricciones

La simulación NO autoriza:

- Telegram;
- Hermes;
- ERP;
- PDF productivo;
- nuevas fórmulas;
- nuevos reportes;
- runtime externo;
- cambios en graph, bridge o DiagnosticCore;
- refactors;
- prometer producto automático;
- cerrar TD-004.

## 4. Caso simulado

Empresa simulada:

```text
La Textil Cosida SRL
```

Perfil operativo:

```text
Fabrica ropa básica y vende por mayor.
Usa Excel para ventas, compras y costos.
El dueño no sabe si gana plata porque el margen parece achicarse.
```

Primer mensaje simulado:

```text
Hola, fabrico ropa y vendo por mayor. No sé si estoy ganando plata porque cada vez compro más tela y me queda menos margen.
```

## 5. Evidencia simulada

Puede usarse fixture existente si está disponible:

```text
prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
```

Si no se usa fixture, la evidencia debe declararse explícitamente como simulada.

Variables mínimas esperadas:

```text
ventas
costos/compras
productos/SKU
cantidades
precios
periodo
```

## 6. Guion operativo

### Paso 1 — Primer contacto

Entrada:

```text
Hola, fabrico ropa y vendo por mayor. No sé si estoy ganando plata porque cada vez compro más tela y me queda menos margen.
```

Esperado:

- fase `FICHA_PYME_INICIAL`;
- `profile_step = ASK_CONTACT_NAME`;
- `raw_first_message` preservado;
- posible `preliminary_taxonomy` en `PRELIMINARY`;
- `has_taxonomy = False`;
- `has_confirmed_taxonomy = False`;
- sin hipótesis;
- sin evidence_requests;
- sin diagnóstico.

### Paso 2 — Ficha inicial

Completar ficha simulada:

```text
Nombre: Juan Pérez
Empresa: La Textil Cosida SRL
Actividad: fabrico o produzco
Rubro: textil / indumentaria
Equipo: 2 a 5 personas
Canales: mayorista + marketplace
Herramientas: Excel / Google Sheets
Catálogo: lista de precios Excel
Dolor principal: no sé si gano plata
Período: últimos 3 meses
Evidencia: ventas, costos, lista de precios, Excel mezclado
Rol: dueño
Teléfono: simulado
Email: simulado
```

Esperado:

- ficha completa;
- taxonomía confirmable sólo desde profile_data confirmado;
- no usar preliminary_taxonomy como confirmación automática.

### Paso 3 — Evidencia

Ingresar documento/Excel simulado.

Esperado:

- intake/evidence bridge;
- OwnerFacingReport;
- owner_questions_bundle si falta evidencia o sentido;
- no inventar columnas;
- no inventar causalidad.

### Paso 4 — Preguntas al dueño

Registrar preguntas generadas para el dueño.

Medir:

- cantidad de preguntas;
- claridad;
- si son respondibles por un dueño PyME;
- si piden evidencia o sentido necesario;
- si evitan tecnicismos.

### Paso 5 — Respuesta simulada del dueño

Respuesta sugerida:

```text
Los productos Remera Básica y Buzo Frisa son los que más vendo. En mayo subió mucho la tela y no actualicé todos los precios. Algunas ventas mayoristas tienen descuento especial.
```

Esperado:

- reentry de owner answer;
- bridge projection;
- reporte actualizado;
- no reejecutar adapter conversacional;
- no reejecutar DiagnosticCore legacy.

## 7. Métricas de simulación

Registrar:

```text
tiempo operativo total
cantidad de pasos manuales
fricciones detectadas
preguntas ambiguas
preguntas útiles
evidencia faltante
calidad del OwnerFacingReport
comprensión esperada del dueño
riesgo de promesa comercial excesiva
```

## 8. Criterios de PASS

La simulación pasa si:

- el flujo F1 → F2 → F3 puede ensayarse sin abrir features nuevas;
- el sistema mantiene límites de taxonomía preliminar;
- el reporte visible no afirma más que la evidencia disponible;
- las preguntas al dueño son operativas;
- el proceso deja claro qué faltaría para un piloto real.

## 9. Criterios de FAIL

La simulación falla si:

- se diagnostica en primer turno;
- preliminary_taxonomy se trata como confirmada;
- se pide evidencia antes de ficha habilitante;
- se inventa causalidad;
- se promete automatización productiva;
- se confunde simulación con validación real.

## 10. Resultado pendiente

Estado actual:

```text
READY_TO_RUN
```

La ejecución de la simulación debe registrarse en un checkpoint separado:

```text
ASSISTED_SIMULATED_PILOT_001_CHECKPOINT.md
```
