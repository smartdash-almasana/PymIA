# PYMIA_ORGANIZATIONAL_IDENTITY_THEORY

## Estado del documento

**Estado:** DRAFT_CANONICAL_CANDIDATE

**Nivel:** Doctrina organizacional fundacional

**No es V1 oficial.** Requiere validación cruzada con código y aprobación explícita antes de convertirse en doctrina canónica.

**Rige:** `ARCHITECTURE_GUARDRAILS.md`

---

## Propósito

Definir qué hace que una organización siga siendo ella misma a través del tiempo.

Establecer la teoría de identidad organizacional que permite a PymIA distinguir entre cambio adaptativo y pérdida de identidad.

Este documento **no implementa código**. Define la teoría de identidad que debe orientar la construcción de artefactos, contratos y software.

---

## Tesis central

**Identidad organizacional es el patrón estructural persistente que hace que una organización sea reconocible como ella misma a través del tiempo, a pesar de cambios en estrategia, personas, productos o contexto.**

No es estática.
No es eterna.
No es declarativa.

Es **persistencia evolutiva**: lo que permanece mientras lo demás cambia, y la forma en que ese núcleo se adapta sin dejar de ser él mismo.

Gobernanza no protege identidad estática.
Gobernanza preserva **capacidad de evolución coherente**.

---

## Alcance

Este documento define:
- Las 4 identidades (declarada, observada, deseada, percibida)
- Las 3 capas estructurales (núcleo persistente, adaptable, periférica)
- La tensión entre persistencia y evolución
- Las crisis de identidad
- La muerte ontológica
- La evolución coherente

Este documento **no define**:
- Ontología organizacional (ver `PYMIA_ORGANIZATIONAL_MODEL_THEORY.md`)
- Salud organizacional (ver `PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md`)
- Gobernanza (ver futuro `PYMIA_ORGANIZATIONAL_GOVERNANCE_THEORY.md`)
- Cultura organizacional (ver futuro `PYMIA_ORGANIZATIONAL_CULTURE_THEORY.md`)
- Patologías de identidad (ver futuro `PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md`)

---

## 1. Definición de identidad organizacional

### 1.1 Definición formal

```
Identidad organizacional =
  patrón estructural reconocible
  compuesto por:
  - compromisos de intercambio persistentes
  - capacidades distintivas acumuladas
  - relaciones críticas sostenidas
  - forma característica de operar
  - narrativa interna coherente
  que persiste a través del tiempo
  mientras permite evolución adaptativa.
```

### 1.2 Identidad no es propósito

**Contraejemplo 1: Mismo propósito, identidades distintas**

```
Organización A: Fábrica textil familiar, 40 años, produce remeras premium
Organización B: Fast fashion importador, 3 años, vende remeras básicas

Ambas responden a la misma pregunta:
"¿Qué problema existe en el mundo que justifica nuestra existencia?"
Respuesta idéntica: "Vestir personas a precio accesible."

Pero son organizaciones completamente diferentes.
Tienen identidades distintas.
```

**Contraejemplo 2: Propósito cambia, identidad persiste**

```
IBM:
- Propósito 1960: "Vender hardware de cómputo"
- Propósito 1990: "Vender software empresarial"
- Propósito 2020: "Vender servicios de consultoría e IA"

Tres propósitos distintos.
Pero IBM sigue siendo reconocible como IBM.
Identidad persistió mientras propósito pivotaba.
```

**Contraejemplo 3: Propósito ausente, identidad presente**

```
PyME familiar de 3 generaciones:
- No tiene propósito declarado
- No sabe "qué problema resuelve en el mundo"
- Simplemente "hace lo que siempre hizo"

Pero tiene identidad clarísima:
- forma de operar
- relaciones con clientes de décadas
- cultura heredada
- forma de tomar decisiones
```

### 1.3 Identidad no es estrategia

**Estrategia:** Lo que la organización HACE para competir y sobrevivir.
- Puede cambiar rápido
- Es táctica y contextual

