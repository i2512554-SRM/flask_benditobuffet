document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("formTransaccion");
    const btnOpenCerrarCaja = document.getElementById("btnOpenCerrarCaja");
    const modal = document.getElementById("modalCerrarCaja");
    const btnCancelarCerrar = document.getElementById("btnCancelarCerrar");
    const btnConfirmarCerrar = document.getElementById("btnConfirmarCerrar");
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabPanels = document.querySelectorAll(".tab-panel");

    tabButtons.forEach(button => {
        button.addEventListener("click", function() {
            const target = this.dataset.tab;
            tabButtons.forEach(btn => btn.classList.toggle("active", btn === this));
            tabPanels.forEach(panel => panel.classList.toggle("active", panel.id === target));
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    if (btnOpenCerrarCaja) {
        btnOpenCerrarCaja.addEventListener("click", function() {
            modal.classList.add("active");
        });
    }

    if (btnCancelarCerrar) {
        btnCancelarCerrar.addEventListener("click", function() {
            modal.classList.remove("active");
        });
    }

    if (btnConfirmarCerrar) {
        // El envío del cierre de caja se maneja por el formulario HTML normal.
    }

    function updateResumen(data) {
        if (!data) return;
        const ventas = document.querySelector(".stats .card:nth-child(1) h2");
        const gastos = document.querySelector(".stats .card:nth-child(2) h2");
        const neto = document.querySelector(".stats .card:nth-child(3) h2");
        if (ventas) ventas.textContent = `$${data.ventas_dia.toFixed(2)}`;
        if (gastos) gastos.textContent = `$${data.gastos_dia.toFixed(2)}`;
        if (neto) neto.textContent = `$${data.neto_dia.toFixed(2)}`;
    }

    // Nueva categoría
    const btnNuevaCategoria = document.getElementById("btnNuevaCategoria");
    const modalCategoria = document.getElementById("modalNuevaCategoria");
    const formCategoria = document.getElementById("formNuevaCategoria");
    const inputCategoria = document.getElementById("nuevaCategoriaNombre");
    const errorCategoria = document.getElementById("categoriaError");
    const selectCategoria = document.getElementById("categoria");

    function openModal(modal) {
        if (!modal) return;
        modal.classList.add("active");
    }

    function closeModal(modal) {
        if (!modal) return;
        modal.classList.remove("active");
    }

    if (btnNuevaCategoria) {
        btnNuevaCategoria.addEventListener("click", function() {
            inputCategoria.value = "";
            errorCategoria.classList.add("hidden");
            openModal(modalCategoria);
            inputCategoria.focus();
        });
    }

    if (formCategoria) {
        formCategoria.addEventListener("submit", function(e) {
            e.preventDefault();
            const nombre = inputCategoria.value.trim();
            if (!nombre) {
                errorCategoria.textContent = "El nombre es obligatorio";
                errorCategoria.classList.remove("hidden");
                return;
            }
            errorCategoria.classList.add("hidden");
            const btnSubmit = formCategoria.querySelector('button[type="submit"]');
            window.setLoadingState(btnSubmit);
            fetch("/caja/categorias/nuevo", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ nombre: nombre })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                window.restoreLoadingState(btnSubmit);
                if (data.success) {
                    var opt = document.createElement("option");
                    opt.value = data.nombre;
                    opt.textContent = data.nombre;
                    selectCategoria.appendChild(opt);
                    selectCategoria.value = data.nombre;
                    closeModal(modalCategoria);
                } else {
                    errorCategoria.textContent = data.message || "Error al crear categoría";
                    errorCategoria.classList.remove("hidden");
                }
            })
            .catch(function() {
                window.restoreLoadingState(btnSubmit);
                errorCategoria.textContent = "Error de conexión";
                errorCategoria.classList.remove("hidden");
            });
        });
    }

    // Cerrar modales al hacer clic fuera
    document.addEventListener("click", function(e) {
        if (e.target.classList.contains("modal")) {
            closeModal(e.target);
        }
    });
});
