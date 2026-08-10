/**
 * Sistema de Consulta DNI - API RENIEC (proxied por el servidor)
 * Consulta automática de datos DNI sin recargar página.
 * El token de la API se mantiene en el servidor (variable de entorno DNI_API_TOKEN).
 */

document.addEventListener('DOMContentLoaded', function() {
    const dniInput = document.getElementById('dniInput');
    const btnConsultarDni = document.getElementById('btnConsultarDni');
    const nombresInput = document.querySelector('input[name="nombres"]');
    const apellidoInput = document.querySelector('input[name="apellido"]');
    const dniMessage = document.getElementById('dniMessage');

    // Si no existen los elementos, no inicializar
    if (!dniInput || !btnConsultarDni || !nombresInput || !apellidoInput) {
        return;
    }

    // La consulta se hace a través del servidor Flask, que guarda el token
    const API_URL = '/api/dni';

    // Listener para botón de consultar DNI
    btnConsultarDni.addEventListener('click', async function(e) {
        e.preventDefault();
        await consultarDNI();
    });

    // Listener para Enter en el input de DNI
    dniInput.addEventListener('keypress', async function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            await consultarDNI();
        }
    });

    /**
     * Consulta datos del DNI mediante la API
     */
    async function consultarDNI() {
        const dni = dniInput.value.trim();

        // Validar DNI
        if (!dni) {
            mostrarMensaje('Por favor ingresa un DNI', 'error');
            return;
        }

        if (!/^\d{8}$/.test(dni)) {
            mostrarMensaje('El DNI debe tener exactamente 8 dígitos', 'error');
            return;
        }

        // Mostrar loading
        setLoadingDni(true);
        mostrarMensaje('Consultando DNI...', 'loading');

        try {
            const response = await fetch(`${API_URL}/${dni}`);

            if (!response.ok) {
                if (response.status === 404) {
                    mostrarMensaje('DNI no encontrado en la base de datos', 'error');
                } else if (response.status === 401) {
                    mostrarMensaje('Token de API inválido o expirado', 'error');
                } else {
                    mostrarMensaje(`Error de API: ${response.status}`, 'error');
                }
                setLoadingDni(false);
                return;
            }

            const data = await response.json();

            // Validar respuesta
            if (!data || !data.nombres) {
                mostrarMensaje('No se encontraron datos para este DNI', 'error');
                setLoadingDni(false);
                return;
            }

            // Autocompletar campos
            autocompletarCampos(data);
            mostrarMensaje('Datos cargados correctamente', 'success');

        } catch (error) {
            console.error('Error consultando DNI:', error);
            mostrarMensaje(`Error de conexión: ${error.message}`, 'error');
        } finally {
            setLoadingDni(false);
        }
    }

    /**
     * Autocompletador de campos con datos de la API
     */
    function autocompletarCampos(data) {
        // Llenar nombres
        if (data.nombres && nombresInput) {
            nombresInput.value = data.nombres.trim();
        }

        // Llenar apellido (concatenar paterno + materno si existen)
        if (apellidoInput) {
            let apellidoCompleto = '';
            if (data.apellidoPaterno) {
                apellidoCompleto += data.apellidoPaterno.trim();
            }
            if (data.apellidoMaterno) {
                if (apellidoCompleto) {
                    apellidoCompleto += ' ' + data.apellidoMaterno.trim();
                } else {
                    apellidoCompleto = data.apellidoMaterno.trim();
                }
            }
            if (apellidoCompleto) {
                apellidoInput.value = apellidoCompleto;
            }
        }
    }

    /**
     * Mostrar/ocultar loading en botón de consulta
     */
    function setLoadingDni(isLoading) {
        if (!btnConsultarDni) return;

        if (isLoading) {
            btnConsultarDni.disabled = true;
            btnConsultarDni.classList.add('loading');
            btnConsultarDni.innerHTML = 'Consultando... <i class="fa-solid fa-spinner fa-spin"></i>';
        } else {
            btnConsultarDni.disabled = false;
            btnConsultarDni.classList.remove('loading');
            btnConsultarDni.innerHTML = 'Consultar DNI <i class="fa-solid fa-magnifying-glass"></i>';
        }
    }

    /**
     * Mostrar mensajes al usuario
     */
    function mostrarMensaje(texto, tipo) {
        if (!dniMessage) return;

        dniMessage.textContent = texto;
        dniMessage.className = 'dni-message ' + tipo;

        // Auto-limpiar mensaje después de 5 segundos si es success
        if (tipo === 'success') {
            setTimeout(() => {
                dniMessage.textContent = '';
                dniMessage.className = 'dni-message';
            }, 5000);
        }
    }
});
