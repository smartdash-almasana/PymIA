# SERVICE_1_XLSX_FORMULA_POLICY_V1

## Estado

```text
Tipo: PRODUCT_DECISION / FORMULA_POLICY
Estado: DECIDED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
Commit autorizado: NO
Push autorizado: NO
```

## Veredicto

```text
XLSX_FORMULA_POLICY_V1: APPROVED
ROADMAP_FORMULA_FAMILY_REMAINS_ACTIVE: YES
FIRST_AID_DELIVERY_MUST_REMAIN_NO_FORMULAS: YES
FORMULA_ENABLED_XLSX_BELONGS_TO_FACTORY_PATH: YES
HARDCODED_FORMULAS_IN_KERNEL_ALLOWED: NO
```

## Propósito

Resolver la contradicción detectada entre:

- el roadmap full, que exige **Excel descargables con fórmulas**;
- y el delivery actual de Servicio 1, que declara explícitamente:
  - `No formulas, macros, or runtime execution were used.`

Esta decisión no cambia código.

Fija la política de producto que separa correctamente:

- el delivery seguro y determinístico actual;
- de la familia futura de XLSX con fórmulas activas.

## Decisión central

```text
La familia “Excel descargables con fórmulas” se mantiene como parte válida de Servicio 1 full.

Pero NO pertenece al delivery genérico actual ni al carril First Aid asistido local.
```

## Regla de separación

### 1. Delivery actual seguro

Los siguientes módulos quedan explícitamente congelados como **no-fórmulas**:

- `pymia/smartpyme/service_1_xlsx_delivery_v1.py`
- `pymia/smartpyme/first_aid_xlsx_delivery_v1.py`

Su rol es:

```text
exportar resultados descriptivos,
determinísticos,
sin macros,
sin fórmulas activas,
sin runtime autónomo.
```

### 2. XLSX con fórmulas activas

La familia de fórmulas activas queda reservada para:

```text
Factoría Excel / Exceland
```

y sólo puede abrirse cuando exista:

1. fuente gobernada de fórmulas;
2. frontera controlada de generación;
3. tests de activación de fórmulas;
4. validación de límites de claims.

## Qué significa esto en producto

### Lo que queda decidido

```text
Primeros Auxilios y delivery genérico:
NO usan fórmulas activas.

Factoría Excel:
SÍ puede producir XLSX con fórmulas activas,
pero sólo como familia separada y gobernada.
```

### Lo que queda prohibido

```text
forzar fórmulas dentro del delivery actual
hardcodear fórmulas en el kernel
llamar “con fórmulas” al delivery actual
usar fórmulas activas sin resolver antes la dependencia Exceland/factory
```

## Fuente permitida de fórmulas

Las fórmulas activas, si se habilitan, deben venir de:

```text
specs / templates / catálogos gobernados
```

No de:

```text
lógica ad hoc metida en el kernel
strings sueltos
cálculos improvisados en delivery genérico
```

## Impacto sobre las familias del roadmap

| Familia | Efecto de esta decisión |
|---|---|
| Primeros Auxilios | sigue usando delivery sin fórmulas |
| Laboratorio Excel | no cambia |
| Factoría Excel | pasa a ser dueña de la salida con fórmulas activas |
| Excel descargables con fórmulas | sigue siendo target válido, pero movido al carril de factoría |
| Servicios para contadores | puede reutilizar delivery seguro o futuro carril con fórmulas, según contrato |

## Condición de cierre de la familia “Excel descargables con fórmulas”

La familia D sólo podrá marcarse cerrada cuando:

```text
1. Factoría Excel deje de depender ambiguamente de un path externo;
2. exista generación física controlada de XLSX con fórmulas activas;
3. haya tests que prueben celdas fórmula activas;
4. exista política explícita de claims permitidos/prohibidos;
5. la salida no rompa los límites de revisión humana.
```

## Resultado inmediato sobre el programa

Esta decisión resuelve la contradicción de producto sin obligar a:

```text
romper el delivery actual,
meter fórmulas en First Aid,
o reescribir la lane asistida local.
```

## Próximo paso autorizado

```text
ETAPA 2 — CIERRE REAL DE PRIMEROS AUXILIOS
```

Porque la contradicción de fórmulas ya quedó resuelta por política, y ahora el siguiente cierre real es completar la familia First Aid dentro del roadmap grande.