**Identidad:** Lo que la organización ES (patrón estructural persistente).
- Cambia lento
- Es estructural y ontológica

**Ejemplo:**
```
Identidad: "Somos empresa familiar con foco en relaciones de largo plazo"
Estrategia 2024: "Competir por precio en canal mayorista"
Estrategia 2025: "Competir por calidad en canal minorista"
```

La estrategia cambió. La identidad persistió.

### 1.4 Identidad no es cultura

**Cultura:** CÓMO la organización hace las cosas (normas, valores, comportamientos).
- Es el "cómo"
- Es social y difícil de modificar conscientemente

**Identidad:** QUÉ es la organización (patrón estructural).
- Es el "qué"
- Es ontológica

**Ejemplo:**
```
Identidad: "Somos empresa familiar artesanal"
Cultura: "Acá se decide por consenso, se valora la lealtad"
```

Cultura puede evolucionar sin que cambie identidad.
Pero cultura contradictoria con identidad erosiona identidad.

---

## 2. Las cuatro identidades

Toda organización tiene simultáneamente cuatro identidades que pueden coincidir o divergir.

### 2.1 Identidad Declarada

**Definición:** Lo que la organización dice que es.

**Fuentes:**
- Ficha organizacional
- Sitio web
- Discurso del dueño
- Materiales comerciales
- Presentaciones a terceros

**Ejemplo:**
```
"Somos fábrica textil premium con 30 años de trayectoria,
 especializada en algodón de alta calidad."
```

**Características:**
- Puede ser aspiracional
- Puede ser defensiva
- Puede estar desactualizada
- Puede ser parcialmente falsa

**Relación con modelo de verdad:**
La identidad declarada es un **HumanInputNode** (ver `modelo-verdad-soberania.md`). Es la verdad operativa declarada por el dueño.

### 2.2 Identidad Observada

**Definición:** Lo que la evidencia muestra que la organización realmente es.

**Fuentes:**
- Patrones de ventas
- Comportamiento operativo
- Decisiones documentadas
- Relaciones reales con clientes/proveedores
- Asignación real de recursos

**Ejemplo:**
```
Evidencia muestra:
- 70% de ingresos por reventa de productos importados
- 30% por producción propia
- Competencia principal por precio, no por calidad
- Clientes mayoristas, no premium
```

**Características:**
- No miente (es lo que realmente ocurre)
- Puede contradecir identidad declarada
- Es la base real para análisis
- Es la identidad que opera

**Relación con modelo de verdad:**
La identidad observada emerge de **FactNode** y **OperationalTruthNode** (ver `modelo-verdad-soberania.md`). Es la verdad factual verificable.

### 2.3 Identidad Deseada

**Definición:** Lo que la organización quiere llegar a ser.

**Fuentes:**
- Planes estratégicos (si existen)
- Declaraciones de visión
- Inversiones en curso
- Contrataciones recientes
- Declaraciones sobre futuro

**Ejemplo:**
```
"Queremos migrar a 80% producción propia
 y posicionarnos como marca premium en 3 años."
```

**Características:**
- Puede ser realista o fantasiosa
- Puede estar alineada con capacidades o no
- Puede tener plan de ejecución o ser solo deseo
- Guía decisiones de inversión

### 2.4 Identidad Percibida

**Definición:** Lo que actores externos (clientes, proveedores, mercado, competidores) ven.

**Fuentes:**
- Reputación de mercado
- Posicionamiento percibido
- Relaciones con stakeholders
- Imagen pública
- Referencias de terceros

**Ejemplo:**
```
Mercado la percibe como:
"Proveedor confiable de volumen medio,
 precios competitivos, calidad estándar."
```

**Características:**
- Puede diferir mucho de las otras tres
- Determina oportunidades reales
- Es difícil de cambiar
- Condiciona estrategia posible

### 2.5 Alineación de las cuatro identidades

**Organización sana:** Las cuatro identidades están razonablemente alineadas.

