# HERMES_LOCAL_SCN_SANDBOX_PREP_CHECKLIST

Estado: PREP CHECKLIST — NO EXECUTION  
Ámbito: Hermes local / SCN / PymIA  
Tipo: Checklist documental preflight  
Fecha: 2026-05-24  

---

## 1. Propósito

Definir una checklist documental previa a cualquier preparación de sandbox local SCN para Hermes.

Este documento:
- No ejecuta Hermes.
- No crea la estructura física del sandbox.
- No modifica ninguna configuración local ni global del sistema.
- No habilita ni interactúa con la integración de Telegram real.
- No interactúa con la instancia de `hermes-agent` real inventariada.
- No autoriza el protocolo MCP-3 ni sus herramientas.
- No autoriza accesos ni interacciones con el entorno de producción.

---

## 2. Alcance

- **Ámbito incluido:** repositorio `PymIA`, documentación SCN en `docs/arquitectura/`, contratos JSON y YAML en `docs/contracts/scn/`, plan de sandbox local, criterios preflight conceptuales.
- **Ámbito excluido:** instancia real de `hermes-agent`, integración y API de Telegram real, archivos `.env` reales de desarrollo o producción, base de datos en producción, memoria clínica persistente, skills previas del agente, logs de ejecución anteriores, servicios en VM de GCP y el runner MCP-3.

---

## 3. Estado base requerido

