# HERMES_LOCAL_SCN_SANDBOX_COMMAND_PLAN

Estado: COMMAND PLAN — NO EXECUTION  
Ámbito: Hermes local / SCN / PymIA  
Tipo: Plan documental de comandos futuros  
Fecha: 2026-05-24  

---

## 1. Propósito

Diseñar comandos futuros de preflight y validación sandbox SCN sin ejecutarlos.

Este documento:
- No ejecuta nada.
- No autoriza el orquestador Hermes ni sus servicios.
- No autoriza el bot ni la API de Telegram real.
- No autoriza accesos ni herramientas ligadas al protocolo MCP-3.
- No autoriza conexiones ni alteraciones del entorno de producción.

---

## 2. Estado base

- **Ruta del sandbox:** `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local`
- **Ruta de HERMES_HOME:** `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\HERMES_HOME`
- **Ruta de política local:** `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\config\runtime_policy.local.yaml`
- **Ruta de plantilla env:** `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\config\.env.sandbox.example`
- **Ruta del repo PymIA:** `E:\BuenosPasos\smartbridge\PymIA`
- **Último estado de validación física conocido:** `SANDBOX_PREFLIGHT_PASS` (Confirmado por auditoría de consistencia previa).

---

## 3. Comandos seguros de inspección futura

Todos los comandos a continuación son plantillas y están marcados explícitamente para prohibir su ejecución sin autorización:

```powershell
# NO EJECUTAR SIN AUTH EXPLÍCITO

# Listar el árbol completo de archivos y directorios del sandbox
Get-ChildItem -Path "E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local" -Recurse

# Leer y verificar las declaraciones operativas del README
Get-Content -Path "E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\README.md"

# Leer y auditar la plantilla dummy del archivo de entorno
Get-Content -Path "E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\config\.env.sandbox.example"

# Leer y verificar el mapa plano YAML de políticas
Get-Content -Path "E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\config\runtime_policy.local.yaml"

# Verificar que el repositorio PymIA continúe limpio
Set-Location -LiteralPath "E:\BuenosPasos\smartbridge\PymIA"
git status --short
```

---

## 4. Comandos de validación de archivos futuros

Para verificar que los archivos del sandbox cumplen las especificaciones y no contienen secretos sin hacer llamadas externas ni ejecutar agentes:

```powershell
# NO EJECUTAR SIN AUTH EXPLÍCITO

# Validar que runtime_policy.local.yaml es un YAML parseable y cumple sintaxis
# Se propone una validación en Python para evitar instalar herramientas externas
python -c "import yaml; yaml.safe_load(open('E:/BuenosPasos/smartbridge/.tmp/hermes-scn-local/config/runtime_policy.local.yaml'))"

# Verificar que los schemas JSON de contratos SCN estén presentes en el repo de PymIA
Get-ChildItem -Path "E:\BuenosPasos\smartbridge\PymIA\docs\contracts\scn\*.json"

# Validar ausencia de patrones de secretos reales o keys dentro del sandbox
# Buscar strings del tipo 'sk-', tokens, api keys reales, o referencias a hermes-agent
Get-ChildItem -Path "E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local" -Recurse | Select-String -Pattern "sk-", "bot", "chat_id", "allowed_users"
```

Directivas de seguridad:
- Prohibido cualquier uso de red externa.
- Prohibido tocar, referenciar o ejecutar comandos dentro de `hermes-agent` real.
- Prohibido arrancar la instancia real de Hermes.

---

## 5. Comandos prohibidos

