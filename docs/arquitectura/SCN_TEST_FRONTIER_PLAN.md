# SCN_TEST_FRONTIER_PLAN

Estado:
DRAFT TEST PLAN — NO EXECUTION

## 1. Propósito
Definir pruebas futuras para validar la frontera SCN antes de implementación runtime.

## 2. No autorizado
Se declara de manera explícita y taxativa que queda prohibido en esta fase:
* **No ejecución de tests**: Este plan es de carácter estrictamente documental; no se deben implementar ni ejecutar baterías de prueba en código real.
* **No runtime**: No se permite la alteración, parche o creación de lógica en el runtime del kernel de PymIA ni en sus componentes conversacionales.
* **No Hermes vivo**: Queda prohibida la ejecución, arranque o manipulación del orquestador Hermes en la VM o entorno de desarrollo.
* **No Telegram real**: No se permite realizar llamadas a la API de Telegram, envío de payloads a cuentas reales ni el uso de tokens activos de producción o staging.
* **No MCP-3**: No se autoriza el despliegue, habilitación o prueba operativa del protocolo MCP-3 ni sus herramientas.
* **No producción**: Queda estrictamente vetado alterar, conectar o interactuar con el entorno de producción.
* **No nuevas tools**: No se permite la creación ni registro de nuevas herramientas (tools) en los adaptadores.
* **No plugins reales**: No se permite crear extensiones de software o plugins ejecutables bajo el kernel o interfaz de frontera.
* **No modificación de configuración sensible**: Queda estrictamente prohibida la edición de archivos `.env`, credenciales de bases de datos, llaves de API o cualquier otra variable del entorno sensible.

## 3. Alcance de prueba futura
Las pruebas futuras del plan de frontera SCN cubrirán rigurosamente los siguientes aspectos arquitectónicos:
* **EvidenceCandidate validation**: Verificación formal de que todo input externo ingresa encapsulado de acuerdo al esquema de candidatos a evidencia, impidiendo datos estructurados de origen no validado.
* **KernelRequest contract**: Validación de que las solicitudes enviadas al kernel cumplan con el contrato unificado y contengan de forma obligatoria las referencias correspondientes.
* **OperationalAuditResult verification**: Aseguramiento de que la salida del kernel preserve de forma íntegra todos los metadatos clínicos-operativos, estados, y firmas sin alteración.
* **RenderContract integrity**: Validación de que el documento recibido por el canal contenga exclusivamente los campos permitidos para visualización, eliminando trazas de razonamiento interno.
* **RuntimePolicy enforcement**: Cumplimiento de la política activa para denegar o autorizar acciones y activar mecanismos de mitigación en la frontera.
* **Fail-closed**: Comportamiento de bloqueo absoluto e inmediato ante inconsistencias estructurales, faltas de evidencia o violación de las reglas de frontera.
* **Forbidden_inferences propagation**: Propagación directa de las inferencias prohibidas por el kernel hasta el contrato de render, evitando que sean filtradas o ignoradas en la comunicación final.
* **Audit_trail propagation**: Mantenimiento de la referencia única y auditabilidad sin exponer lógica transaccional o pesos internos de decisión.
* **Sovereign_mark enforcement**: Exigencia obligatoria de la firma/marca soberana verificable emitida por PymIA para autorizar la visualización de resultados.
* **Hermes cannot generate findings**: Garantía técnica de que Hermes no puede generar hallazgos propios por vía conversacional, persistir memoria clínica paralela, ni suplantar la autoridad computacional del núcleo.
* **Router non-degradation**: Certificación de que el gateway o ruteador de resultados mantiene la estructura original del contrato sin degradarla a texto plano o formatos no tipados.

## 4. Matriz de tests futuros