```
Declarada: fábrica premium
Observada: fábrica con componente premium
Deseada: consolidar posicionamiento premium
Percibida: fabricante premium reconocido
```

Coherencia alta. Gobernanza funciona.

**Organización en tensión:** Divergencia controlada entre identidades.

```
Declarada: fábrica premium
Observada: mixto con 50% premium
Deseada: migrar a 80% premium
Percibida: en transición
```

Tensión productiva. Evolución en curso.

**Organización en crisis:** Divergencia severa entre identidades.

```
Declarada: fábrica premium
Observada: reventa masiva low-cost
Deseada: volver a ser premium
Percibida: commodity
```

Crisis de identidad. Gobernanza fallando.

---

## 3. Las tres capas estructurales

### 3.1 Núcleo persistente

**Definición:** Lo que NO puede cambiar sin que la organización deje de ser ella misma.

**Componentes típicos:**
- Valores fundamentales no negociables
- Capacidades distintivas centrales
- Relaciones críticas históricas
- Forma característica de operar
- Narrativa fundacional

**Ejemplo:**
```
Núcleo persistente de PyME textil familiar:
- Calidad artesanal como estándar mínimo
- Relaciones personales con clientes clave
- Propiedad familiar con decisión centralizada
- Producción local (no importación masiva)
```

**Propiedad clave:**
Si el núcleo se rompe, hay muerte ontológica.

### 3.2 Capa adaptable

**Definición:** Lo que PUEDE cambiar manteniendo identidad.

**Componentes típicos:**
- Estrategia comercial
- Mix de productos
- Canales de venta
- Tecnología operativa
- Estructura organizacional

**Ejemplo:**
```
Capa adaptable:
- Pueden migrar de local físico a e-commerce
- Pueden agregar línea infantil
- Pueden incorporar ERP
- Pueden contratar gerentes no familiares
```

**Propiedad clave:**
Si la capa adaptable no se ajusta, hay obsolescencia.

### 3.3 Capa periférica

**Definición:** Lo que cambia constantemente sin afectar identidad.

**Componentes típicos:**
- Precios específicos
- Campañas de marketing
- Proveedores no críticos
- Empleados no clave
- Herramientas menores

**Ejemplo:**
```
Capa periférica:
- Cambian precios cada trimestre
- Rotan campañas mensuales
- Cambian proveedor de botones
- Contratan vendedores temporarios
```

**Propiedad clave:**
La capa periférica es donde la organización experimenta sin riesgo identitario.

---

## 4. Persistencia vs evolución: el eje central

### 4.1 La tensión fundamental

**Persistencia sin evolución:** Rigidez. La organización no se adapta y muere por obsolescencia.

**Evolución sin persistencia:** Disolución. La organización cambia tanto que deja de ser ella misma.

**Identidad sana:** Persistencia del núcleo + evolución de capas adaptable y periférica.

### 4.2 Ejemplos de balance

**Caso Kodak (falta de evolución):**
- Núcleo: "somos empresa de película fotográfica"
- Entorno cambió: llegó digital
- Identidad no permitió evolucionar
- Persistencia rígida → muerte

**Caso IBM (evolución con persistencia):**
- Núcleo: "resolvemos problemas complejos de cómputo empresarial"
- Evolucionó: hardware → software → servicios → IA
- Identidad persistió mientras pivoteaba
- Evolución coherente → supervivencia 100+ años

**Caso Netflix (evolución radical con persistencia):**
- Núcleo: "entretenimiento en el hogar a demanda"
- Evolucionó: DVD por correo → streaming → producción propia
- Identidad persistió (entretenimiento a demanda)
- Evolución coherente → crecimiento masivo

### 4.3 Cómo PymIA detecta el balance

**Señales de persistencia excesiva:**
- "Siempre hicimos así"
- Rechazo sistemático a cambios de entorno
- Pérdida de mercado por no adaptarse
- Innovación ausente

**Señales de evolución excesiva:**
- Pivotes frecuentes sin consolidación
- Identidad declarada cambia cada año
- Equipo confundido sobre qué es la organización
- Clientes no reconocen a la organización

