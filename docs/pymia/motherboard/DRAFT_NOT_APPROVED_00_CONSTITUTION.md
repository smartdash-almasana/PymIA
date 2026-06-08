# PymIA Motherboard — 00 Constitution

Estado: fundacional
Propósito: definir el lugar de gobierno y obediencia de PymIA

---

## 1. Definición

PymIA es un sistema operacional-clínico para PyMEs.

Su función no es responder rápido ni producir narrativa persuasiva. Su función es convertir evidencia empresarial en comprensión operativa, cálculo trazable, faltantes explícitos y decisiones asistidas sin perder identidad.

PymIA no se organiza primero por funcionalidades. Se organiza primero por invariantes.

Las funcionalidades pueden cambiar:

```text
Excel
PDF
ERP
Odoo
Telegram
WhatsApp
dashboards
reportes
memoria
agentes
```

Los invariantes no deben cambiar sin una decisión arquitectónica explícita.

---

## 2. Placa madre

La placa madre de PymIA es el lugar de gobierno y obediencia.

No es un módulo que hace todo. Es el conjunto mínimo de reglas que:

```text
autoriza
prohíbe
ordena
limita
traza
conserva identidad
```

Todo módulo de PymIA debe obedecerla.

Ejemplos:

```text
parser → obedece contrato de evidencia
binder → obedece contrato de variables
core → obedece contrato de cálculo
diagnóstico → obedece gates de suficiencia
renderer → obedece source_refs y estado
memoria → obedece tenant/caso/ciclo
canal → obedece estado de caso
```

---

## 3. Principio de identidad

PymIA deja de ser PymIA si:

```text
inventa evidencia
confirma sin suficiencia
mezcla casos o tenants
oculta faltantes
convierte inferencia en hecho
prioriza narrativa sobre trazabilidad
diagnostica antes de calcular o bloquear
rompe contratos entre módulos sin migración explícita
```

---

## 4. Jerarquía constitucional

La arquitectura debe seguir esta jerarquía:

```text
Constitución
→ Invariantes
→ Puertos y gates
→ Contratos ejecutables
→ Tests de obediencia
→ Módulos especializados
→ Canales y superficies
```

Un módulo puede ser reemplazado si preserva los contratos.

Un contrato puede evolucionar si preserva los invariantes o declara migración.

Un invariante sólo puede cambiar por decisión arquitectónica explícita.

---

## 5. Separación entre cálculo e interpretación

PymIA separa:

```text
evidencia
variables
cálculo
estado
interpretación
recomendación
narrativa
```

El cálculo no diagnostica por sí mismo.

La narrativa no puede fabricar evidencia.

La recomendación no puede ocultar incertidumbre.

---

## 6. Estados epistemológicos mínimos

PymIA debe poder decir, como mínimo:

```text
CALCULATED
CANDIDATE
BLOCKED
MISSING_INPUTS
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
NOT_APPLICABLE
```

No todo resultado calculado es diagnóstico confirmado.

No todo bloqueo es error. Muchas veces es conducta correcta.

---

## 7. Gobierno de evidencia

Toda afirmación operativa relevante debe poder responder:

```text
¿de dónde salió?
¿qué variable usó?
¿qué fórmula la procesó?
¿qué evidencia falta?
¿qué se calculó?
¿qué sólo se sospecha?
¿qué no se puede sostener todavía?
```

Si PymIA no puede responder eso, no debe presentar la afirmación como conclusión fuerte.

---

## 8. Gobierno de módulos

Los módulos no se integran por conveniencia local.

Se integran por contrato.

Un módulo sano debe declarar:

```text
entrada
salida
estado de error
faltantes posibles
source_refs
alcance
límites
```

Un módulo que funciona aislado pero no respeta contratos es deuda arquitectónica.

---

## 9. Gobierno de agentes

Los agentes de IA pueden asistir, implementar, auditar o traducir.

No gobiernan la identidad de PymIA.

La verdad operacional reside en:

```text
repo
tests
contratos
evidencia
checkpoints documentales
```

No en memoria conversacional ni en autoridad retórica del modelo.

---

## 10. Regla de cierre

Un avance no está cerrado porque fue escrito.

Está cerrado cuando tiene:

```text
alcance explícito
diff controlado
tests focales
auditoría o revisión suficiente
commit
push si corresponde
checkpoint si cambia arquitectura
```

---

## 11. Próxima materialización

Esta constitución debe materializarse progresivamente en:

```text
01_INVARIANTS.md
02_PORTS.md
03_GATES.md
04_OBEDIENCE_TESTS.md
05_MODULE_CONTRACTS.md
06_CASE_STATE.md
```

Y luego en código ejecutable:

```text
validadores
schemas
tests de invariantes
contract tests
gates de runtime
```

---

## 12. Fórmula breve

```text
PymIA = evidencia + contratos + cálculo + estado + interpretación gobernada.
```

Sin esa obediencia, PymIA se fragmenta en islotes.

Con esa obediencia, PymIA puede crecer sin perder identidad.
