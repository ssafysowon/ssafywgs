<template>
  <header class="alt-header">
    <div class="alt-inner">
      <router-link to="/" class="logo"><span class="dot"></span>LocalHub</router-link>
      <nav class="alt-nav">
        <router-link to="/course">코스 만들기</router-link>
        <router-link to="/posts">공유 게시판</router-link>
        <router-link to="/about">소개</router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
</script>

<style scoped>
.alt-header{
  height:64px;
  border-bottom:1px solid var(--line);
  background:#fff;
  display:flex;align-items:center;position:sticky;top:0;z-index:1200;
}
.alt-inner{max-width:1220px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:flex-start}
.logo{display:flex;align-items:center;gap:8px;font-family:'Archivo',sans-serif;font-weight:800;letter-spacing:-.03em;font-size:17px;text-decoration:none;color:var(--ink)}
.logo .dot{width:8px;height:8px;border-radius:50%;background:var(--route);box-shadow:0 0 0 4px rgba(3,78,161,.12)}
.alt-nav{display:flex;gap:28px;align-items:center;margin-left:auto}
.alt-nav a{color:var(--ink-60);text-decoration:none;font-weight:700;font-size:13px;position:relative;padding:6px 0}
.alt-nav a::after{content:"";position:absolute;left:0;bottom:-8px;height:1px;width:0;background:var(--ink);transition:width .25s var(--ease)}
.alt-nav a:hover::after{width:100%}
.alt-nav a.router-link-active{color:var(--route)}
</style>