**Señales de balance sano:**
- Núcleo estable, capas externas adaptables
- Evolución con narrativa coherente
- Equipo entiende qué permanece y qué cambia
- Mercado reconoce evolución como natural

---

## 5. Crisis de identidad

### 5.1 Definición

**Crisis de identidad = divergencia severa y creciente entre las cuatro identidades (declarada, observada, deseada, percibida) que compromete coherencia organizacional.**

### 5.2 Crisis de negación

**Divergencia:** Declarada vs Observada

**Descripción:** Organización dice ser algo que la evidencia muestra que no es.

**Ejemplo:**
```
Declarada: "Somos premium"
Observada: compite por precio, calidad estándar, márgenes comprimidos
```

**Síntomas:**
- Discurso desconectado de realidad
- Decisiones inconsistentes
- Frustración del dueño ("no entiendo por qué no nos valoran")

**Causa:** Apego a identidad pasada o deseada que ya no opera.

### 5.3 Crisis de frustración

**Divergencia:** Deseada vs Observada

**Descripción:** Organización quiere ser algo que no logra ser.

**Ejemplo:**
```
Deseada: "Ser líderes en innovación"
Observada: copia competidores, no invierte en I+D, cultura conservadora
```

**Síntomas:**
- Planes que no se ejecutan
- Frustración con equipo
- Inversiones que no rinden

**Causa:** Identidad deseada incompatible con capacidades y cultura actuales.

### 5.4 Crisis de reputación

**Divergencia:** Declarada vs Percibida

**Descripción:** Mercado ve algo distinto de lo que organización dice ser.

**Ejemplo:**
```
Declarada: "Somos confiables y cumplidores"
Percibida: "Tardan en entregar, hay que controlarlos"
```

**Síntomas:**
- Pérdida de clientes sin causa aparente
- Dificultad para ganar nuevos clientes
- Esfuerzos de marketing no rinden

**Causa:** Comportamiento real no coincide con discurso.

### 5.5 Crisis de propósito

**Divergencia:** Las cuatro identidades divergen entre sí

**Descripción:** No hay coherencia en ninguna dirección.

**Ejemplo:**
```
Declarada: "Somos premium"
Observada: compite por precio
Deseada: quiere ser innovadora
Percibida: la ven como commodity
```

**Síntomas:**
- Confusión estratégica total
- Equipo desalineado
- Decisiones contradictorias
- Pérdida de rumbo

**Causa:** Ausencia de gobernanza identitaria, cambios reactivos sin coherencia.

### 5.6 Cómo PymIA detecta crisis de identidad

**Indicadores:**
- Divergencia creciente entre identidad declarada (ficha) y observada (evidencia)
- Decisiones que contradicen identidad declarada
- Cambios frecuentes de posicionamiento
- Narrativa del dueño inconsistente en el tiempo
- Mercado responde distinto a lo esperado
- Equipo confunde prioridad estratégica

---

## 6. Muerte ontológica

### 6.1 Definición

**Muerte organizacional ontológica = ruptura del núcleo persistente de identidad, de modo que la organización deja de ser reconocible como ella misma, aunque jurídicamente siga existiendo.**

No es quiebra.
No es cierre.
No es venta.

Es **pérdida de lo que la hacía ser ella**.

### 6.2 Cuándo ocurre muerte ontológica

#### 6.2.1 Ruptura de valores fundamentales

**Ejemplo:**
```
Organización fundada sobre "calidad artesanal sin concesiones"
Por presión de mercado, empieza a producir con estándares mínimos
Clientes históricos se van
Equipo fundador renuncia
Aunque siga operando, ya no es la misma organización
```

#### 6.2.2 Pérdida de capacidades distintivas

**Ejemplo:**
```
Consultora que se destacaba por expertise técnico profundo
Por crecimiento, contrata generalistas, diluye expertise
Sigue siendo consultora, pero perdió lo que la hacía única
```

#### 6.2.3 Ruptura de relaciones críticas

