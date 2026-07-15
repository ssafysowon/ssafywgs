<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

</script>

<template>
  <div id="app">
    <nav v-if="route.name !== 'course' && route.name !== 'course-result' && route.name !== 'Home'" id="nav">
      <div class="wrap nav-in">
        <router-link to="/" class="logo"><span class="dot"></span>LocalHub</router-link>
        <ul class="nav-links">
          <li><router-link to="/course">코스 만들기</router-link></li>
          <li><router-link to="/posts">공유 게시판</router-link></li>
          <li><router-link to="/about">소개</router-link></li>
        </ul>
        <span class="nav-spacer" aria-hidden="true"></span>
      </div>
    </nav>

    <main class="site-main">
      <router-view />
    </main>

    <footer v-if="route.name !== 'course' && route.name !== 'course-result' && route.name !== 'Home'" class="site-footer">
      <div class="wrap">
        <div class="foot-top">
          <p class="foot-title">오늘 남은 시간.<br>충분히 떠날 수 있습니다.</p>
          <div class="foot-cols">
            <div>
              <h4>Service</h4>
              <a href="#">코스 만들기</a>
              <a href="#">공유 게시판</a>
              <a href="#">이번 주 인기</a>
            </div>
            <div>
              <h4>Team</h4>
              <a href="#">프로젝트 소개</a>
              <a href="#">깃허브</a>
              <a href="#">문의하기</a>
            </div>
          </div>
        </div>
        <div class="foot-bottom">
          <span class="src">출처: 한국관광공사 TourAPI 4.0 · 공공누리 제3유형</span>
          <span>© 2026 SSAFY TEAM PJT. All rights reserved.</span>
        </div>
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

.wrap{max-width:1240px;margin:0 auto;padding:0 32px}

nav{
  position:fixed;top:0;left:0;right:0;z-index:50;
  background:rgba(255,255,255,.72);
  backdrop-filter:saturate(1.4) blur(14px);
  border-bottom:1px solid transparent;
  transition:border-color .4s var(--ease);
}
nav.stuck{border-bottom-color:var(--line)}
.nav-in{display:flex;align-items:center;justify-content:space-between;height:68px}
.logo{
  display:flex;align-items:center;gap:9px;
  font-family:'Archivo',sans-serif;font-weight:800;letter-spacing:-.03em;font-size:19px;
  text-decoration:none;color:var(--ink);
}
.logo .dot{
  width:9px;height:9px;border-radius:50%;background:var(--route);
  box-shadow:0 0 0 4px rgba(46,43,255,.14);
}
.nav-links{display:flex;gap:30px;list-style:none}
.nav-spacer{width:110px}
.nav-links a{
  text-decoration:none;color:var(--ink-60);font-size:14px;font-weight:500;
  position:relative;padding:4px 0;transition:color .25s var(--ease);
}
.nav-links a::after{
  content:"";position:absolute;left:0;bottom:0;height:1px;width:0;background:var(--ink);
  transition:width .3s var(--ease);
}
.nav-links a:hover{color:var(--ink)}
.nav-links a:hover::after{width:100%}
.nav-links .router-link-active{color:var(--route)}

.site-main {
  min-height: calc(100vh - 140px);
  padding-top: 68px; /* offset fixed nav height so content aligns under header */
}

.site-footer {
  border-top: 1px solid #e5e7eb;
  background: #fff;
}

/* Footer layout (match Home view) */
.foot-top{display:flex;justify-content:space-between;gap:40px;flex-wrap:wrap;padding-bottom:40px}
.foot-title{font-size:20px;font-weight:700;letter-spacing:-.03em;max-width:320px;line-height:1.4}
.foot-cols{display:flex;gap:64px}
.foot-cols h4{font-family:'Archivo',sans-serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-30);margin-bottom:14px;font-weight:600}
.foot-cols a{display:block;text-decoration:none;color:var(--ink-60);font-size:14px;margin-bottom:9px;transition:color .2s}
.foot-cols a:hover{color:var(--ink)}
.foot-bottom{border-top:1px solid var(--line);padding-top:24px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:13px;color:var(--ink-30)}
.foot-bottom .src{color:var(--ink-60)}

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