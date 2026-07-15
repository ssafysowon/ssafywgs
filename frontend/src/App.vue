<script setup>
import '@/styles/tokens.css'
</script>

<template>
  <div id="app">
    <header class="site-header">
      <div class="header-container">
        <router-link to="/" class="brand">
          <span class="brand-dot"></span>
          LocalHub
        </router-link>

        <nav class="nav-links">
          <router-link to="/">홈</router-link>
          <router-link to="/course">코스 만들기</router-link>
          <router-link to="/posts">공유 게시판</router-link>
          <router-link to="/about">소개</router-link>
        </nav>
      </div>
    </header>

    <main class="site-main">
      <router-view />
    </main>

    <footer class="site-footer">
      <div class="footer-container">
        <p>출처: 한국관광공사 TourAPI 4.0 · 공공누리 제3유형</p>
        <p>© 2026 SSAFY TEAM PJT. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  background: #ffffff;
  color: var(--ink, #111827);
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  height: 64px;
  border-bottom: 1px solid #e5e7eb;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
}

.header-container {
  max-width: 1220px;
  height: 100%;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #111827;
  font-size: 17px;
  font-weight: 800;
  text-decoration: none;
}

.brand-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #034ea1;
  box-shadow: 0 0 0 4px rgba(3, 78, 161, 0.1);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav-links a {
  color: #6b7280;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}

.nav-links a.router-link-active {
  color: #034ea1;
}

.site-main {
  min-height: calc(100vh - 140px);
}

.site-footer {
  border-top: 1px solid #e5e7eb;
  background: #fff;
}

.footer-container {
  max-width: 1220px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.footer-container p {
  margin: 0;
  color: #9ca3af;
  font-size: 12px;
}

@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }

  .nav-links {
    gap: 14px;
  }

  .nav-links a {
    font-size: 12px;
  }
}
</style>