| Comando/Patrón | Motivo | Riesgo | Estado |
| :--- | :--- | :--- | :--- |
| **Cualquier comando dentro de `E:\BuenosPasos\smartbridge\hermes-agent`** | Aislamiento estricto de activos sensibles del sistema | Modificación accidental de soul, memory o skills reales | **PROHIBIDO** |
| **Lectura de `.env` real** | Protección de la capa de seguridad relacional Supabase y APIs de GCP | Fuga o filtración de credenciales reales a los logs del sandbox | **PROHIBIDO** |
| **Ejecución del orquestador Hermes** | No hay autorización del usuario humano para correr loops autónomos | Comportamiento del agente descontrolado o llamadas a red no deseadas | **PROHIBIDO** |
| **Telegram bot polling o webhooks** | Interacción con el canal de producción activo | Respuestas huérfanas en el bot real a usuarios finales | **PROHIBIDO** |
| **Llamadas MCP-3** | Acceso a recursos de nube configurados de forma global | Alteración de instancias, snapshots o bases de datos de GCP | **PROHIBIDO** |
| **Creación o manipulación de `systemd`** | Evitar procesos daemon persistentes en segundo plano | Degradación del control de procesos locales | **PROHIBIDO** |
| **Apertura de túneles (ngrok, etc.)** | Protección de puertos locales y firewall | Exposición de la red local a accesos externos | **PROHIBIDO** |
| **Cualquier llamada de red externa (`curl`, `wget`, `socket`)** | Mantener hermeticidad computacional | Fuga de datos clínicos-operativos | **PROHIBIDO** |
| **Escritura fuera del sandbox `.tmp/`** | Preservar integridad del core de PymIA | Alteración del código de producción o tests contractuales | **PROHIBIDO** |

---

## 6. Condiciones antes de ejecutar cualquier comando futuro

Antes de que un comando de esta lista sea removido de su restricción de ejecución, se debe certificar en el canal del repo:
1. **Mensaje del usuario con AUTH explícito:** Aprobación literal escrita por parte del dueño humano.
2. **Comando exacto:** Declarar la línea de comando exacta que se ejecutará en la sesión.
3. **Alcance exacto:** Especificar el límite y efecto de la llamada en el sistema.
4. **Ruta exacta:** Confirmar el directorio de ejecución (estrictamente contenido bajo `.tmp/`).
5. **Confirmación de no secrets:** Auditoría final del entorno que verifique que no se han importado tokens reales.
6. **Rollback/cleanup definido:** Plan listo para borrar y limpiar toda traza tras la ejecución.
7. **Criterio PASS/BLOCKED:** Las aserciones esperadas para clasificar la validez de la prueba.

---

## 7. Secuencia futura recomendada

El orden lógico de los hitos secuenciales (solo con propósitos documentales conceptuales):
- **A. Validar estructura:** Inspección física del árbol de directorios de pruebas.
- **B. Validar policy:** Confirmación y chequeo sintáctico de `runtime_policy.local.yaml`.
- **C. Validar schemas SCN presentes:** Chequeo de consistencia de los esquemas de contratos de PymIA.
- **D. Validar no secrets:** Auditoría visual de placeholders dummy en `.env.sandbox.example`.
- **E. Preparar input sintético:** Crear archivo de candidato de evidencia mockeado bajo `evidence/`.
- **F. Ejecución simulada (Fase posterior):** Evaluar la corrida del pipeline y parseadores en sandbox aislado, sin invocar el agente Hermes real.

---

## 8. Criterios BLOCKED

La secuencia de validación debe abortarse y transicionar a estado **BLOCKED** de forma inmediata ante:
- Falta de la autorización explícita escrita del usuario.
- Presencia de cualquier API key o token activo.
- Presencia del archivo `.env` real del repositorio.
- Intento de acceso, lectura o ejecución en `E:\BuenosPasos\smartbridge\hermes-agent`.
- Intento de habilitación o conexión de Telegram real.
- Intento de habilitar llamadas externas a internet.
- Intentos de invocar herramientas GCP / MCP-3.
- Intento de conexión con la base de datos viva de Supabase.
- Intentos de escritura o modificación de código Python fuera del directorio `.tmp/`.

---

## 9. Próxima acción permitida

La única acción inmediata aprobada tras la conformación de este plan es:
- Registrar este documento en la tabla general de [docs/DOCUMENTATION_INDEX.md](file:///E:/BuenosPasos/smartbridge/PymIA/docs/DOCUMENTATION_INDEX.md) para mantener la gobernanza documental alineada al 100%.
