document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanels = document.querySelectorAll('.tab-panel');
    const btnNuevoArticulo = document.getElementById('btnNuevoArticulo');
    const btnRegistrarCompra = document.getElementById('btnRegistrarCompra');
    const modalNuevoArticulo = document.getElementById('modalNuevoArticulo');
    const modalRegistrarCompra = document.getElementById('modalRegistrarCompra');
    const closeButtons = document.querySelectorAll('.close-modal');
    const sortHeaders = document.querySelectorAll('th.sortable');
    let sortOrder = { fecha: 'desc' };

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = this.dataset.tab;
            tabButtons.forEach(btn => btn.classList.toggle('active', btn === this));
            tabPanels.forEach(panel => panel.classList.toggle('active', panel.id === target));
        });
    });

    function openModal(modal) {
        if (!modal) return;
        modal.classList.add('active');
    }

    function closeModal(modal) {
        if (!modal) return;
        modal.classList.remove('active');
    }

    function sortTable(sortBy) {
        const rows = Array.from(document.querySelectorAll('#productosTable tbody tr[data-nombre]'));
        
        rows.sort((a, b) => {
            let aVal, bVal;
            
            if (sortBy === 'fecha') {
                aVal = parseFloat(a.dataset.fecha) || 0;
                bVal = parseFloat(b.dataset.fecha) || 0;
            } else {
                return 0;
            }
            
            return sortOrder[sortBy] === 'asc' ? aVal - bVal : bVal - aVal;
        });
        
        const tbody = document.querySelector('#productosTable tbody');
        rows.forEach(row => tbody.appendChild(row));
        
        sortOrder[sortBy] = sortOrder[sortBy] === 'asc' ? 'desc' : 'asc';
        
        sortHeaders.forEach(header => {
            const icon = header.querySelector('i');
            if (header.dataset.sort === sortBy) {
                icon.className = sortOrder[sortBy] === 'asc' ? 'fa-solid fa-arrow-up' : 'fa-solid fa-arrow-down';
            } else {
                icon.className = 'fa-solid fa-arrow-down';
            }
        });
    }

    if (btnNuevoArticulo) {
        btnNuevoArticulo.addEventListener('click', function() {
            openModal(modalNuevoArticulo);
        });
    }

    if (btnRegistrarCompra) {
        btnRegistrarCompra.addEventListener('click', function() {
            openModal(modalRegistrarCompra);
        });
    }

    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal);
        });
    });

    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target);
        }
    });

    sortHeaders.forEach(header => {
        header.addEventListener('click', function() {
            sortTable(this.dataset.sort);
        });
    });

    // Edit article modal
    const modalEditar = document.getElementById('modalEditarArticulo');
    const editForm = document.getElementById('editForm');
    const editNombre = document.getElementById('editNombreDisplay');
    const editPrecio = document.getElementById('editPrecio');
    const editStock = document.getElementById('editStock');

    document.querySelectorAll('.btn-editar-articulo').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.id;
            const nombre = this.dataset.nombre;
            const precio = this.dataset.precio;
            const stock = this.dataset.stock;
            editNombre.textContent = nombre;
            editPrecio.value = precio;
            editStock.value = stock;
            editForm.action = '/inventario/articulo/editar/' + id;
            openModal(modalEditar);
        });
    });
});