**Ejemplo:**
```
PyME que existía por relaciones de 30 años con 5 clientes clave
Pierde 3 de esos clientes en 1 año
Aunque consiga clientes nuevos, ya no es la misma organización
```

#### 6.2.4 Cambio de narrativa fundacional

**Ejemplo:**
```
Empresa familiar con narrativa "somos la empresa del abuelo"
Tercera generación vende a fondo de inversión
Aunque siga operando con mismo nombre, narrativa fundacional murió
```

#### 6.2.5 Pivotaje sin continuidad

**Ejemplo:**
```
Fábrica textil que cierra producción y se convierte en importadora
Mismo CUIT, mismo dueño, mismo nombre
Pero ontológicamente es otra organización
```

### 6.3 Muerte gradual vs muerte súbita

**Muerte gradual:**
- Erosión lenta del núcleo persistente
- No se nota hasta que es irreversible
- Ejemplo: pérdida gradual de calidad, cultura, relaciones
- PymIA puede detectarla temprano

**Muerte súbita:**
- Evento que rompe núcleo de golpe
- Ejemplo: venta, pivote radical, crisis que fuerza cambio total
- PymIA puede documentarla pero no prevenirla

### 6.4 Qué queda después de muerte ontológica

**Puede quedar:**
- CUIT (identidad jurídica)
- Marca (identidad comercial)
- Activos (identidad patrimonial)

**Pero no queda:**
- La organización como entidad reconocible
- El patrón estructural que la definía
- La continuidad ontológica

### 6.5 Cómo PymIA detecta proximidad a muerte ontológica

**Señales tempranas:**
- Decisiones que violan valores declarados históricamente
- Pérdida de capacidades distintivas sin reemplazo
- Ruptura de relaciones críticas acumulada
- Narrativa del dueño ya no menciona elementos fundacionales
- Equipo histórico se va sin reemplazo cultural

---

## 7. Evolución coherente

### 7.1 Cuándo identidad debe evolucionar

**1. Entorno cambió estructuralmente:**
Lo que funcionaba ya no funciona.
Identidad actual es obstáculo para supervivencia.

**2. Capacidades evolucionaron:**
Organización desarrolló nuevas capacidades que identidad vieja no refleja.

**3. Oportunidad de crecimiento requiere expansión:**
Identidad actual es muy estrecha para capturar oportunidad.

**4. Generación nueva toma control:**
Nueva generación tiene visión distinta que requiere actualización identitaria.

### 7.2 Cómo evoluciona identidad coherentemente

**1. Identificar núcleo persistente:**
¿Qué NO debe cambiar?
¿Qué nos hace ser nosotros?

**2. Identificar qué debe evolucionar:**
¿Qué capa adaptable debe ajustarse?
¿Por qué?

**3. Construir narrativa de continuidad:**
¿Cómo el cambio es evolución natural y no ruptura?
¿Qué hilo conductor conecta pasado con futuro?

**4. Evolucionar coherentemente:**
Decisiones, inversiones, contrataciones alineadas con nueva identidad.
No declarativa: operativa.

**5. Consolidar nueva identidad:**
Tiempo suficiente para que nueva identidad se observe, no solo se declare.
Mercado e internos la reconocen como natural.

### 7.3 Ejemplo de evolución coherente

```
PyME textil familiar:

Identidad 2010:
"Fábrica artesanal de ropa masculina clásica"

Entorno cambia:
- Competencia importada
- Clientes piden más variedad
- Hijos se incorporan con visión distinta

Evolución 2015-2020:
- Núcleo persistente: calidad artesanal, relaciones personales
- Capa adaptable: incorpora línea femenina, e-commerce
- Narrativa: "Evolucionamos manteniendo calidad y cercanía"

Identidad 2020:
"Empresa textil familiar con líneas masculina y femenina,
 canal físico y digital, manteniendo calidad artesanal"

Evolución coherente:
- Mercado reconoce continuidad
- Equipo entiende qué permanece y qué cambió
- Identidad se expandió sin romperse
```

