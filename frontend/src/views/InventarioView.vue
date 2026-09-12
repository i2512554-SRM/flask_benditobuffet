<template>
  <div class="inventario-view">
    <div class="page-hero">
      <VolverBtn to="/inventario" />
      <h1>Operaciones de Inventario</h1>
      <p>Productos, unidades y stock. Las inversiones registran compras; las entradas de stock no registran gastos.</p>
    </div>

    <div class="actions">
      <Button :disabled="$saving" label="Nuevo producto" icon="pi pi-plus" @click="agregarDialog" />
      <Button :disabled="$saving" label="Entrada sin compra" icon="pi pi-arrow-down" severity="secondary" @click="abrirAgregarStock()" />
      <Button :disabled="$saving" label="Registrar salida" icon="pi pi-arrow-up" severity="secondary" @click="abrirRegistrarSalida()" />
      <Button :disabled="$saving" v-if="esAdmin" label="Registrar inversión (compra)" icon="pi pi-cart-plus" severity="secondary" @click="openCompra" />
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Valor total inventario</div>
        <div class="stat-value">S/. {{ fmt(resumen.valor_total) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Inversiones del mes</div>
        <div class="stat-value">S/. {{ fmt(resumen.inversiones_mes) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Artículos registrados</div>
        <div class="stat-value">{{ resumen.articulos_registrados }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Productos del mes</div>
        <div class="stat-value">{{ resumen.productos_mes }}</div>
      </div>
    </div>

    <div class="view-toggle">
      <Button :disabled="$saving" label="Productos" :class="{ active: vista === 'productos' }" severity="secondary" plain @click="vista = 'productos'" />
      <Button :disabled="$saving" v-if="esAdmin" label="Inversiones (compras)" :class="{ active: vista === 'compras' }" severity="secondary" plain @click="vista = 'compras'" />
      <Button :disabled="$saving" v-if="esAdmin && inversiones.length" label="Registros anteriores" :class="{ active: vista === 'inversiones' }" severity="secondary" plain @click="vista = 'inversiones'" />
      <Button :disabled="$saving" label="Movimientos" :class="{ active: vista === 'movimientos' }" severity="secondary" plain @click="vista = 'movimientos'" />
    </div>

    <div class="table-card" v-if="vista === 'productos'">
      <div class="table-header">
        <h2>Productos</h2>
        <div class="search-box">
          <InputText v-model="busqueda" placeholder="Buscar producto o categoría..." class="w-full" @input="cargarProductos" />
          <Select v-model="categoriaFiltro" :options="categorias" optionLabel="nombre" optionValue="id_categoria" placeholder="Todas las categorías" showClear class="w-full" @update:model-value="cargarProductos" />
          <div class="check-activos">
            <Checkbox v-model="mostrarInactivos" inputId="mostrarInactivos" binary @update:model-value="cargarProductos" />
            <label for="mostrarInactivos">Ver inactivos</label>
          </div>
        </div>
      </div>
      <DataTable :value="productos" data-key="id_producto" :paginator="true" :rows="10" class="mt-4">
        <Column field="nombre" header="Producto" sortable></Column>
        <Column field="categoria" header="Categoría" sortable></Column>
        <Column field="precio" header="Precio" sortable>
          <template #body="slotProps">S/. {{ fmt2(slotProps.data.precio) }}</template>
        </Column>
        <Column field="unidad_medida" header="Unidad" sortable></Column>
        <Column field="stock" header="Stock" sortable>
          <template #body="slotProps">
            <span :class="['stock-num', { 'stock-cero': Number(slotProps.data.stock) <= 0 }]">{{ fmtStock(slotProps.data.stock) }} {{ unidadLabel(slotProps.data.unidad_medida) }}</span>
          </template>
        </Column>
        <Column field="estado" header="Estado" sortable>
          <template #body="slotProps">
            <span :class="['estado-badge', slotProps.data.estado ? 'estado-activo' : 'estado-inactivo']">
              {{ slotProps.data.estado ? 'Activo' : 'Inactivo' }}
            </span>
          </template>
        </Column>
        <Column header="Acciones" :exportable="false">
          <template #body="slotProps">
            <div class="row-actions">
              <Button :disabled="$saving" icon="pi pi-eye" severity="info" text rounded @click="verProducto(slotProps.data)" />
              <Button :disabled="$saving" icon="pi pi-pencil" severity="secondary" text rounded @click="editar(slotProps.data)" />
              <Button :disabled="$saving" icon="pi pi-arrow-down" text rounded title="Agregar stock" @click="abrirAgregarStock(slotProps.data)" />
              <Button :disabled="$saving" icon="pi pi-arrow-up" text rounded title="Registrar salida" @click="abrirRegistrarSalida(slotProps.data)" />
              <Button v-if="esAdmin" :disabled="$saving" :icon="slotProps.data.estado ? 'pi pi-ban' : 'pi pi-check'" :severity="slotProps.data.estado ? 'danger' : 'success'" text rounded :title="slotProps.data.estado ? 'Desactivar' : 'Activar'" @click="toggleEstado(slotProps.data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'compras'">
      <h2>Inversiones en productos</h2>
      <DataTable :value="compras" :paginator="true" :rows="10" class="mt-4">
        <Column field="codigo" header="Código" sortable></Column>
        <Column field="fecha" header="Fecha" sortable>
          <template #body="slotProps">{{ fmtFecha(slotProps.data.fecha) }}</template>
        </Column>
        <Column field="proveedor" header="Proveedor">
          <template #body="slotProps">{{ slotProps.data.proveedor || '-' }}</template>
        </Column>
        <Column field="n_detalle" header="Productos" sortable></Column>
        <Column field="total_compra" header="Total" sortable>
          <template #body="slotProps">S/. {{ fmt2(slotProps.data.total_compra) }}</template>
        </Column>
        <Column field="estado" header="Estado" sortable></Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button :disabled="$saving" icon="pi pi-eye" severity="info" text rounded @click="verCompra(slotProps.data)" />
            <Button :disabled="$saving" icon="pi pi-trash" severity="danger" text rounded @click="eliminarCompra(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'inversiones'">
      <h2>Inversiones</h2>
      <DataTable :value="inversiones" :paginator="true" :rows="10" class="mt-4">
        <Column field="fecha" header="Fecha" sortable>
          <template #body="slotProps">{{ fmtFecha(slotProps.data.fecha) }}</template>
        </Column>
        <Column field="descripcion" header="Descripción" sortable></Column>
        <Column field="proveedor" header="Proveedor">
          <template #body="slotProps">{{ slotProps.data.proveedor || '-' }}</template>
        </Column>
        <Column field="monto" header="Monto" sortable>
          <template #body="slotProps">S/. {{ fmt2(slotProps.data.monto) }}</template>
        </Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button :disabled="$saving" icon="pi pi-eye" severity="info" text rounded @click="verInversion(slotProps.data)" />
            <Button :disabled="$saving" icon="pi pi-trash" severity="danger" text rounded @click="eliminarInversion(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <div class="table-card" v-if="vista === 'movimientos'">
      <div class="table-header">
        <h2>Historial de movimientos</h2>
        <div class="search-box">
          <InputText v-model="movBusqueda" placeholder="Buscar por producto..." class="w-full" @input="cargarMovimientos" />
          <Select v-model="movTipo" :options="['Entrada', 'Salida', 'Ajuste']" placeholder="Todos los tipos" showClear class="w-full" @update:model-value="cargarMovimientos" />
        </div>
      </div>
      <DataTable :value="movimientos" :paginator="true" :rows="10" class="mt-4">
        <Column field="fecha" header="Fecha" sortable>
          <template #body="slotProps">{{ fmtFechaHora(slotProps.data.fecha) }}</template>
        </Column>
        <Column field="producto" header="Producto" sortable></Column>
        <Column field="tipo" header="Tipo" sortable>
          <template #body="slotProps">
            <span :class="['mov-tipo', 'mov-' + slotProps.data.tipo.toLowerCase()]">{{ slotProps.data.tipo }}</span>
          </template>
        </Column>
        <Column field="cantidad" header="Cantidad" sortable>
          <template #body="slotProps">
            <span :class="['mov-cant', { 'mov-menos': Number(slotProps.data.cantidad) < 0 }]">
              {{ firmarCantidad(slotProps.data.cantidad) }} {{ unidadLabel(slotProps.data.unidad) }}
            </span>
          </template>
        </Column>
        <Column field="unidad" header="Unidad" sortable>
          <template #body="slotProps">{{ slotProps.data.unidad || '-' }}</template>
        </Column>
        <Column field="stock_anterior" header="Stock anterior" sortable>
          <template #body="slotProps">{{ fmtStock(slotProps.data.stock_anterior) }} {{ slotProps.data.unidad || '' }}</template>
        </Column>
        <Column field="stock_posterior" header="Stock posterior" sortable>
          <template #body="slotProps">{{ fmtStock(slotProps.data.stock_posterior) }} {{ slotProps.data.unidad || '' }}</template>
        </Column>
        <Column field="motivo" header="Motivo"></Column>
        <Column field="usuario" header="Responsable">
          <template #body="slotProps">{{ slotProps.data.usuario || '-' }}</template>
        </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="productoDialog" :header="editing.id_producto ? 'Editar Producto' : 'Nuevo Producto'" :modal="true" :style="{ width: '520px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="nombre">Nombre *</label>
          <InputText id="nombre" v-model="form.nombre" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="unidad_medida">Unidad de medida</label>
          <Select id="unidad_medida" v-model="form.unidad_medida" :options="unidades" optionLabel="label" optionValue="valor" class="w-full" placeholder="Selecciona Kg, Un o Lt" />
        </div>
        <div class="field col-6">
          <label for="estado">Estado</label>
          <Select id="estado" v-model="form.estado" :options="[{ label: 'Activo', valor: true }, { label: 'Inactivo', valor: false }]" optionLabel="label" optionValue="valor" class="w-full" />
        </div>
        <div class="field col-6">
          <label for="categoria">Categoría</label>
          <Select id="categoria" v-model="form.id_categoria" :options="categorias" optionLabel="nombre" optionValue="id_categoria" showClear class="w-full" />
        </div>
        <div class="field col-6">
          <label for="precio">Precio</label>
          <InputNumber :maxFractionDigits="2" placeholder="Ej. 100.00" id="precio" v-model="form.precio" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-6" v-if="!editing.id_producto">
          <label for="stock">Stock inicial</label>
          <InputNumber :maxFractionDigits="2" placeholder="Ej. 100.00" id="stock" v-model="form.stock" :min="0" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="descripcion">Descripción</label>
          <Textarea id="descripcion" v-model="form.descripcion" rows="2" class="w-full" />
        </div>
      </div>
      <div v-if="duplicadoInfo" class="dup-advice">
        <i class="pi pi-exclamation-triangle"></i>
        <span>El producto "{{ duplicadoInfo.nombre }}" ya existe en el sistema. Si deseas aumentar su cantidad usa "Agregar stock".</span>
        <Button :disabled="$saving" label="Ir a Agregar stock" icon="pi pi-arrow-down" size="small" @click="irAgregarStock()" />
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="productoDialog = false" />
        <Button :disabled="$saving" label="Guardar" @click="guardarProducto" />
      </template>
    </Dialog>

    <Dialog v-model:visible="stockDialog" :header="stockModo === 'entrada' ? 'Agregar stock' : 'Registrar salida'" :modal="true" :style="{ width: '460px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="stock-producto">Producto *</label>
          <Select id="stock-producto" v-model="stockForm.id_producto" :options="productosActivos" filter optionLabel="nombre" optionValue="id_producto" placeholder="Selecciona un producto activo" class="w-full">
            <template #option="slotProps">
              <div class="opt-prod">
                <span>{{ slotProps.option.nombre }}</span>
                <span class="opt-stock">{{ fmtStock(slotProps.option.stock) }} {{ unidadLabel(slotProps.option.unidad_medida) }}</span>
              </div>
            </template>
          </Select>
        </div>
        <div class="field col-6" v-if="stockProducto">
          <label>Stock actual</label>
          <div class="stock-actual">{{ fmtStock(stockProducto.stock) }} {{ unidadLabel(stockProducto.unidad_medida) }}</div>
        </div>
        <div class="field col-6">
          <label>Unidad</label>
          <div class="stock-actual">{{ stockProducto ? unidadLabel(stockProducto.unidad_medida) : '-' }}</div>
        </div>
        <div class="field col-6">
          <label for="stock-cantidad">Cantidad *</label>
          <InputNumber :maxFractionDigits="2" placeholder="Ej. 100.00" id="stock-cantidad" v-model="stockForm.cantidad" :min="0" class="w-full" />
        </div>
        <div class="field col-12" v-if="stockModo === 'entrada'">
          <label for="stock-motivo">Motivo (opcional)</label>
          <InputText id="stock-motivo" v-model="stockForm.motivo" placeholder="Ej. Reposición de almacén" class="w-full" />
        </div>
        <div class="field col-12" v-else>
          <label for="stock-motivo">Motivo *</label>
          <InputText id="stock-motivo" v-model="stockForm.motivo" placeholder="Ej. Preparación de menú del día" class="w-full" />
        </div>
      </div>
      <div v-if="stockWarning" class="dup-advice warn">
        <i class="pi pi-exclamation-triangle"></i>
        <span>{{ stockWarning }}</span>
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="stockDialog = false" />
        <Button :disabled="$saving" label="Confirmar" @click="confirmarStock" />
      </template>
    </Dialog>

    <Dialog v-model:visible="productoVerDialog" header="Detalle de producto" :modal="true" :style="{ width: '480px' }">
      <div v-if="productoVisto.id_producto" class="detalle-info">
        <div class="d-row"><span class="d-label">Nombre</span><span>{{ productoVisto.nombre }}</span></div>
        <div class="d-row"><span class="d-label">Unidad</span><span>{{ unidadLabel(productoVisto.unidad_medida) }}</span></div>
        <div class="d-row"><span class="d-label">Stock</span><span>{{ fmtStock(productoVisto.stock) }} {{ unidadLabel(productoVisto.unidad_medida) }}</span></div>
        <div class="d-row"><span class="d-label">Precio</span><span>S/. {{ fmt2(productoVisto.precio) }}</span></div>
        <div class="d-row"><span class="d-label">Categoría</span><span>{{ productoVisto.categoria || '-' }}</span></div>
        <div class="d-row"><span class="d-label">Estado</span><span>{{ productoVisto.estado ? 'Activo' : 'Inactivo' }}</span></div>
        <div class="d-row"><span class="d-label">Descripción</span><span>{{ productoVisto.descripcion || '-' }}</span></div>
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cerrar" severity="secondary" @click="productoVerDialog = false" />
      </template>
    </Dialog>

    <Dialog v-model:visible="compraDialog" header="Registrar inversión en productos" :modal="true" :style="{ width: '620px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="proveedor">Proveedor (opcional)</label>
          <Select id="proveedor" v-model="compraForm.id_proveedor" :options="proveedores" optionLabel="nombre" optionValue="id_proveedor" class="w-full" showClear />
        </div>
        <div class="field col-12">
          <label>Detalle de productos</label>
          <div v-for="(linea, idx) in compraForm.detalle" :key="idx" class="detalle-row">
            <Select v-model="linea.id_producto" :options="productosActivos" filter optionLabel="nombre" optionValue="id_producto" placeholder="Producto" class="w-full" />
            <InputNumber :maxFractionDigits="2" v-model="linea.cantidad" placeholder="Cant." :min="0" class="w-full" />
            <InputNumber :maxFractionDigits="2" v-model="linea.precio_unitario" placeholder="P. unit." mode="currency" currency="PEN" locale="es-PE" :min="0" class="w-full" />
            <Button :disabled="$saving" icon="pi pi-trash" severity="danger" text rounded @click="quitarLinea(idx)" />
          </div>
          <Button :disabled="$saving" label="Agregar línea" icon="pi pi-plus" severity="secondary" text @click="agregarLinea" class="mt-1" />
        </div>
        <div class="field col-12">
          <label for="notas">Notas</label>
          <Textarea id="notas" v-model="compraForm.notas" rows="2" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="compraDialog = false" />
        <Button label="Guardar inversión" :disabled="$saving || (!compraForm.detalle.length)" @click="guardarCompra" />
      </template>
    </Dialog>

    <Dialog v-model:visible="inversionDialog" header="Registrar inversión" :modal="true" :style="{ width: '520px' }">
      <div class="formgrid grid">
        <div class="field col-12">
          <label for="descripcion">Descripción</label>
          <InputText id="descripcion" v-model="inversionForm.descripcion" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="proveedor">Proveedor</label>
          <Select id="proveedor" v-model="inversionForm.id_proveedor" :options="proveedores" optionLabel="nombre" optionValue="id_proveedor" class="w-full" showClear />
        </div>
        <div class="field col-6">
          <label for="monto">Monto</label>
          <InputNumber :maxFractionDigits="2" placeholder="Ej. 100.00" id="monto" v-model="inversionForm.monto" mode="currency" currency="PEN" locale="es-PE" class="w-full" />
        </div>
        <div class="field col-12">
          <label for="notas">Notas</label>
          <Textarea id="notas" v-model="inversionForm.notas" rows="3" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button :disabled="$saving" label="Cancelar" severity="secondary" @click="inversionDialog = false" />
        <Button :disabled="$saving" label="Guardar" @click="guardarInversion" />
      </template>
    </Dialog>

    <Dialog v-model:visible="proveedorDialog" header="Gestionar proveedores" :modal="true" :style="{ width: '640px' }">
      <div class="prov-form-grid">
        <div class="field">
          <label for="prov-nombre">Nombre *</label>
          <InputText id="prov-nombre" v-model="provForm.nombre" placeholder="Nombre del proveedor" class="w-full" />
        </div>
        <div class="field">
          <label for="prov-ruc">RUC</label>
          <InputText id="prov-ruc" v-model="provForm.ruc" placeholder="Opcional" class="w-full" />
        </div>
        <div class="field">
          <label for="prov-tel">Teléfono</label>
          <InputText id="prov-tel" v-model="provForm.telefono" placeholder="Opcional" class="w-full" />
        </div>
        <div class="field">
          <label for="prov-mail">Correo</label>
          <InputText id="prov-mail" v-model="provForm.correo" placeholder="Opcional" class="w-full" />
        </div>
        <Button :disabled="$saving" label="Agregar proveedor" icon="pi pi-plus" @click="guardarProveedor" class="w-full" />
      </div>
      <DataTable :value="proveedores" :rows="8" class="mt-3">
        <Column field="nombre" header="Proveedor"></Column>
        <Column field="ruc" header="RUC">
          <template #body="slotProps">{{ slotProps.data.ruc || '-' }}</template>
        </Column>
        <Column field="telefono" header="Teléfono">
          <template #body="slotProps">{{ slotProps.data.telefono || '-' }}</template>
        </Column>
        <Column field="correo" header="Correo">
          <template #body="slotProps">{{ slotProps.data.correo || '-' }}</template>
        </Column>
      </DataTable>
    </Dialog>

    <Dialog v-model:visible="compraDetalleDialog" header="Detalle de compra" :modal="true" :style="{ width: '560px' }">
      <div v-if="compraSeleccionada.codigo" class="detalle-info">
        <div class="d-row"><span class="d-label">Código</span><span>{{ compraSeleccionada.codigo }}</span></div>
        <div class="d-row"><span class="d-label">Proveedor</span><span>{{ compraSeleccionada.proveedor || '-' }}</span></div>
        <div class="d-row"><span class="d-label">Fecha</span><span>{{ fmtFecha(compraSeleccionada.fecha) }}</span></div>
        <div class="d-row"><span class="d-label">Total</span><span>S/. {{ fmt2(compraSeleccionada.total_compra) }}</span></div>
        <h4 class="sub-det">Productos</h4>
        <div v-for="d in compraSeleccionada.detalle || []" :key="d.id_detalle" class="det-line">
          <span>{{ d.producto }}</span>
          <span>{{ d.cantidad }} × S/. {{ fmt2(d.precio_unitario) }} = S/. {{ fmt2(d.subtotal) }}</span>
        </div>
        <div class="d-row"><span class="d-label">Notas</span><span>{{ compraSeleccionada.notas || '-' }}</span></div>
      </div>
    </Dialog>

    <Dialog v-model:visible="inversionDetalleDialog" header="Detalle de inversión" :modal="true" :style="{ width: '480px' }">
      <div v-if="compraSeleccionada.id_inversion" class="detalle-info">
        <div class="d-row"><span class="d-label">Descripción</span><span>{{ compraSeleccionada.descripcion }}</span></div>
        <div class="d-row"><span class="d-label">Proveedor</span><span>{{ compraSeleccionada.proveedor || '-' }}</span></div>
        <div class="d-row"><span class="d-label">Monto</span><span>S/. {{ fmt2(compraSeleccionada.monto) }}</span></div>
        <div class="d-row"><span class="d-label">Fecha</span><span>{{ fmtFecha(compraSeleccionada.fecha) }}</span></div>
        <div class="d-row"><span class="d-label">Notas</span><span>{{ compraSeleccionada.notas || '-' }}</span></div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { formatFecha as fechaLegible } from '../utils/format'
import { ref, computed, onMounted, watch }  from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'
import { useAuthStore } from '../stores/auth'
import api from '../config/axios'

const route = useRoute()
const auth = useAuthStore()
const esAdmin = computed(() => auth.userRole === 1)
const toast = useToast()
const productos = ref([])
const categorias = ref([])
const compras = ref([])
const inversiones = ref([])
const movimientos = ref([])
const proveedores = ref([])
const resumen = ref({ valor_total: 0, inversiones_mes: 0, articulos_registrados: 0, productos_mes: 0 })
const vistaValida = ['productos', 'compras', 'inversiones', 'movimientos']
const vista = ref(vistaValida.includes(route.query.vista) ? route.query.vista : 'productos')
const busqueda = ref('')
const categoriaFiltro = ref(null)
const mostrarInactivos = ref(false)
const movBusqueda = ref('')
const movTipo = ref(null)
const unidades = [{ label: 'Kg', valor: 'Kg' }, { label: 'Un', valor: 'Un' }, { label: 'Lt', valor: 'Lt' }]
const productoDialog = ref(false)
const stockDialog = ref(false)
const stockModo = ref('entrada')
const compraDialog = ref(false)
const inversionDialog = ref(false)
const proveedorDialog = ref(false)
const compraDetalleDialog = ref(false)
const inversionDetalleDialog = ref(false)
const productoVerDialog = ref(false)
const editing = ref({})
const form = ref({})
const duplicadoInfo = ref(null)
const stockForm = ref({})
const compraForm = ref({})
const inversionForm = ref({})
const provForm = ref({ nombre: '' })
const compraSeleccionada = ref({})
const productoVisto = ref({})
const stockWarning = ref('')

const productosActivos = computed(() => productos.value.filter(p => p.estado))
const stockProducto = computed(() => productosActivos.value.find(p => p.id_producto === stockForm.value.id_producto) || null)

const fmt = (v) => Number(v || 0).toFixed(2)
const fmt2 = (v) => Number(v || 0).toFixed(2)
const fmtFecha = fechaLegible
const fmtFechaHora = fechaLegible
const unidadLabel = (u) => u === 'Kg' ? 'Kg' : u === 'Lt' ? 'Lt' : 'Un'
const fmtStock = (v) => Number(v || 0) % 1 === 0 ? String(Number(v || 0)) : Number(v || 0).toFixed(2)
const firmarCantidad = (v) => {
  const n = Number(v || 0)
  return n > 0 ? `+${fmtStock(n)}` : fmtStock(n)
}

const cargarProductos = async () => {
  const params = {}
  if (busqueda.value) params.q = busqueda.value
  if (categoriaFiltro.value) {
    const cat = categorias.value.find(c => c.id_categoria === categoriaFiltro.value)
    if (cat) params.cat = cat.nombre
  }
  if (!mostrarInactivos.value) params.activos = '1'
  const res = await api.get('/inventario/productos', { params })
  if (res.data.success) productos.value = res.data.data
}

const cargarCategorias = async () => {
  const res = await api.get('/inventario/categorias')
  if (res.data.success) categorias.value = res.data.data
}

const cargarCompras = async () => {
  const res = await api.get('/inventario/compras')
  if (res.data.success) compras.value = res.data.data
}

const cargarInversiones = async () => {
  const res = await api.get('/inventario/inversiones')
  if (res.data.success) inversiones.value = res.data.data
}

const cargarMovimientos = async () => {
  const params = {}
  if (movBusqueda.value) params.producto = movBusqueda.value
  if (movTipo.value) params.tipo = movTipo.value
  const res = await api.get('/inventario/movimientos', { params })
  if (res.data.success) movimientos.value = res.data.data
}

const cargarProveedores = async () => {
  const res = await api.get('/inventario/proveedores')
  if (res.data.success) proveedores.value = res.data.data
}

const cargarResumen = async () => {
  const res = await api.get('/inventario/resumen')
  if (res.data.success) resumen.value = res.data.data
}

const recargarTodo = () => Promise.all([cargarProductos(), cargarMovimientos(), cargarResumen()])

const agregarDialog = () => {
  editing.value = {}
  duplicadoInfo.value = null
  form.value = { nombre: '', unidad_medida: null, estado: true, id_categoria: null, precio: null, stock: null, descripcion: '' }
  productoDialog.value = true
}

const editar = (prod) => {
  editing.value = prod
  duplicadoInfo.value = null
  form.value = { ...prod, unidad_medida: prod.unidad_medida || 'Un', descripcion: prod.descripcion || '' }
  productoDialog.value = true
}

const verProducto = (prod) => {
  productoVisto.value = { ...prod }
  productoVerDialog.value = true
}

const guardarProducto = async () => {
  if (!form.value.unidad_medida) { toast.add({severity:'warn', summary:'Selecciona la unidad de medida.', life:3000}); return }
  try {
    if (editing.value.id_producto) {
      await api.put(`/inventario/productos/${editing.value.id_producto}`, form.value)
    } else {
      await api.post('/inventario/productos', form.value)
    }
    toast.add({ severity: 'success', summary: 'Producto guardado', life: 2500 })
    productoDialog.value = false
    await recargarTodo()
  } catch (e) {
    const d = e.response?.data || {}
    if (d.existe) {
      duplicadoInfo.value = { nombre: form.value.nombre, id_producto: d.id_producto }
      return
    }
    toast.add({ severity: 'error', summary: d.error || d.message || 'Error al guardar', life: 3500 })
  }
}

const irAgregarStock = () => {
  productoDialog.value = false
  abrirAgregarStock({ id_producto: duplicadoInfo.value.id_producto })
}

const toggleEstado = async (prod) => {
  try {
    const msg = prod.estado ? 'desactivar' : 'activar'
    if (prod.estado && !confirm(`¿Desactivar "${prod.nombre}"? Conservará su historial y dejará de estar disponible.`)) return
    if (prod.estado) {
      await api.delete(`/inventario/productos/${prod.id_producto}`)
    } else {
      await api.put(`/inventario/productos/${prod.id_producto}`, { estado: true })
    }
    toast.add({ severity: 'success', summary: `Producto ${msg}`, life: 2500 })
    await recargarTodo()
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'Error al cambiar estado', life: 3500 })
  }
}

const cargarActivos = async () => {
  if (true) {
    const res = await api.get('/inventario/productos', { params: { activos: '1' } })
    if (res.data.success) productos.value = res.data.data
  }
}

const abrirAgregarStock = (prod = null) => {
  stockModo.value = 'entrada'
  stockWarning.value = ''
  stockForm.value = { id_producto: prod?.id_producto || null, cantidad: null, motivo: '' }
  cargarActivos()
  stockDialog.value = true
}

const abrirRegistrarSalida = (prod = null) => {
  stockModo.value = 'salida'
  stockWarning.value = ''
  stockForm.value = { id_producto: prod?.id_producto || null, cantidad: null, motivo: '' }
  cargarActivos()
  stockDialog.value = true
}

const confirmarStock = async () => {
  stockWarning.value = ''
  const prod = stockProducto.value
  if (!stockForm.value.id_producto || !prod) {
    toast.add({ severity: 'warn', summary: 'Selecciona un producto', life: 3000 })
    return
  }
  const cantidad = Number(stockForm.value.cantidad)
  if (!cantidad || cantidad <= 0) {
    toast.add({ severity: 'warn', summary: 'La cantidad debe ser mayor a cero', life: 3000 })
    return
  }
  if (stockModo.value === 'salida') {
    if (!stockForm.value.motivo || !stockForm.value.motivo.trim()) {
      toast.add({ severity: 'warn', summary: 'El motivo de la salida es obligatorio', life: 3000 })
      return
    }
    if (cantidad > Number(prod.stock)) {
      stockWarning.value = `No hay suficiente stock disponible (actual: ${fmtStock(prod.stock)} ${unidadLabel(prod.unidad_medida)}).`
      return
    }
  }
  try {
    const url = `/inventario/productos/${stockForm.value.id_producto}/stock/${stockModo.value}`
    const body = { cantidad }
    if (stockForm.value.motivo) body.motivo = stockForm.value.motivo
    const res = await api.post(url, body)
    toast.add({ severity: 'success', summary: res.data.message || 'Operación registrada', life: 2500 })
    stockDialog.value = false
    await recargarTodo()
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'Error en la operación', life: 3500 })
  }
}

const openCompra = () => {
  cargarActivos()
  compraForm.value = { id_proveedor: null, detalle: [{ id_producto: null, cantidad: null, precio_unitario: null }], notas: '' }
  compraDialog.value = true
}

const agregarLinea = () => {
  compraForm.value.detalle.push({ id_producto: null, cantidad: null, precio_unitario: null })
}

const quitarLinea = (idx) => {
  compraForm.value.detalle.splice(idx, 1)
}

const guardarCompra = async () => {
  try {
    const lineas = compraForm.value.detalle.filter(l => l.id_producto && l.cantidad > 0)
    if (!lineas.length) {
      toast.add({ severity: 'warn', summary: 'Agrega al menos un producto con cantidad', life: 3000 })
      return
    }
    await api.post('/inventario/compras', {
      id_proveedor: compraForm.value.id_proveedor,
      notas: compraForm.value.notas,
      detalle: lineas
    })
    toast.add({ severity: 'success', summary: 'Compra registrada y stock actualizado', life: 2500 })
    compraDialog.value = false
    await Promise.all([cargarCompras(), cargarProductos(), cargarMovimientos(), cargarResumen()])
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'Error al registrar', life: 3500 })
  }
}