| ID | Nombre | Input | Expected Result | Contract | Risk Covered | Required Before Runtime |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SCN-T001** | valid EvidenceCandidate accepted | `valid_evidence_candidate.json` (esquema correcto, `diagnostic_authority: false`) | La validación en el gateway de entrada es exitosa y se enruta de forma correcta hacia el kernel. | `evidence_candidate.schema.json` | Ingreso de candidatos de evidencia con sintaxis rota o estructuras de datos inconsistentes. | Sí |
| **SCN-T002** | invalid EvidenceCandidate blocked | `invalid_evidence_candidate_missing_tenant.json` (falta `tenant_id` obligatorio) | El gateway intercepta la entrada, la rechaza por esquema inválido y activa el comportamiento de error. | `evidence_candidate.schema.json` | Procesamiento de datos sin contexto de tenant o sin un propietario identificado. | Sí |
| **SCN-T003** | Hermes diagnostic_authority true blocked | `evidence_candidate_diagnostic_authority_true.json` (Hermes intenta fijar autoridad diagnóstica) | La validación de esquema rechaza el archivo debido a la restricción `const: false` del parámetro. | `evidence_candidate.schema.json` | Hermes intenta suplantar la autoridad de decisión clínica o financiera del kernel. | Sí |
| **SCN-T004** | KernelRequest without evidence_refs blocked | `kernel_request_without_evidence_refs.json` (array `evidence_refs` vacío) | Error de validación de esquema por restricción de tamaño mínimo (`minItems: 1`). Petición bloqueada. | `kernel_request.schema.json` | El kernel ejecuta análisis diagnósticos sin ninguna referencia de evidencia que los respalde. | Sí |
| **SCN-T005** | OperationalAuditResult without sovereign_mark blocked | `operational_audit_result_missing_sovereign_mark.json` (ausencia de firma soberana de PymIA) | El gateway de salida detecta la falta de la marca, activa el handler fail-closed y bloquea el renderizado. | `operational_audit_result.scn.schema.json` | Renderizado de hallazgos huérfanos o que no fueron emitidos legítimamente por la autoridad de PymIA. | Sí |
| **SCN-T006** | OperationalAuditResult with missing_evidence becomes pending/block | `operational_audit_result_pending_data.json` (con listado de datos requeridos pendientes) | Se intercepta el resultado, se fuerza el estado `pending_data` y se restringe la respuesta a solicitar la evidencia restante. | `operational_audit_result.scn.schema.json` | El usuario recibe inferencias y diagnósticos sin la confirmación o la evidencia total requerida. | Sí |
| **SCN-T007** | forbidden_inferences propagate to RenderContract | `operational_audit_result_valid.json` (con inferencias prohibidas activas) | `RenderContractBuilder` propaga íntegramente la lista de restricciones hacia el contrato de render final. | `operational_audit_result.scn.schema.json` / `render_contract.schema.json` | El canal conversacional ignora las limitaciones semánticas del kernel y emite inferencias indebidas. | Sí |
| **SCN-T008** | RenderContract cannot include unauthorized finding | `render_contract_with_unauthorized_finding.json` (intento de inyección de findings en el render) | El gateway rechaza el archivo ya que el esquema de renderizado no admite arreglos estructurados de findings. | `render_contract.schema.json` | Exposición de detalles sensibles de hallazgos directamente al canal conversacional sin minimización. | Sí |
| **SCN-T009** | Hermes attempt to generate finding blocked | Petición conversacional de Hermes con payload pretendiendo actuar como origen de un hallazgo nuevo. | Intercepción por el motor de políticas de la frontera; rechazo inmediato de la acción por conflicto de policy. | `runtime_policy.example.yaml` | Hermes asume erróneamente un rol clínico de generación de conclusiones y altera el estado del caso. | Sí |
| **SCN-T010** | blocked result cannot become recommendation | `operational_audit_result_blocked.json` (estado bloqueado por violación de políticas de frontera) | Se descarta el render, se fija `allowed_tone: blocked` y se despliega exclusivamente un mensaje informativo. | `render_contract.schema.json` | Un resultado catalogado como bloqueado por el kernel es malinterpretado como recomendación de negocio. | Sí |
| **SCN-T011** | pending_data result asks for evidence only | `operational_audit_result_pending_data.json` | El contrato de render se genera restrictivo, poblando únicamente `next_questions` y anulando resúmenes clínicos. | `render_contract.schema.json` | Un estado con datos faltantes emite recomendaciones prematuras antes de completar el ciclo de evidencia. | Sí |
| **SCN-T012** | audit_trail_ref preserved | `operational_audit_result_valid.json` (con ID de traza de auditoría válido) | El campo `result_ref` en el `RenderContract` final conserva el valor original mapeado contra la traza de PymIA. | `render_contract.schema.json` | Pérdida del enlace de auditoría que permite asociar un mensaje conversacional con la ejecución que lo causó. | Sí |
| **SCN-T013** | runtime_policy forbids Telegram real in sandbox | Sandbox inicializado con credencial real de Telegram o acción prohibida `use_real_telegram_in_sandbox` activa. | El motor de políticas detiene la ejecución inmediatamente, previniendo cualquier conexión a la red externa. | `runtime_policy.example.yaml` | Filtración de datos de pruebas o suplantación de la interacción del bot real durante tests locales. | Sí |
| **SCN-T014** | runtime_policy forbids MCP-3 without authorization | Llamada al adaptador o herramientas asociadas a privilegios MCP-3 sin token/autorización explícita. | El motor de políticas cancela la acción, lanza excepción de seguridad y transiciona a estado `blocked`. | `runtime_policy.example.yaml` | Acceso descontrolado a herramientas de sistema o alteración de servicios por parte de agentes no autorizados. | Sí |
| **SCN-T015** | output minimization removes internal reasoning | `operational_audit_result_valid.json` conteniendo reasoning steps internos y trazas de computabilidad. | `RenderContractBuilder` desecha todos los metadatos internos, entregando solo la versión sintetizada whitelisted. | `render_contract.schema.json` | Fuga de lógica de negocio, reglas de cálculo, pesos matemáticos y heurísticas del kernel local. | Sí |
| **SCN-T016** | router does not degrade OperationalAuditResult to free text | `OperationalAuditResult` complejo mapeado a través del gateway y el enrutador de datos. | Se conserva la integridad tipada de campos como `audit_trail_ref`, `forbidden_inferences` y `missing_evidence`. | `operational_audit_result.scn.schema.json` / `render_contract.schema.json` | El ruteador descarta datos estructurales convirtiendo la respuesta soberana del kernel en texto plano opaco. | Sí |
| **SCN-T017** | no findings means no diagnosis | `operational_audit_result_valid.json` con campo `findings` vacío o nulo. | El render final se limita a resumir el estado operativo plano, sin inventar ni inferir patologías financieras. | `operational_audit_result.scn.schema.json` | Hallucinación de patologías contables o diagnósticos sin un sustento computacional en el kernel. | Sí |
| **SCN-T018** | multiple findings preserve structure | `operational_audit_result_valid.json` conteniendo múltiples objetos estructurados en el array de `findings`. | El gateway valida de manera exitosa la multiplicidad del array sin degradar o colapsar sus ramas internas. | `operational_audit_result.scn.schema.json` | Colapso de hallazgos complejos o eliminación de advertencias secundarias en la capa intermedia del router. | Sí |
| **SCN-T019** | invalid status blocked | `operational_audit_result_valid.json` con campo `status` no soportado en la enumeración (ej. `"partial_ok"`) | El gateway de salida arroja error de validación de contrato y enruta la respuesta al handler de bloqueo de emergencia. | `operational_audit_result.scn.schema.json` | Aceptación de estados operacionales anómalos o de transición que burlan la lógica fail-closed. | Sí |
| **SCN-T020** | policy conflict fail-closed | Ejecución donde se intercepta el flag de conflicto de reglas de seguridad o triggers superpuestos. | El sistema cae de manera inmediata a estado `blocked` total, inhabilitando la herramienta en ejecución. | `runtime_policy.example.yaml` | Evasión de la frontera soberana por medio de reglas de autorización que colisionan o que resultan ambiguas. | Sí |

