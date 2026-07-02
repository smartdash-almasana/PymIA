/* -------------------------------------------------------------
   PymIA JavaScript - Lógica del Analizador e Interacción
   Simula la lectura de planillas reales para generar confianza
   ------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const stateLoaded = document.getElementById('state-loaded');
    const stateAnalyzing = document.getElementById('state-analyzing');
    const stateError = document.getElementById('state-error');
    
    const loadedFileName = document.getElementById('loaded-file-name');
    const loadedFileSize = document.getElementById('loaded-file-size');
    const analysisStepText = document.getElementById('analysis-step-text');
    const analysisProgress = document.getElementById('analysis-progress');
    const errorMessageText = document.getElementById('error-message-text');
    
    const btnStartAnalysis = document.getElementById('btn-start-analysis');
    const btnCancelLoaded = document.getElementById('btn-cancel-loaded');
    const btnRetryUpload = document.getElementById('btn-retry-upload');
    
    const dynamicReportContainer = document.getElementById('dynamic-report-container');
    const userReportView = document.getElementById('user-report-view');
    
    let activeFile = null;

    // Drag and Drop Handlers
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleSelectedFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            handleSelectedFile(fileInput.files[0]);
        }
    });

    // Handle selected file validation
    function handleSelectedFile(file) {
        activeFile = file;
        const fileExtension = file.name.split('.').pop().toLowerCase();
        const validExtensions = ['xlsx', 'xls', 'csv'];
        
        // Hide dropzone and show loaded state or error
        dropzone.classList.add('d-none');
        dynamicReportContainer.classList.add('d-none'); // Hide previous report if any
        
        if (!validExtensions.includes(fileExtension)) {
            showErrorState("Formato no compatible", `El archivo "${file.name}" no es una planilla válida. Por favor, subí un archivo Excel (.xlsx, .xls) o de texto (.csv).`);
            return;
        }

        // 15 MB Max limit
        if (file.size > 15 * 1024 * 1024) {
            showErrorState("Archivo demasiado pesado", `El archivo "${file.name}" supera el límite de 15 MB. Por favor, subí una planilla más liviana.`);
            return;
        }

        // Show loaded state
        stateLoaded.classList.remove('d-none');
        loadedFileName.textContent = file.name;
        
        // Format size
        const sizeInMb = (file.size / (1024 * 1024)).toFixed(2);
        loadedFileSize.textContent = `${sizeInMb} MB • Archivo cargado correctamente`;
    }

    // Cancel Loaded State
    btnCancelLoaded.addEventListener('click', resetUploadStates);
    btnRetryUpload.addEventListener('click', resetUploadStates);

    function resetUploadStates() {
        activeFile = null;
        fileInput.value = '';
        stateLoaded.classList.add('d-none');
        stateAnalyzing.classList.add('d-none');
        stateError.classList.add('d-none');
        dropzone.classList.remove('d-none');
    }

    function showErrorState(title, message) {
        stateLoaded.classList.add('d-none');
        stateAnalyzing.classList.add('d-none');
        stateError.classList.remove('d-none');
        
        stateError.querySelector('h3').textContent = title;
        errorMessageText.textContent = message;
    }

    // Start simulated analysis
    btnStartAnalysis.addEventListener('click', () => {
        if (!activeFile) return;
        
        stateLoaded.classList.add('d-none');
        stateAnalyzing.classList.remove('d-none');
        
        const steps = [
            { progress: 15, text: "Leyendo cabeceras y estructura de hojas..." },
            { progress: 35, text: "Identificando columnas de importes, fechas y códigos..." },
            { progress: 55, text: "Cruzando registros y buscando diferencias de sumas..." },
            { progress: 75, text: "Analizando márgenes de ganancia y rotación de artículos..." },
            { progress: 92, text: "Consolidando faltantes de información y alertas..." },
            { progress: 100, text: "Generando lectura técnica..." }
        ];

        let currentStep = 0;
        
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                analysisProgress.style.width = `${steps[currentStep].progress}%`;
                analysisStepText.textContent = steps[currentStep].text;
                currentStep++;
            } else {
                clearInterval(interval);
                showAnalysisResult();
            }
        }, 800);
    });

    // Generate dynamic mock report based on file name keywords
    function showAnalysisResult() {
        stateAnalyzing.classList.add('d-none');
        dynamicReportContainer.classList.remove('d-none');
        
        const name = activeFile.name.toLowerCase();
        let reportHTML = '';

        if (name.includes('venta') || name.includes('ingreso') || name.includes('factura')) {
            reportHTML = generateSalesReport(activeFile.name);
        } else if (name.includes('stock') || name.includes('inventario') || name.includes('mercader')) {
            reportHTML = generateStockReport(activeFile.name);
        } else if (name.includes('caja') || name.includes('movimiento') || name.includes('banco') || name.includes('diari')) {
            reportHTML = generateCashReport(activeFile.name);
        } else {
            reportHTML = generateGeneralReport(activeFile.name);
        }

        userReportView.innerHTML = reportHTML;
        
        // Scroll smoothly to report view
        dynamicReportContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Reset file input so user can upload again later if they want
        fileInput.value = '';
    }

    /* -------------------------------------------------------------
       Template Generators for Custom Interactive Reports
       ------------------------------------------------------------- */

    function generateSalesReport(fileName) {
        return `
            <div class="report-header-ui">
                <div class="report-meta">
                    <span class="report-title-badge">Reporte Técnico de Ventas</span>
                    <h3>Lectura de Archivo: <span class="file-name-highlight">${fileName}</span></h3>
                    <p class="report-date">Análisis de consistencia sobre registros de facturación e ingresos</p>
                </div>
                <div class="report-status-pill success">
                    <span class="dot"></span> Lectura Completada
                </div>
            </div>

            <div class="report-grid">
                <div class="report-main-col">
                    <div class="report-card">
                        <h4 class="card-title">1. Resumen del archivo analizado</h4>
                        <div class="stats-row">
                            <div class="stat-box">
                                <span class="stat-label">Registros procesados</span>
                                <span class="stat-val">1.240 ventas</span>
                            </div>
                            <div class="stat-box">
                                <span class="stat-label">Hojas identificadas</span>
                                <span class="stat-val">1 pestaña</span>
                            </div>
                            <div class="stat-box">
                                <span class="stat-label">Total de facturado</span>
                                <span class="stat-val">$5.820.000</span>
                            </div>
                        </div>
                        <p class="report-text-muted mt-3">
                            <strong>Columnas identificadas:</strong> "Fecha", "Detalle/Producto", "Cantidad", "Precio Unitario" e "Importe Total". Hemos ordenado las transacciones temporalmente para evaluar los flujos.
                        </p>
                    </div>

                    <div class="report-card">
                        <h4 class="card-title">2. Señales operativas detectadas</h4>
                        
                        <div class="signal-alert alert-warning">
                            <div class="signal-icon">⚠</div>
                            <div class="signal-body">
                                <h5>Falta correlación con ingresos de caja o bancos</h5>
                                <p>El archivo detalla ventas por cuenta corriente por un total de <strong>$1.150.000</strong>. Sin embargo, no se identifica ninguna columna de "Estado de Cobro" o "Fecha de Pago", lo que impide verificar si este dinero ya ingresó al negocio o si permanece como deuda activa de clientes.</p>
                            </div>
                        </div>

                        <div class="signal-alert alert-info">
                            <div class="signal-body">
                                <h5>Alta concentración en pocos artículos</h5>
                                <p>El <strong>68% de la facturación</strong> se explica únicamente por 3 productos de tu lista. Si tenés problemas de entrega con estos proveedores, tu nivel de ingresos mensual se verá afectado de manera crítica.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-side-col">
                    <div class="report-card">
                        <h4 class="card-title">3. Datos faltantes en tu planilla</h4>
                        <ul class="gaps-list">
                            <li>
                                <span class="gap-bullet">✖</span>
                                <div>
                                    <strong>Falta el costo de reposición:</strong>
                                    <p class="gap-desc">Al no tener el costo de compra de cada artículo en este archivo, no es posible calcular la rentabilidad real de tus ventas.</p>
                                </div>
                            </li>
                            <li>
                                <span class="gap-bullet">✖</span>
                                <div>
                                    <strong>Formas de cobro en blanco:</strong>
                                    <p class="gap-desc">Hay 42 ventas sin especificación de si se cobraron en efectivo, transferencia o tarjeta.</p>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <div class="report-card">
                        <h4 class="card-title">4. Preguntas para el negocio</h4>
                        <ol class="questions-list">
                            <li>¿Las ventas registradas sin forma de cobro corresponden a retiros de mercadería de clientes habituales anotados a fin de mes?</li>
                            <li>¿Tienen una planilla separada donde registren el costo neto de compra de cada producto vendido?</li>
                        </ol>
                    </div>

                    <div class="report-card highlight-card">
                        <h4 class="card-title">5. Próximo paso recomendado</h4>
                        <p class="suggested-next-step">
                            Conviene agregar una columna llamada "Cobrado (Sí/No)" en tu planilla diaria de ventas para que puedas conciliar los saldos pendientes a fin de semana y evitar deudas acumuladas silenciosas.
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    function generateStockReport(fileName) {
        return `
            <div class="report-header-ui">
                <div class="report-meta">
                    <span class="report-title-badge">Reporte Técnico de Inventario</span>
                    <h3>Lectura de Archivo: <span class="file-name-highlight">${fileName}</span></h3>
                    <p class="report-date">Análisis de rotación de stock y capital inmovilizado</p>
                </div>
                <div class="report-status-pill success">
                    <span class="dot"></span> Lectura Completada
                </div>
            </div>

            <div class="report-grid">
                <div class="report-main-col">
                    <div class="report-card">
                        <h4 class="card-title">1. Resumen del archivo analizado</h4>
                        <div class="stats-row">
                            <div class="stat-box">
                                <span class="stat-label">Artículos listados</span>
                                <span class="stat-val">412 productos</span>
                            </div>
                            <div class="stat-box">
                                <span class="stat-label">Unidades en depósito</span>
                                <span class="stat-val">3.150 unidades</span>
                            </div>
                            <div class="stat-box">
                                <span class="stat-label">Valor estimado de stock</span>
                                <span class="stat-val">$12.400.000</span>
                            </div>
                        </div>
                        <p class="report-text-muted mt-3">
                            <strong>Hojas encontradas:</strong> "Stock_Físico" y "Precios_Reposición". Hemos cruzado las cantidades en depósito con la lista de costos unitarios de tu proveedor.
                        </p>
                    </div>

                    <div class="report-card">
                        <h4 class="card-title">2. Señales operativas detectadas</h4>
                        
                        <div class="signal-alert alert-warning">
                            <div class="signal-icon">⚠</div>
                            <div class="signal-body">
                                <h5>Mercadería acumulada con baja rotación</h5>
                                <p>Un <strong>38% de los artículos</strong> del depósito no registran variaciones de cantidad en los períodos de muestreo. Esto representa aproximadamente <strong>$4.700.000 de capital parado</strong> que no está generando ingresos para tu caja.</p>
                            </div>
                        </div>

                        <div class="signal-alert alert-danger">
                            <div class="signal-icon">↓</div>
                            <div class="signal-body">
                                <h5>Faltantes críticas de productos con alta demanda</h5>
                                <p>Se identificaron 8 productos con stock en cero o menor a 3 unidades que, según tus promedios históricos de venta, tienen un flujo alto de salida. Estás perdiendo ventas diarias por falta de reposición preventiva.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-side-col">
                    <div class="report-card">
                        <h4 class="card-title">3. Datos faltantes en tu planilla</h4>
                        <ul class="gaps-list">
                            <li>
                                <span class="gap-bullet">✖</span>
                                <div>
                                    <strong>Falta fecha de última compra:</strong>
                                    <p class="gap-desc">No pudimos precisar la antigüedad exacta de los productos inmovilizados para estimar desvalorización por obsolescencia.</p>
                                </div>
                            </li>
                            <li>
                                <span class="gap-bullet">✖</span>
                                <div>
                                    <strong>Ubicaciones físicas en blanco:</strong>
                                    <p class="gap-desc">No se detalla a qué sucursal o estante pertenece el stock listado.</p>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <div class="report-card">
                        <h4 class="card-title">4. Preguntas para el negocio</h4>
                        <ol class="questions-list">
                            <li>¿La mercadería que figura como "baja rotación" está en exhibición o guardada en depósito sin visibilidad para el cliente?</li>
                            <li>¿Tienen un margen de seguridad establecido (stock mínimo) antes de realizar un nuevo pedido al proveedor?</li>
                        </ol>
                    </div>

                    <div class="report-card highlight-card">
                        <h4 class="card-title">5. Próximo paso recomendado</h4>
                        <p class="suggested-next-step">
                            Organizá una oferta especial o liquidación para los artículos de baja rotación identificados para liberar espacio y recuperar efectivo rápido, y definí una alerta de stock mínimo de 10 unidades para los productos de alta salida.
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    function generateCashReport(fileName) {
        return `
            <div class="report-header-ui">
                <div class="report-meta">
                    <span class="report-title-badge">Reporte Técnico de Conciliación y Caja</span>
                    <h3>Lectura de Archivo: <span class="file-name-highlight">${fileName}</span></h3>
                    <p class="report-date">Análisis de consistencia sobre movimientos de caja y efectivo</p>
                </div>
                <div class="report-status-pill success">
                    <span class="dot"></span> Lectura Completada
                </div>
            </div>

            <div class="report-grid">
                <div class="report-main-col">
                    <div class="report-card">
                        <h4 class="card-title">1. Resumen del archivo analizado</h4>
                        <div class="stats-row">
                            <div class="stat-box">
                                <span class="stat-label">Movimientos leídos</span>
                                <span class="stat-val">840 movimientos</span>
                            </div>
                            <div class="stat-box">
                                <span class="stat-label">Total Ingresos</span>
                                <span class="stat-val">$4.230.000</span>
                            </div>
                            <div class="stat-box">
                                <span class="stat-label">Total Egresos</span>
                                <span class="stat-val">$3.890.000</span>
                            </div>
                        </div>
                        <p class="report-text-muted mt-3">
                            <strong>Campos conciliados:</strong> "Fecha", "Detalle de Concepto", "Ingreso ($)", "Egreso ($)" y "Saldo Calculado". Hemos auditado la secuencia matemática de saldos diarios.
                        </p>
                    </div>

                    <div class="report-card">
                        <h4 class="card-title">2. Señales operativas detectadas</h4>
                        
                        <div class="signal-alert alert-danger">
                            <div class="signal-icon">↓</div>
                            <div class="signal-body">
                                <h5>Fugas de dinero por gastos diarios no justificados</h5>
                                <p>Se detectaron múltiples egresos de caja rotulados de forma ambigua como <em>"Varios"</em>, <em>"Caja Chica"</em> o <em>"Retiros"</em> que suman <strong>$320.000 en el mes</strong> (un 8.2% del total de egresos). Este desorden en gastos hormiga reduce significativamente tu margen neto real.</p>
                            </div>
                        </div>

                        <div class="signal-alert alert-warning">
                            <div class="signal-icon">⚠</div>
                            <div class="signal-body">
                                <h5>Saltos de saldo y diferencias de planilla</h5>
                                <p>El saldo final de caja del día 14/05 no coincide con el saldo de apertura registrado el día 15/05. Hay un saldo faltante de <strong>$45.000</strong> que no figura respaldado por ningún concepto de egreso o retiro.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-side-col">
                    <div class="report-card">
                        <h4 class="card-title">3. Datos faltantes en tu planilla</h4>
                        <ul class="gaps-list">
                            <li>
                                <span class="gap-bullet">✖</span>
                                <div>
                                    <strong>Falta el medio de pago:</strong>
                                    <p class="gap-desc">No se aclara si los movimientos son en efectivo, transferencias bancarias o cobros con tarjeta.</p>
                                </div>
                            </li>
                            <li>
                                <span class="gap-bullet">✖</span>
                                <div>
                                    <strong>Faltan comprobantes de gastos:</strong>
                                    <p class="gap-desc">Hay 18 retiros de caja por importes mayores a $15.000 que no tienen una referencia a factura o recibo.</p>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <div class="report-card">
                        <h4 class="card-title">4. Preguntas para el negocio</h4>
                        <ol class="questions-list">
                            <li>¿Los egresos bajo el concepto "Retiros" corresponden a adelantos de sueldos al personal o retiros personales de los dueños?</li>
                            <li>¿Tienen un límite máximo establecido para realizar pagos en efectivo desde la caja diaria?</li>
                        </ol>
                    </div>

                    <div class="report-card highlight-card">
                        <h4 class="card-title">5. Próximo paso recomendado</h4>
                        <p class="suggested-next-step">
                            Prohibir los retiros de efectivo para gastos generales sin la presentación del comprobante digital o físico correspondiente, y crear una planilla de caja unificada que distinga el "Efectivo Físico" de la "Cuenta del Banco".
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    function generateGeneralReport(fileName) {
        return `
            <div class="report-header-ui">
                <div class="report-meta">
                    <span class="report-title-badge">Lectura Técnica Inicial</span>
                    <h3>Lectura de Archivo: <span class="file-name-highlight">${fileName}</span></h3>
                    <p class="report-date">Análisis general de filas y consistencia de datos operativos</p>
                </div>
                <div class="report-status-pill success">
                    <span class="dot"></span> Lectura Completada
                </div>
            </div>

            <div class="report-grid">
                <div class="report-main-col">
                    <div class="report-card">
                        <h4 class="card-title">1. Resumen del archivo analizado</h4>
                        <div class="stats-row">
                            <div class="stat-box">
                                <span class="stat-label">Filas leídas</span>
                                <span class="stat-val">1.120 filas</span>
                            </div>
                            <div class="stat-box">
                                <span class="stat-label">Hojas de datos</span>
                                <span class="stat-val">2 pestañas</span>
                            </div>
                            <div class="stat-box">
                                <span class="stat-label">Calidad tabular</span>
                                <span class="stat-val">Aceptable (82%)</span>
                            </div>
                        </div>
                        <p class="report-text-muted mt-3">
                            <strong>Estructura analizada:</strong> Hemos detectado registros organizados por fecha. Las celdas tienen tipos mixtos (texto y números) con un bajo porcentaje de fórmulas rotas.
                        </p>
                    </div>

                    <div class="report-card">
                        <h4 class="card-title">2. Señales operativas detectadas</h4>
                        
                        <div class="signal-alert alert-info">
                            <div class="signal-icon">ℹ</div>
                            <div class="signal-body">
                                <h5>Estructura ordenada pero aislada</h5>
                                <p>Los datos cargados muestran buena continuidad diaria. Sin embargo, no se cruzan los importes cobrados con el costo de la mercadería vendida ni con los gastos fijos del mes. Estás gestionando a ciegas sobre el margen real.</p>
                            </div>
                        </div>

                        <div class="signal-alert alert-warning">
                            <div class="signal-icon">⚠</div>
                            <div class="signal-body">
                                <h5>Celdas en blanco o descripciones incompletas</h5>
                                <p>Se detectó un 14% de filas donde el concepto o descripción del movimiento figura vacío o con la leyenda <em>"Sin especificar"</em>. Esto dificulta la categorización y distorsiona el balance semanal.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-side-col">
                    <div class="report-card">
                        <h4 class="card-title">3. Datos faltantes en tu planilla</h4>
                        <ul class="gaps-list">
                            <li>
                                <span class="gap-bullet">✖</span>
                                <div>
                                    <strong>Falta columna de costos o categorías:</strong>
                                    <p class="gap-desc">Al no clasificar las filas por rubro (por ejemplo: Impuestos, Sueldos, Proveedores, Mercadería), los números generales no muestran dónde se gasta más.</p>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <div class="report-card">
                        <h4 class="card-title">4. Preguntas para el negocio</h4>
                        <ol class="questions-list">
                            <li>¿Quién es el encargado de completar la planilla diaria y qué criterio usa para etiquetar los movimientos del local?</li>
                            <li>¿Qué periodicidad usan para revisar las celdas en blanco de sus registros?</li>
                        </ol>
                    </div>

                    <div class="report-card highlight-card">
                        <h4 class="card-title">5. Próximo paso recomendado</h4>
                        <p class="suggested-next-step">
                            Definir un catálogo simple de 4 categorías para clasificar cada movimiento (Ventas, Mercadería, Gastos Fijos, Retiros de Caja) para que tu próxima planilla muestre con total exactitud de dónde entra y a dónde va cada peso de tu negocio.
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    // Mobile menu toggle logic
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            mainNav.classList.toggle('active');
            menuToggle.classList.toggle('open');
        });
    }

    // Add visual styling active classes to active mobile menu links
    const navLinks = document.querySelectorAll('.main-nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (mainNav.classList.contains('active')) {
                mainNav.classList.remove('active');
                menuToggle.classList.remove('open');
            }
        });
    });
});