const verCompra = async (compra) => {
  try {
    const res = await api.get(`/inventario/compras/${compra.id_compra}`)
    if (res.data.success) {
      compraSeleccionada.value = res.data.data
      compraDetalleDialog.value = true
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error al cargar detalle', life: 3000 })
  }
}

const eliminarCompra = async (compra) => {
  if (!confirm(`¿Anular la compra ${compra.codigo}? Se revertirá el stock.`)) return
  try {
    await api.delete(`/inventario/compras/${compra.id_compra}`)
    toast.add({ severity: 'success', summary: 'Compra anulada y stock revertido', life: 2500 })
    await Promise.all([cargarCompras(), cargarProductos(), cargarMovimientos(), cargarResumen()])
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'Error al anular', life: 3500 })
  }
}

const openInversion = () => {
  inversionForm.value = { descripcion: '', id_proveedor: null, monto: null, notas: '' }
  inversionDialog.value = true
}

const guardarInversion = async () => {
  try {
    await api.post('/inventario/inversiones', inversionForm.value)
    toast.add({ severity: 'success', summary: 'Inversión registrada', life: 2500 })
    inversionDialog.value = false
    await Promise.all([cargarInversiones(), cargarResumen()])
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.message || 'Error al registrar', life: 3500 })
  }
}