## 5. Fases de test
El proceso de verificación de la frontera de soberanía SCN se estructurará en fases estrictamente secuenciales:

* **Fase A — Contract validation tests**:
  Pruebas de conformidad de esquemas JSON y YAML sobre las estructuras definidas en los contratos draft. Se asegura que ningún payload pueda violar los tipos o la obligatoriedad de campos sin ser capturado por la capa de validación.
* **Fase B — Gateway unit tests**:
  Validación aislada de los componentes lógicos propuestos (`PymIAInputGateway`, `PymIAOutputGateway`, `EvidenceCandidateValidator`, `RenderContractBuilder`). Estas pruebas unitarias simularán la inyección de payloads para verificar la lógica de transformación y minimización de outputs de frontera.
* **Fase C — Router non-degradation tests**:
  Pruebas de extremo a extremo que evalúan el flujo de datos a través del `operational_audit_router` y los gateways, validando que los metadatos complejos (`forbidden_inferences`, `missing_evidence`, etc.) no sufran aplanamiento ni degradación semántica a texto plano.
* **Fase D — Hermes sandbox dry-run tests**:
  Ejecución en el entorno aislado de pruebas (`.tmp/hermes-scn-local`) empleando configuraciones simuladas y llaves redactadas. Valida el acoplamiento de recolección de evidencia y renderizado controlado bajo un entorno real pero contenido.
