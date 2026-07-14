<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const pathRef = ref(null)
const markersVisible = ref([false, false, false, false])
const prefersReduced = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
const mapRef = ref(null)
const parallax = ref({ x: 0, y: 0 })

onMounted(() => {
  const path = pathRef.value
  if (!path) return

  const length = path.getTotalLength()
  path.style.strokeDasharray = length
  if (prefersReduced) {
    path.style.strokeDashoffset = 0
    markersVisible.value = [true, true, true, true]
    return
  }

  path.style.strokeDashoffset = length

  setTimeout(() => {
    path.style.transition = 'stroke-dashoffset 1.5s ease-out'
    path.style.strokeDashoffset = '0'

    const pathDuration = 1500
    const base = pathDuration
    for (let i = 0; i < 4; i++) {
      setTimeout(() => { markersVisible.value[i] = true }, base + i * 150)
    }
  }, 300)
})

function goCourse() {
  router.push('/course')
}

function handleMouseMove(e) {
  const el = mapRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const relX = (e.clientX - rect.left) / rect.width - 0.5
  const relY = (e.clientY - rect.top) / rect.height - 0.5
  parallax.value = { x: -relX * 16, y: -relY * 16 }
}

function handleMouseLeave() {
  parallax.value = { x: 0, y: 0 }
}

onMounted(() => {
  // register parallax listeners only when not reduced-motion
  if (!prefersReduced && mapRef.value) {
    mapRef.value.addEventListener('mousemove', handleMouseMove)
    mapRef.value.addEventListener('mouseleave', handleMouseLeave)
  }
})

onBeforeUnmount(() => {
  if (mapRef.value) {
    mapRef.value.removeEventListener('mousemove', handleMouseMove)
    mapRef.value.removeEventListener('mouseleave', handleMouseLeave)
  }
})
</script>

<template>
  <section class="hero">
    <div class="hero-content">
      <h1>어디로 갈지<br/>물어보기만 하세요</h1>
      <p class="sub">한 문장이면 서울 관광 코스가 완성됩니다.</p>
      <p class="sub">다녀온 후엔 후기와 함께 코스를 공유해 보세요.</p>
      <button class="btn--route" @click="goCourse">체험하기</button>
    </div>

    <div class="map-card card">
      <div class="map-wrapper" ref="mapRef">
        <svg class="map-svg" :style="{ transform: `translate(${parallax.x}px, ${parallax.y}px)` }" viewBox="0 0 560 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <!-- grid lines (2 horizontal, 2 vertical) -->
        <line x1="0" y1="50" x2="560" y2="50" stroke="var(--line)" stroke-width="1" />
        <line x1="0" y1="150" x2="560" y2="150" stroke="var(--line)" stroke-width="1" />
        <line x1="140" y1="0" x2="140" y2="200" stroke="var(--line)" stroke-width="1" />
        <line x1="420" y1="0" x2="420" y2="200" stroke="var(--line)" stroke-width="1" />

        <!-- route path -->
        <path
          ref="pathRef"
          class="route-line"
          d="M40 150 C150 60, 220 40, 320 90 C400 130, 480 60, 520 50"
          stroke-width="3.5"
          stroke-linecap="round"
          fill="none"
        />

        <!-- markers as groups placed exactly on path points -->
        <g class="marker-group" :class="{visible: markersVisible[0]}" transform="translate(40,150)">
          <circle r="15" fill="#2F6F5E" stroke="var(--paper)" stroke-width="3" />
          <text x="0" y="5" text-anchor="middle" font-size="14" fill="#fff">①</text>
        </g>
        <g class="marker-group" :class="{visible: markersVisible[1]}" transform="translate(220,40)">
          <circle r="15" fill="#2F6F5E" stroke="var(--paper)" stroke-width="3" />
          <text x="0" y="5" text-anchor="middle" font-size="14" fill="#fff">②</text>
        </g>
        <g class="marker-group" :class="{visible: markersVisible[2]}" transform="translate(400,130)">
          <circle r="15" fill="#2F6F5E" stroke="var(--paper)" stroke-width="3" />
          <text x="0" y="5" text-anchor="middle" font-size="14" fill="#fff">③</text>
        </g>
        <g class="marker-group" :class="{visible: markersVisible[3]}" transform="translate(520,50)">
          <circle r="15" fill="#2F6F5E" stroke="var(--paper)" stroke-width="3" />
          <text x="0" y="5" text-anchor="middle" font-size="14" fill="#fff">④</text>
        </g>
        </svg>
      </div>

      <aside class="floating-card">
        <div class="caption">오늘의 코스</div>
        <div class="place-row"><span class="marker-icon">①</span><span class="place-name">경복궁</span></div>
        <div class="place-row"><span class="marker-icon">②</span><span class="place-name">북촌한옥마을</span></div>
        <div class="place-row"><span class="marker-icon">③</span><span class="place-name">서울숲</span></div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
/* Hero centered */
.hero { text-align: center; max-width: 640px; margin: 0 auto; padding: 56px 32px 40px }
.hero .btn--route { margin-bottom: 40px }
.hero .hero-content { margin: 0 }
.hero h1 { margin: 0 0 12px 0 }
.sub { margin: 0 0 32px 0; color: var(--muted) }

/* Map card */
.map-card { margin: 0 32px 40px; background: var(--paper-soft); border-radius: var(--radius-card); padding: 32px; display: grid; grid-template-columns: 1fr 200px; gap: 24px; align-items: center }

/* SVG map styling */
.map-wrapper { overflow: hidden }
.map-svg { width: 100%; height: 200px; display: block; transition: transform 0.15s ease-out }
.map-svg .route-line { stroke: var(--route); stroke-width: 3.5; fill: none; stroke-dasharray: 0; stroke-dashoffset: 0 }
.map-svg line { vector-effect: non-scaling-stroke }

/* Marker groups inside SVG */
.marker-group { opacity: 0; transition: opacity 0.35s ease; }
.marker-group.visible { opacity: 1 }

/* Floating card */
.floating-card { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-card); padding: 16px }
.floating-card .caption { font-size: 12px; color: var(--muted); margin-bottom: 8px }
.place-row { display:flex; align-items:flex-start; gap:8px; margin:8px 0 }
.marker-icon { display:inline-flex; width:18px; height:18px; border-radius:50%; background:var(--route); color:#fff; font-size:12px; align-items:center; justify-content:center }
.place-name { font-size:13px }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .map-svg .route-line { transition: none !important }
  .marker-group { transition: none !important; opacity: 1 !important }
}

/* Responsive */
@media (max-width: 768px) {
  .map-card { grid-template-columns: 1fr; padding: 20px }
  .map-svg { height: 160px }
  .hero { padding: 40px 20px }
}
</style>