const verInversion = (inv) => {
  compraSeleccionada.value = inv
  inversionDetalleDialog.value = true
}

const eliminarInversion = async (inv) => {
  await api.delete(`/inventario/inversiones/${inv.id_inversion}`)
  toast.add({ severity: 'success', summary: 'Inversión eliminada', life: 2500 })
  await Promise.all([cargarInversiones(), cargarResumen()])
}

const openProveedores = () => {
  provForm.value = { nombre: '', ruc: '', telefono: '', correo: '' }
  proveedorDialog.value = true
}

const guardarProveedor = async () => {
  if (!provForm.value.nombre || !provForm.value.nombre.trim()) {
    toast.add({ severity: 'warn', summary: 'El nombre del proveedor es obligatorio', life: 3000 })
    return
  }
  try {
    await api.post('/inventario/proveedores', provForm.value)
    toast.add({ severity: 'success', summary: 'Proveedor agregado', life: 2500 })
    provForm.value = { nombre: '', ruc: '', telefono: '', correo: '' }
    await cargarProveedores()
  } catch (e) {
    toast.add({ severity: 'error', summary: e.response?.data?.error || 'No se pudo guardar el proveedor', life: 3500 })
  }
}

onMounted(async () => {
  await Promise.all([
    cargarProductos(), cargarCategorias(), cargarMovimientos(), cargarResumen(),
    ...(esAdmin.value ? [cargarCompras(), cargarInversiones(), cargarProveedores()] : [])
  ])
  if(route.query.accion === 'entrada') abrirAgregarStock()
  if(route.query.accion === 'nuevo') agregarDialog()
})
watch(() => route.query.vista, v => { if(vistaValida.includes(v)) vista.value=v })
</script>

