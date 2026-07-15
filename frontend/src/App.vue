<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

</script>

<template>
  <div id="app">
    <main>
      <router-view />
    </main>

    <footer v-if="route.name !== 'course'" class="site-footer">
      <div class="container footer-inner">
        <div class="source">출처: 한국관광공사 TourAPI 4.0 · 공공누리 제3유형</div>
        <div class="copyright">© 2026 SSAFY TEAM PJT. All rights reserved.</div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Header */
.site-header {
  position: sticky;
  top: 0;
  height: 60px;
  background: var(--paper);
  border-bottom: 1px solid var(--line);
  z-index: 40;
  display: flex;
  align-items: center;
}
.container { max-width: 1200px; margin: 0 auto; width: 100%; padding: 0 24px; display:flex; align-items:center; justify-content:space-between }
.brand a { font-size: 17px; font-weight: 500; color: var(--ink); text-decoration: none }

.nav-right { display:flex; align-items:center; gap:16px }
.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}
.nav-links a { font-size:13px; color: var(--ink); opacity: 0.6; text-decoration: none }
.nav-links .router-link-active { opacity: 1 }
.pill, .badge { font-size:12px; padding:5px 14px; border-radius: var(--radius-card); border: 1px solid var(--line); }
.badge { margin-left: 0; }
.nav-toggle { display: none; }

main { padding: 20px; }

/* Footer */
.site-footer { border-top: 1px solid var(--line); padding: 20px 0; background: transparent }
.footer-inner { display:flex; flex-direction:column; align-items:center; gap:6px }
.footer-inner .source, .footer-inner .copyright { font-size:11px; opacity:0.5 }

/* keep styles minimal; tokens.css handles global body styles */

@media (max-width: 768px) {
  .nav-links { display: none; }
  .nav-toggle { display: block; }
}
</style>
