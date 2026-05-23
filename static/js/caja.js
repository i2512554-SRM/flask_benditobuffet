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
});
