document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanels = document.querySelectorAll('.tab-panel');
    const btnNuevoArticulo = document.getElementById('btnNuevoArticulo');
    const btnRegistrarCompra = document.getElementById('btnRegistrarCompra');
    const modalNuevoArticulo = document.getElementById('modalNuevoArticulo');
    const modalRegistrarCompra = document.getElementById('modalRegistrarCompra');
    const closeButtons = document.querySelectorAll('.close-modal');
    const searchInput = document.getElementById('inventarioSearch');
    const categoryFilter = document.getElementById('categoriaFilter');
    const productRows = document.querySelectorAll('#productosTable tbody tr[data-nombre]');
    const noResultsRow = document.getElementById('noResultsRow');
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

    function filterProductos() {
        const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
        const category = categoryFilter ? categoryFilter.value.toLowerCase() : '';
        let visibleCount = 0;

        productRows.forEach(row => {
            const nombre = row.dataset.nombre.toLowerCase();
            const categoria = row.dataset.categoria.toLowerCase();
            const matchesQuery = !query || nombre.includes(query) || categoria.includes(query);
            const matchesCategory = !category || categoria === category;
            const visible = matchesQuery && matchesCategory;
            row.style.display = visible ? '' : 'none';
            if (visible) visibleCount += 1;
        });

        if (noResultsRow) {
            noResultsRow.style.display = visibleCount ? 'none' : 'table-row';
        }
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

    if (searchInput) {
        searchInput.addEventListener('input', filterProductos);
    }
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterProductos);
    }

    filterProductos();

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