### 7.4 Rol de PymIA en evolución identitaria

**Detecta necesidad de evolución:**
- Entorno cambió pero identidad no
- Oportunidades no capturables con identidad actual
- Tensión creciente entre identidades

**Facilita reflexión:**
- Ayuda a identificar núcleo persistente
- Señala qué debe evolucionar
- Muestra divergencias entre identidades

**Monitorea coherencia:**
- Durante transición, verifica que decisiones alineen con nueva identidad
- Detecta si evolución es coherente o errática
- Alerta sobre retrocesos o contradicciones

---

## 8. Identidades múltiples en organizaciones complejas

### 8.1 El problema

Organizaciones con múltiples unidades de negocio, líneas de productos o geografías tienen **múltiples identidades operativas**.

**Pregunta:** ¿Cómo coordinar identidades múltiples sin destruir diversidad ni perder coherencia?

### 8.2 Niveles de identidad

**Identidad corporativa (nivel superior):**
- Valores fundamentales
- Propósito general
- Estándares éticos
- Narrativa paraguas

**Identidades de unidad (nivel operativo):**
- Estrategia específica
- Modelo de negocio
- Cultura local
- Relaciones específicas

### 8.3 Ejemplo

```
Conglomerado industrial:

Identidad corporativa:
"Soluciones industriales confiables con integridad"

Identidad unidad A (química):
"Química especializada de alta precisión"

Identidad unidad B (logística):
"Logística industrial flexible y rápida"

Identidad unidad C (servicios):
"Mantenimiento preventivo de clase mundial"
```

Cada unidad tiene identidad propia.
Todas comparten identidad corporativa.

### 8.4 Coordinación de identidades múltiples

**Gobernanza corporativa debe:**
- Preservar identidad corporativa (valores, ética)
- Permitir diversidad de identidades de unidad
- Coordinar donde hay sinergias
- Evitar contradicciones entre unidades

**Patologías de identidades múltiples:**
- Unidades compiten entre sí (canibalización)
- Unidades tienen valores contradictorios
- Identidad corporativa es tan genérica que no significa nada
- Unidades ignoran identidad corporativa

---

## 9. Relación con otros documentos del lote

### 9.1 Con PYMIA_ORGANIZATIONAL_MODEL_THEORY.md

MODEL define la dimensión de identidad de forma mínima (declarada/observada/operativa).

Este documento desarrolla en profundidad:
- Las 4 identidades (declarada, observada, deseada, percibida)
- Las 3 capas (núcleo persistente, adaptable, periférica)
- La evolución identitaria
- La muerte ontológica

### 9.2 Con PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md

HEALTH_MODEL define cuándo la organización está sana.

Una organización puede estar financieramente sana pero en crisis de identidad (divergencia severa entre identidades).

Una organización puede tener identidad coherente pero estar enferma (patologías operativas).

Salud e identidad son dimensiones distintas pero relacionadas.

---

## 10. Relación con documentos fuente existentes

Este documento se apoya conceptualmente en:

**`fundamentos/organismo-pyme.md`:**
- Dueño como variable dinámica
- Excepciones y redefinición de prioridades

**`epistemologia/modelo-verdad-soberania.md`:**
- HumanInputNode (identidad declarada)
- OperationalTruthNode (identidad observada)
- TruthConflict (divergencia entre identidades)

**`epistemologia/protocolo-conversacional-hermes.md`:**
- Modos DIOS/HIBRIDO/INVESTIGADOR como expresiones de identidad conversacional

**`hermes/soul.md`:**
- Identidad conversacional de Hermes como proxy de identidad organizacional

---

## 11. Riesgos de deriva conceptual

### 11.1 Riesgo 1: Confundir identidad con propósito

Identidad es patrón estructural persistente. Propósito es razón de existir.
Pueden cambiar independientemente.

**Mitigación:** Definir explícitamente que identidad ≠ propósito.

### 11.2 Riesgo 2: Tratar identidad como estática

Identidad evoluciona. No es fija.

