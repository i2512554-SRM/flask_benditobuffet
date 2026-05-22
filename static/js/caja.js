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

    if (form) {
        form.addEventListener("submit", async function(event) {
            event.preventDefault();
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            });

            const body = await response.json().catch(() => null);
            if (!response.ok) {
                alert(body?.message || "Ocurrió un error al registrar la transacción.");
                return;
            }

            updateResumen(body);
            form.reset();
            alert(body?.message || "Transacción registrada correctamente.");
            window.location.reload();
        });
    }

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
        btnConfirmarCerrar.addEventListener("click", async function() {
            const observaciones = document.getElementById("observaciones").value;
            const payload = new FormData();
            payload.append("observaciones", observaciones);

            const response = await fetch("/caja/cerrar", {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: payload
            });
            const body = await response.json().catch(() => null);
            if (!response.ok) {
                alert(body?.message || "Error al cerrar la caja.");
                return;
            }
            modal.classList.remove("active");
            alert(body?.message || "Caja cerrada correctamente.");
            window.location.reload();
        });
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
