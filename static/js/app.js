// CAMBIO DE ROLES (LOGIN)

function cambiarRol(rol, elemento){

    const roles = document.querySelectorAll(".rol");
    roles.forEach(r => r.classList.remove("activo"));

    elemento.classList.add("activo");

    const titulo = document.getElementById("tituloRol");
    const desc = document.getElementById("descRol");
    const boton = document.getElementById("btnLogin");

    // Cambiar contenido según rol
    if(rol === "administrador"){
        titulo.innerText = "Administrador";
        desc.innerText = "Acceso completo a todos los módulos del sistema.";
        boton.innerText = "Entrar como Administrador";
    }

    if(rol === "cajero"){
        titulo.innerText = "Cajero";
        desc.innerText = "Apertura y cierre de caja, registro de ingresos y egresos, reportes diarios de caja.";
        boton.innerText = "Entrar como Cajero";
    }

    if(rol === "cocina"){
        titulo.innerText = "Cocina";
        desc.innerText = "Visualización de pedidos, gestión de platos y actualización del estado de preparación.";
        boton.innerText = "Entrar como Cocina";
    }

    if(rol === "trabajador"){
        titulo.innerText = "Trabajador";
        desc.innerText = "Acceso a perfil personal, consulta de sueldo asignado e historial de pagos.";
        boton.innerText = "Entrar como Trabajador";
    }
}

function toggleDarkMode() {
    if (window.benditoTheme && typeof window.benditoTheme.toggle === 'function') {
        window.benditoTheme.toggle();
    } else {
        document.body.classList.toggle('dark-mode');
    }
}

function getLoadingText(element) {
    if (!element) return 'Procesando...';
    const customText = element.dataset.loadingText;
    if (customText) return customText;

    const label = (element.dataset.action || element.textContent || '').trim().toLowerCase();
    if (/login|ingresar|acceder/.test(label)) return 'Ingresando...';
    if (/registrar|guardar|nuevo|submit/.test(label)) return 'Guardando...';
    if (/actualizar|editar|modificar/.test(label)) return 'Actualizando...';
    if (/eliminar|borrar|quitar/.test(label)) return 'Eliminando...';
    if (/cerrar caja|cerrando|caja/.test(label)) return 'Cerrando caja...';
    if (/buscar|consultar|filtrar/.test(label)) return 'Consultando...';
    if (/procesar|procesando|enviando/.test(label)) return 'Procesando...';

    return 'Procesando...';
}

function setLoadingState(element) {
    if (!element || element.dataset.loadingActive === 'true') return;

    const originalHtml = element.innerHTML;
    element.dataset.originalHtml = originalHtml;

    const loadingText = getLoadingText(element);
    const loadingIcon = element.dataset.loadingIcon || 'fa-solid fa-spinner fa-spin';
    element.innerHTML = `${loadingText} <i class="${loadingIcon}"></i>`;
    element.disabled = true;
    element.classList.add('loading');
    element.setAttribute('aria-busy', 'true');
    element.dataset.loadingActive = 'true';
}

function restoreLoadingState(element) {
    if (!element || element.dataset.loadingActive !== 'true') return;

    if (typeof element.dataset.originalHtml !== 'undefined') {
        element.innerHTML = element.dataset.originalHtml;
    }
    element.disabled = false;
    element.classList.remove('loading');
    element.removeAttribute('aria-busy');
    delete element.dataset.loadingActive;
}

function getSubmitButton(form) {
    if (!(form instanceof HTMLFormElement)) return null;
    return form.querySelector('button[type="submit"], input[type="submit"]');
}

function attachGlobalLoadingListeners() {
    // Listener para submit de formularios
    document.addEventListener('submit', function(event) {
        const form = event.target;
        if (!(form instanceof HTMLFormElement)) return;

        const submitButton = event.submitter || getSubmitButton(form);
        if (submitButton && !submitButton.disabled) {
            setLoadingState(submitButton);
        }
    }, true);

    // Listener para botones de acción (NO submit) con data-loading-text
    document.addEventListener('click', function(event) {
        const button = event.target.closest('button[data-loading-text]:not([type="submit"]), input[type="button"][data-loading-text], a button[data-loading-text]');
        if (!button || button.disabled) return;
        setLoadingState(button);
    }, true);
}

window.setLoadingState = setLoadingState;
window.restoreLoadingState = restoreLoadingState;
window.getSubmitButton = getSubmitButton;

document.addEventListener('DOMContentLoaded', attachGlobalLoadingListeners);