- [ ] **Repositorio PymIA limpio:** git status no debe reportar modificaciones locales no deseadas fuera del alcance documental.
- [ ] **HEAD registrado:** El último commit de main debe ser conocido y coherente con el cierre de frontera (ej. `40ceb0d`).
- [ ] **DOCUMENTATION_INDEX actualizado:** Este checklist y el plan de sandbox deben estar formalmente listados en [DOCUMENTATION_INDEX.md](file:///E:/BuenosPasos/smartbridge/PymIA/docs/DOCUMENTATION_INDEX.md).
- [ ] **Contratos SCN presentes:** Los cuatro schemas JSON de contratos y el glosario de SCN deben existir y estar conformados en la ruta de contratos.
- [ ] **Runtime Policy presente:** Debe existir `runtime_policy.example.yaml` con las directivas de seguridad.
- [ ] **HERMES_LOCAL_INSTANCE_INVENTORY leído:** Auditoría observacional del Hermes real asimilada.
- [ ] **HERMES_LOCAL_SCN_SANDBOX_PLAN leído:** Entendimiento formal de la necesidad de aislamiento físico y lógico para SCN.
- [ ] **SCN_TEST_FRONTIER_PLAN leído:** Casos de prueba de no-degradación y fail-closed integrados.

---

## 4. Guardrails absolutos

| Regla | Estado requerido | Motivo | Evidencia esperada |
| :--- | :--- | :--- | :--- |
| **No tokens reales** | **BLOQUEADO / PROHIBIDO** | Evitar fugas accidentales o transacciones reales | Archivos de configuración de sandbox con `<DUMMY>` o `<REDACTED>`. |
| **No Telegram real** | **BLOQUEADO / PROHIBIDO** | Prevenir interacciones directas con el canal real durante las pruebas | `TELEGRAM_BOT_TOKEN=dummy_token` en variables del entorno de sandbox. |
| **No .env real** | **BLOQUEADO / PROHIBIDO** | El entorno real expone base de datos y credenciales sensibles de la VM | Sandbox sin archivo `.env` o solo con plantilla redacted. |
| **No hermes-agent real como sandbox** | **BLOQUEADO / PROHIBIDO** | La carpeta de desarrollo posee memoria y tokens reales activos | El sandbox se despliega en una ruta física independiente descartable. |
| **No memoria real** | **BLOQUEADO / PROHIBIDO** | Evitar contaminación con estados conversacionales históricos | Base de datos local vacía o logs de sesión inexistentes al arrancar. |
| **No skills reales** | **BLOQUEADO / PROHIBIDO** | Prevenir que el agente use herramientas con lógica de negocio o de sistema no auditadas | Carpeta `skills/` del sandbox vacía o limitada a la whitelist mínima. |
| **No logs reales** | **BLOQUEADO / PROHIBIDO** | Evitar la exposición de secretos en archivos de logs antiguos | Archivos de logs del sandbox inicializados desde cero. |
| **No tools productivas** | **BLOQUEADO / PROHIBIDO** | Prevenir que Hermes invoque scripts con efectos secundarios en base de datos o sistema | Whitelist de herramientas del sandbox estrictamente limitada. |
| **No shell libre** | **BLOQUEADO / PROHIBIDO** | Impide que el agente ejecute comandos de consola arbitrarios | Herramienta de ejecución de comandos desactivada en el sandbox. |
| **No red externa sin policy** | **BLOQUEADO / PROHIBIDO** | Prevenir llamadas salientes a servicios externos no controlados | Motor de políticas de frontera validando y bloqueando URLs no declaradas. |
| **No escritura fuera de sandbox** | **BLOQUEADO / PROHIBIDO** | Evitar que el agente modifique el código base de `PymIA` o archivos de configuración global | Restricción de permisos y control estricto de paths de escritura. |
| **No MCP-3** | **BLOQUEADO / PROHIBIDO** | El protocolo MCP-3 otorga acceso directo a infraestructura de nube | Sin configuraciones ni tokens activos para GCP-MCP en sandbox. |
| **No producción** | **BLOQUEADO / PROHIBIDO** | Evitar cualquier alteración del negocio o bases de datos relacionales vivas | Configuración de conexión relacional a Supabase totalmente dummy. |

---

## 5. Sandbox propuesto

Rutas propuestas de carácter estrictamente documental:
- **Raíz del sandbox:** `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local`
- **HERMES_HOME del sandbox:** `E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\HERMES_HOME`

Directivas de las rutas:
- Tienen un propósito puramente documental; no son creadas físicamente en esta fase previa.
- Son descartables y diseñadas para ser destruidas al finalizar cada ciclo de pruebas.
- Quedan completamente fuera del directorio principal de `hermes-agent` real para evitar cruces.
- Operan sin copiar ningún archivo `.env` o secreto real.

---

## 6. Configuración dummy permitida futura

Ejemplo documental de entorno de sandbox:
```text
TELEGRAM_BOT_TOKEN=<DUMMY_OR_REDACTED>
OPENROUTER_API_KEY=<DUMMY_OR_REDACTED>
HERMES_HOME=E:\BuenosPasos\smartbridge\.tmp\hermes-scn-local\HERMES_HOME
```

Guardrails de configuración:
- Prohibido copiar el archivo `.env` real del repositorio.
- Prohibido configurar tokens, API keys o chat IDs reales.
- Prohibido poblar listas de usuarios autorizados (`allowed_users`) con IDs reales de producción.

---

## 7. Contratos SCN requeridos

1. **[evidence_candidate.schema.json](file:///E:/BuenosPasos/smartbridge/PymIA/docs/contracts/scn/evidence_candidate.schema.json)**
   - *Propósito:* Definir la estructura única de entrada externa recolectada.
   - *Rol:* Encapsula el input antes de la validación del Kernel.
   - *Criterio mínimo de presencia:* Debe validar la restricción `diagnostic_authority: false` y campos de control mínimos (`tenant_id`, `evidence_id`, `raw_content_hash`).
   - *Criterio de bloqueo:* Si falta, se bloquea el procesamiento e ingesta de cualquier archivo o mensaje adjunto.
2. **[kernel_request.schema.json](file:///E:/BuenosPasos/smartbridge/PymIA/docs/contracts/scn/kernel_request.schema.json)**
   - *Propósito:* Sobre de solicitud tipada y segura para el Kernel de PymIA.
   - *Rol:* Evita que Hermes llame de forma directa o informal al núcleo clínico.
   - *Criterio mínimo de presencia:* Exige arreglo de referencias `evidence_refs` con al menos 1 ítem obligatorio.
   - *Criterio de bloqueo:* Bloquea la computación diagnóstica si la petición no está formalmente estructurada y enlazada.
3. **[operational_audit_result.scn.schema.json](file:///E:/BuenosPasos/smartbridge/PymIA/docs/contracts/scn/operational_audit_result.scn.schema.json)**
   - *Propósito:* Proyección de salida soberana e íntegra del Kernel de PymIA.
   - *Rol:* Transporta los hallazgos y restricciones semánticas de render.
   - *Criterio mínimo de presencia:* Exige la marca soberana (`sovereign_mark`) con firma de PymIA y arreglo de `forbidden_inferences`.
   - *Criterio de bloqueo:* Impide cualquier visualización conversacional o render si el resultado carece de la firma digital de PymIA.
4. **[render_contract.schema.json](file:///E:/BuenosPasos/smartbridge/PymIA/docs/contracts/scn/render_contract.schema.json)**
   - *Propósito:* Contrato de minimización de salida conversacional.
   - *Rol:* Define qué campos y valores específicos puede visualizar Hermes en el canal.
   - *Criterio mínimo de presencia:* Elimina razonamiento clínico/financiero interno, limitando el tono conversacional a valores whitelisted (`clinical`, `operational`, `blocked`).
   - *Criterio de bloqueo:* Bloquea el render conversacional si el mensaje de salida no cumple con las directivas de minimización y no reinterpretación.
5. **[runtime_policy.example.yaml](file:///E:/BuenosPasos/smartbridge/PymIA/docs/contracts/scn/runtime_policy.example.yaml)**
   - *Propósito:* Centralizar las políticas dinámicas de la frontera SCN.
   - *Rol:* Gobierna la denegación y autorizaciones de acciones de orquestación.
   - *Criterio mínimo de presencia:* Declara la whitelist de acciones y las condiciones obligatorias de disparo fail-closed.
   - *Criterio de bloqueo:* Bloquea la inicialización de herramientas del sandbox si la política no está cargada o contiene colisiones de reglas.

---

## 8. Flujo futuro permitido, solo conceptual

El flujo de transacciones de soberanía bajo el sandbox local SCN se define como:

```text
[Input Sintético Externo]
        │
        ▼
[Hermes Agent] ──(Genera)──► EvidenceCandidate
                                   │
                                   ▼
[Boundary Layer] ────► KernelRequest (Validado)
                                   │
                                   ▼
[PymIA Kernel] ──────► OperationalAuditResult (Firmado)
                                   │
                                   ▼
[Output Gateway] ────► RenderContract (Minimizado)
                                   │
                                   ▼
[Hermes Render] ────► (Muestra al usuario sin reinterpretar)
```

Aclaraciones de frontera:
- Este flujo es puramente conceptual y no se implementa en esta fase.
- No se ejecutan procesos ni runners reales en el entorno local.
- No se autorizan integraciones MCP-3 ni llamadas de red al canal real de Telegram.

---

## 9. Casos mínimos de preflight

- [ ] **EvidenceCandidate válido:** Prueba de que un candidato correcto se valida y clasifica adecuadamente por la Boundary Layer.
- [ ] **Input inválido fail-closed:** Demostración de que la falta de campos obligatorios en el candidato bloquea inmediatamente el flujo.
- [ ] **OperationalAuditResult -> RenderContract:** Verificación de que la salida del kernel se minimiza correctamente de acuerdo al contrato de render.
- [ ] **Forbidden inferences propagadas:** Confirmación de que las inferencias restringidas se listan en el render contract para guiar el tono conversacional.
- [ ] **Sovereign mark ausente bloqueado:** Intento de renderizar una salida que carece de la firma digital de PymIA debe fallar de inmediato.
- [ ] **Hermes crea findings bloqueado:** Simulación de que Hermes intenta auto-generar un hallazgo o conclusión y la política lo bloquea.
- [ ] **Pending data no diagnostica:** Si el estado es `pending_data`, el render se restringe a solicitar las pruebas faltantes sin dar diagnósticos.
- [ ] **Blocked comunica bloqueo:** Si el estado es `blocked`, se anula el resumen clínico y se emite exclusivamente la advertencia segura.
- [ ] **Audit trail sandbox preservado:** Confirmación de que el ID de traza de auditoría se mantiene intacto sin aplanarse a texto plano en el router.
- [ ] **No escritura fuera de sandbox:** Comprobación de que las ejecuciones de prueba no alteran archivos en `PymIA/` o directorios adyacentes.

---

## 10. Criterios BLOCKED

La preparación del sandbox debe permanecer en estado **BLOCKED** ante cualquiera de estas condiciones:
- Repositorio Git reporta cambios no controlados o archivos sucios en producción.
- Ausencia o inconsistencia en cualquiera de los schemas de contratos SCN.
- Ausencia del archivo de políticas de runtime de frontera.
- Detección de cualquier API key o token activo de Telegram/OpenRouter en los directorios del sandbox.
- Intento de apuntar los scripts del sandbox al checkout real de `hermes-agent`.
- Intento de habilitar la integración del bot con el canal real de Telegram.
- Presencia del archivo `.env` real copiado al sandbox.
- Intento de habilitar llamadas de red externas no autorizadas en la política de sandbox.
- Intentos de escritura o parcheo fuera del directorio aislado de pruebas.
- Invocación de herramientas o procesos ligados a privilegios de GCP / MCP-3.
- Intento de conexión con la base de datos viva de Supabase.
- Ausencia de la firma y aprobación explícita del usuario humano para realizar la fase de preparación física.

---

## 11. Criterios READY_FOR_SANDBOX_CREATION

El estado formal de esta fase del sandbox local SCN se define como:
**READY_FOR_SANDBOX_CREATION_DOC_ONLY**

Se alcanza exclusivamente si:
- Esta checklist documental preflight se encuentra 100% completada y revisada.
- No existen secretos reales en los planes de configuración.
- Se mantiene el bloqueo absoluto a la API y el bot de Telegram real.
- Las rutas del sandbox están declaradas de forma conceptual y aislada de la instalación principal.
- Todos los contratos y schemas JSON de SCN están presentes y válidos en el repo.
- La plantilla de políticas y triggers fail-closed de frontera está conformada.
- Las pruebas mínimas preflight están perfectamente alineadas con `SCN_TEST_FRONTIER_PLAN.md`.
- La autorización explícita por escrito del usuario para la creación física de carpetas está pendiente y registrada en este documento.

> [!WARNING]
> Este estado es de carácter ESTRICTAMENTE DOCUMENTAL. Bajo ninguna circunstancia autoriza la creación física de carpetas ni la ejecución del orquestador Hermes o sus herramientas.

---

## 12. Criterios antes de cualquier ejecución futura

Antes de autorizar cualquier ejecución de prueba o corrida del sandbox local en una fase posterior, se debe verificar físicamente:
1. **Autorización explícita:** Firma electrónica o confirmación directa del usuario humano en el chat del repo.
2. **Comando exacto:** Definición clara del comando de ejecución (ej. script de preflight unitario sin loops autónomos).
3. **Entorno aislado:** Verificación de que las variables de entorno están limitadas estrictamente a los paths dummy.
4. **HERMES_HOME creado:** Inicialización del directorio descartable de sandbox vacío.
5. **Configuración dummy cargada:** Confirmación de que no se importó ninguna credencial real en los archivos temporales.
6. **Whitelist activa:** El motor de políticas configurado en modo estricto, con denegación por defecto y whitelist de herramientas de lectura.
7. **Logs de sandbox activos:** Trazas redirigidas exclusivamente a `.tmp/hermes-scn-local/logs/` sin contaminación.
8. **Rollback definido:** Script o procedimiento listo para remover y limpiar en su totalidad el directorio `.tmp/` al finalizar la prueba.
9. **Criterio de éxito formal (PASS/BLOCKED):** Rúbricas de aserción contractual automatizadas y listas para ser validadas.

---

## 13. Próxima acción permitida

La única acción operativa habilitada de forma inmediata es:
- Registrar este checklist en la tabla general de [docs/DOCUMENTATION_INDEX.md](file:///E:/BuenosPasos/smartbridge/PymIA/docs/DOCUMENTATION_INDEX.md) para mantener la gobernanza documental alineada al 100%.
