<template>
  <div class="home">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-bg">
        <img :src="heroImg" alt="Fusion peruano-asiatica" fetchpriority="high" />
      </div>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="hero-badge">
          <i class="fa-solid fa-star"></i> Desde 2025
        </div>
        <img :src="logoSrc" alt="Bendito Buffet" class="hero-logo" />
        <h1>Bendito Buffet</h1>
        <p class="hero-sub">
          Donde el mar peruano encuentra la selva, el criollo abraza al asiatico
          y cada plato cuenta una historia de fusion sin limites.
        </p>
        <div class="hero-cta-group">
          <router-link to="/login" class="hero-cta">
            Acceso Empleados
            <i class="fa-solid fa-arrow-right"></i>
          </router-link>
        </div>
      </div>
      <a href="#about" class="hero-scroll">
        Descubrir
        <div class="scroll-line"></div>
      </a>
    </section>

    <!-- ABOUT -->
    <section class="section section-dark" id="about">
      <div class="section-inner">
        <div class="about-grid">
          <div class="about-media fade-in">
            <img :src="comidaCriollaImg" alt="Cocina criolla peruana" loading="lazy" />
            <div class="about-tag">
              <i class="fa-solid fa-utensils"></i> Fusion sin fronteras
            </div>
          </div>
          <div class="about-text">
            <span class="section-label">Nuestra Historia</span>
            <h3>Cuatro mundos en un solo bocado</h3>
            <p>
              Bendito Buffet nace de la conviccion de que la mejor cocina
              no conoce limites. Fusionamos la riqueza del mar peruano con
              tecnicas asiaticas milenarias, el alma de la cocina criolla
              y los ingredientes indomitos de la selva.
            </p>
            <p>
              Cada plato es un viaje: desde un chaufa crocante con toques
              de aji amarillo hasta un anticucho glaseado con miso, pasando
              por la frescura de un ceviche nikkei y la potencia de un
              juane con infusion de sacha culantro.
            </p>
            <div class="about-flavors">
              <div class="flavor-card">
                <span class="icon"><i class="fa-solid fa-fish"></i></span>
                <h4>Mar</h4>
                <p>Cebiches, tiraditos & mas</p>
              </div>
              <div class="flavor-card">
                <span class="icon"><i class="fa-solid fa-bowl-rice"></i></span>
                <h4>Asia</h4>
                <p>Nikkei, chifa & fusion</p>
              </div>
              <div class="flavor-card">
                <span class="icon"><i class="fa-solid fa-leaf"></i></span>
                <h4>Selva</h4>
                <p>Ingredientes amazonicos</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CUISINE -->
    <section class="section section-teal">
      <div class="section-inner">
        <span class="section-label">Nuestra Cocina</span>
        <h2>Cuatro <span>tradiciones</span>, un solo destino</h2>
        <p>Cada plato es una exploracion de sabores que cruzan oceanos y cordilleras.</p>
        <div class="cuisine-grid">
          <div class="cuisine-card fade-in fade-in-delay-1">
            <div class="cuisine-card-tag">Mar &amp; Tradicion</div>
            <img :src="comidaCriollaImg" alt="Cocina criolla" loading="lazy" />
            <div class="cuisine-card-overlay">
              <h3>Cocina Criolla</h3>
              <p>La esencia del Peru en cada bocado</p>
            </div>
          </div>
          <div class="cuisine-card fade-in fade-in-delay-2">
            <div class="cuisine-card-tag">Fusion Oriental</div>
            <img :src="heroImg" alt="Arroz chaufa fusion" loading="lazy" />
            <div class="cuisine-card-overlay">
              <h3>Peruano-Asiatica</h3>
              <p>Chifa, nikkei y la mejor fusion del Pacifico</p>
            </div>
          </div>
          <div class="cuisine-card fade-in fade-in-delay-3">
            <div class="cuisine-card-tag">Amazonia Viva</div>
            <img :src="selvaticoImg" alt="Cocina selvatica" loading="lazy" />
            <div class="cuisine-card-overlay">
              <h3>Cocina Selvatica</h3>
              <p>Ingredientes amazonicos que sorprenden</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- STATS -->
    <section class="section section-dark">
      <div class="section-inner">
        <span class="section-label">Trayectoria</span>
        <h2>Hechos que <span>nos respaldan</span></h2>
        <p>Mas que un buffet, somos una experiencia que crece cada dia.</p>
        <div class="stats-grid">
          <div class="stat-item fade-in fade-in-delay-1">
            <div class="stat-number">7+</div>
            <div class="stat-label">Anos de experiencia</div>
          </div>
          <div class="stat-item fade-in fade-in-delay-2">
            <div class="stat-number">150+</div>
            <div class="stat-label">Platos en carta</div>
          </div>
          <div class="stat-item fade-in fade-in-delay-3">
            <div class="stat-number">50+</div>
            <div class="stat-label">Colaboradores</div>
          </div>
          <div class="stat-item fade-in fade-in-delay-4">
            <div class="stat-number">15k+</div>
            <div class="stat-label">Clientes al mes</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="section section-teal">
      <div class="section-inner cta-banner">
        <h2>Formas parte del <span>equipo</span>?</h2>
        <p>Accede al sistema de gestion para administrar pedidos, inventario y mas.</p>
        <router-link to="/login" class="hero-cta">
          <i class="fa-solid fa-lock-open"></i>
          Ingresar al Sistema
          <i class="fa-solid fa-arrow-right"></i>
        </router-link>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
      <div class="footer-inner">
        <img :src="logoSrc" alt="Bendito Buffet" class="footer-logo" loading="lazy" />
        <p>&copy; 2025-2026 Bendito Buffet. Todos los derechos reservados.</p>
        <p>Sistema de Gestion Integral - <router-link to="/login">Acceso Empleados</router-link></p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import logoSrc from '../assets/logo.png'
import heroImg from '../assets/cocina-criolla-peruana-arroz-chaufa.jpg'
import comidaCriollaImg from '../assets/comida-criolla.jpg'
import selvaticoImg from '../assets/selvatico.jpg'

onMounted(() => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
      }
    })
  }, { threshold: 0.15 })

  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el))
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
@import '../assets/index.css';

.home {
  background: #0a0a0a;
}
</style>