**Mitigación:** Definir las 3 capas (núcleo/adaptable/periférica) y la evolución coherente.

### 11.3 Riesgo 3: Patologizar toda divergencia

Divergencia controlada entre identidades puede ser evolución en curso, no crisis.

**Mitigación:** Distinguir divergencia controlada de crisis severa.

### 11.4 Riesgo 4: Confundir muerte ontológica con quiebra

Organización puede quebrar sin morir ontológicamente (y viceversa).

**Mitigación:** Definir explícitamente que muerte ontológica es pérdida de patrón estructural, no cese de operaciones.

---

## 12. Criterio de uso futuro para mapping/artefactos/software

### 12.1 Artefactos que eventualmente deben existir

```
OrganizationalIdentity
├── DeclaredIdentity (lo que dice ser)
├── ObservedIdentity (lo que evidencia muestra)
├── DesiredIdentity (lo que quiere ser)
├── PerceivedIdentity (lo que mercado ve)
├── PersistentCore (valores, capacidades, relaciones, narrativa)
├── AdaptableLayer (estrategia, productos, canales, tecnología)
└── PeripheralLayer (precios, campañas, proveedores menores)
```

### 12.2 Contratos que eventualmente deben existir

```
IdentityDeclaration (declaración formal de identidad)
IdentityObservation (observación basada en evidencia)
IdentityDivergence (divergencia entre identidades)
IdentityCrisis (crisis de identidad tipificada)
IdentityEvolution (evolución coherente)
OntologicalDeath (muerte ontológica)
```

### 12.3 Software que eventualmente debe implementarse

- Persistencia de las 4 identidades por tenant
- Detección automática de divergencias
- Alertas de crisis de identidad
- Tracking de evolución identitaria
- Detección de proximidad a muerte ontológica
- Versionado de identidad

---

## 13. Regla final

```
Identidad organizacional no es propósito.
No es estrategia.
No es cultura.

Es el patrón estructural persistente
que hace que una organización sea reconocible
como ella misma a través del tiempo.

Compuesta por:
- núcleo persistente (lo que no puede cambiar)
- capa adaptable (lo que puede cambiar coherentemente)
- capa periférica (lo que cambia constantemente)

Manifestada en cuatro dimensiones:
- declarada (lo que dice ser)
- observada (lo que realmente es)
- deseada (lo que quiere ser)
- percibida (lo que otros ven)

La gobernanza no preserva identidad estática.
Preserva capacidad de evolución coherente.

La muerte ontológica ocurre
cuando el núcleo persistente se rompe.

Las crisis de identidad ocurren
cuando las cuatro identidades divergen severamente.

PymIA no define identidad.
PymIA la observa, la monitorea, la protege.

Porque sin identidad coherente,
no hay organización.
Solo hay actividad.
```

---

## Conceptos incluidos

- Identidad organizacional como patrón estructural persistente
- 4 identidades (declarada, observada, deseada, percibida)
- 3 capas estructurales (núcleo persistente, adaptable, periférica)
- Persistencia vs evolución
- Crisis de identidad (4 tipos: negación, frustración, reputación, propósito)
- Muerte ontológica
- Evolución coherente
- Identidades múltiples en organizaciones complejas

---

## Conceptos excluidos

- Ontología organizacional (pertenece a MODEL_THEORY)
- Teoría de salud (pertenece a HEALTH_MODEL)
- Teoría de gobernanza (pertenece a futuro GOVERNANCE_THEORY)
- Teoría de cultura (pertenece a futuro CULTURE_THEORY)
- Patologías de identidad (pertenecen a futuro PATHOLOGY_THEORY)
- Teoría de intervención (pertenece a futuro INTERVENTION_THEORY)
- Teoría de decisión (pertenece a futuro DECISION_QUALITY_THEORY)

---

**Documento cerrado como DRAFT_CANONICAL_CANDIDATE.**

Listo para revisión cruzada con MODEL_THEORY y HEALTH_MODEL antes de promoción a V1 oficial.
