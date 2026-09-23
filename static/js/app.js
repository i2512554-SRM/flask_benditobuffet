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
    document.body.classList.toggle("dark-mode");
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference on page load
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