<style scoped>
.inventario-view { padding: 0; }
.subtitle { color: var(--text-muted); margin-top: 0.25rem; }
.actions { display: flex; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); }
.stat-value { font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem; }
.table-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.search-box { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
.check-activos { display: flex; align-items: center; gap: 0.4rem; white-space: nowrap; }
.check-activos label { margin: 0; font-size: 0.85rem; }
.view-toggle { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.view-toggle .active { background: var(--btn-primary); color: white; border-color: var(--btn-primary); }
.table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; }
.mt-4 { margin-top: 1rem; }
.mt-3 { margin-top: 0.75rem; }
.row-actions { display: flex; gap: 0.15rem; }
.stock-num { font-weight: 600; }
.stock-cero { color: var(--color-danger, #dc2626); }
.estado-badge { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.estado-activo { background: rgba(34, 197, 94, 0.12); color: #16a34a; }
.estado-inactivo { background: rgba(100, 116, 139, 0.15); color: #64748b; }
.mov-tipo { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.mov-entrada { background: rgba(34, 197, 94, 0.12); color: #16a34a; }
.mov-salida { background: rgba(239, 68, 68, 0.12); color: #dc2626; }
.mov-ajuste { background: rgba(245, 158, 11, 0.15); color: #b45309; }
.mov-cant { font-weight: 600; }
.mov-menos { color: #dc2626; }
.opt-prod { display: flex; justify-content: space-between; gap: 1rem; width: 100%; }
.opt-stock { color: var(--text-muted); font-size: 0.85rem; }
.stock-actual { font-size: 1.05rem; font-weight: 700; padding-top: 0.5rem; }
.dup-advice { display: flex; flex-direction: column; gap: 0.75rem; align-items: flex-start; margin-top: 1rem; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.4); padding: 0.9rem; border-radius: 8px; font-size: 0.9rem; }
.dup-advice.warn { background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.4); color: #b91c1c; }
.detalle-info .d-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); }
.detalle-info .d-label { font-weight: 600; color: var(--text-muted); }
.sub-det { margin: 1rem 0 0.5rem; }
.det-line { display: flex; justify-content: space-between; gap: 1rem; padding: 0.35rem 0; font-size: 0.9rem; border-bottom: 1px dashed var(--border-color); }
.mt-1 { margin-top: 0.25rem; }
.detalle-row { display: grid; grid-template-columns: 2fr 1fr 1.5fr auto; gap: 0.5rem; margin-bottom: 0.5rem; align-items: center; }
.prov-form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.prov-form-grid .field { margin: 0; }
</style>