* **Fase E — Human approval before live sandbox**:
  Paso final obligatorio de revisión manual del log de evidencias e historial de pruebas en el sandbox. Requiere la firma y autorización explícita por escrito del usuario humano antes de remover las restricciones de aislamiento o interactuar con APIs reales.

## 6. Fixtures futuras
Definición conceptual de las estructuras de prueba que deberán materializarse en la fase de implementación (no creadas físicamente en este hito):
* `valid_evidence_candidate.json`: Contenedor estructurado de un input de evidencia completo y legítimo enviado por Hermes.
* `invalid_evidence_candidate_missing_tenant.json`: Payload de candidato a evidencia alterado intencionalmente para omitir el identificador del tenant.
* `evidence_candidate_diagnostic_authority_true.json`: Payload que emula un intento malicioso de Hermes para auto-asignarse autoridad de diagnóstico clínico/financiero.
* `kernel_request_without_evidence_refs.json`: Petición de ejecución que carece de referencias físicas o lógicas a documentos de prueba.
* `operational_audit_result_valid.json`: Salida completa del kernel firmada, con findings específicos, trazas semánticas y marcas de política.
* `operational_audit_result_missing_sovereign_mark.json`: Salida estructurada de auditoría que carece de la firma digital de PymIA.
* `operational_audit_result_blocked.json`: Resultado del kernel con estatus de bloqueo explícito debido a violaciones de límites operativos.
* `operational_audit_result_pending_data.json`: Salida del kernel que especifica de manera precisa los documentos y datos de evidencia ausentes.
* `render_contract_valid.json`: Payload minimizado y aprobado con información segura y tono formal apto para visualización directa.
* `render_contract_with_unauthorized_finding.json`: Estructura de render que intenta forzar la inclusión de un hallazgo contable no minimizado.
* `runtime_policy_strict.yaml`: Configuración de reglas estrictas para limitar las acciones de Hermes, activar el fail-closed ante desvíos y prohibir interacciones externas.

## 7. Criterios de aceptación
Antes de proceder con cualquier fase de desarrollo de código o implementación runtime de la frontera SCN, es mandatorio satisfacer:
1. **Tests contract-only**: Validación exitosa al 100% de todos los esquemas JSON de contratos frente a sus fixtures conceptuales sin dependencias de código vivo.
2. **Tests fail-closed**: Demostración y paso de tests que fuercen escenarios de error, validando la interrupción y bloqueo del flujo de datos sin excepciones.
3. **Tests no-degradation**: Asegurar mediante aserciones estrictas que los componentes de Gateway y Router conservan íntegramente las variables complejas sin simplificaciones.
4. **Tests no-Hermes-findings**: Verificación de que cualquier intento de añadir o persistir hallazgos de forma directa en el flujo es detectado y abortado.
5. **Tests policy enforcement**: Pruebas que validen el enforzamiento de la whitelist de acciones y la denegación de procesos no declarados en la política activa.
6. **Sandbox separado**: Estructuración física completa de la ruta `.tmp/hermes-scn-local` con sus directorios de home independientes y variables dummy listas.
7. **Autorización explícita**: Aprobación escrita y directa por parte del usuario, validando la integridad del plan documental actual.

## 8. Bloqueos
Se establece de manera mandatoria el bloqueo técnico inmediato de la fase de implementación runtime en caso de presentarse cualquiera de las siguientes brechas:
* **Ausencia de sovereign_mark**: Cualquier payload que intente renderizarse en el canal sin contar con la firma digital e íntegra de PymIA.
* **Falta de propagación de forbidden_inferences**: Si el gateway o router omiten o eliminan las restricciones lógicas y de inferencia emitidas por el kernel.
* **Degradación estructural del router**: Si el `operational_audit_router` descarta campos del `OperationalAuditResult` o los unifica en campos de texto tradicionales.
* **Hermes produce findings**: Si se detecta un flujo donde Hermes es capaz de registrar hallazgos o conclusiones sin el procesamiento directo del núcleo.
* **Telegram real habilitado**: Si el token de producción de Telegram es detectado activo dentro del entorno de desarrollo o sandbox de prueba.
* **MCP-3 habilitado**: Si se intenta activar o invocar utilidades del protocolo MCP-3 sin las firmas documentales correspondientes aprobadas.
* **Falta de aislamiento de HERMES_HOME**: Si la ruta configurada para la simulación de Hermes interactúa con archivos, base de datos o logs del entorno sensible de producción.
* **Ausencia de audit_trail_ref**: Si un resultado carece de la traza correlativa que asegure la trazabilidad de la decisión.
* **Falta de RuntimePolicy activa**: Si el motor de frontera se ejecuta sin cargar un archivo de políticas activo y verificado en la whitelist.

## 9. Relación documental
Este plan documental está supeditado y mapeado directamente con el siguiente ecosistema regulatorio de PymIA:
* `docs/arquitectura/SCN_001_SOVEREIGN_COMPUTATION_BOUNDARY.md`: Define el principio fundacional de la separación estricta entre la agencia de Hermes y la autoridad de PymIA.
* `docs/arquitectura/SCN_002_CONTRACT_VALIDATION_LAYER_DESIGN.md`: Propone el diseño estructural de la Boundary Layer, Gateways, minimizadores y flujo de datos tipados.
* `docs/contracts/scn/GLOSSARY.md`: Establece el vocabulario preciso y unificado para prevenir inconsistencias semánticas en la frontera.
* `docs/hermes/HERMES_LOCAL_SCN_SANDBOX_PLAN.md`: Rigurosa delimitación física del sandbox `.tmp/hermes-scn-local` e instrucciones de aislamiento sin secretos reales.
* `docs/contracts/scn/runtime_policy.example.yaml`: Define el juego de acciones permitidas, denegadas y los disparadores fail-closed de la frontera.

## 10. Decisión
Se ratifica que este documento representa un plan de diseño técnico futuro de pruebas de frontera. Su redacción:
* **No crea pruebas unitarias o de integración reales en archivos `.py`.**
* **No ejecuta ningún script de test o validación en el sistema.**
* **No habilita la ejecución en vivo del runtime, el bot de Telegram, ni servicios en segundo plano.**
* El desarrollo de código en la frontera SCN queda estrictamente congelado y bloqueado hasta obtener la aprobación formal de este plan por parte del usuario.
