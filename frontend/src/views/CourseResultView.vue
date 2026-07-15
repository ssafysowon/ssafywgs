<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'

async function postJson(path, payload) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const txt = await res.text().catch(() => res.statusText)
    throw new Error(txt || res.statusText)
  }
  return res.json()
}

function mapServerStopsToLocal(stops) {
  return (stops || []).map(s => ({
    id: s.id,
    name: s.name || s.title || '',
    cat: s.category || s.cat || '',
    desc: s.description || s.desc || '',
    lat: s.lat,
    lng: s.lng,
    stay: s.stay || ''
  }))
}

const router = useRouter()
const courseTitle = ref('역삼 탈출 코스')
const isLoading = ref(false)

// 이전 페이지에서 router.push({ name, state:{ answers } }) 로 넘어온 값
const incoming = (window?.history?.state?.answers) || {}
const answers = reactive({
  time: incoming.time || '1시간',
  field: incoming.field || '강남구',
  companion: incoming.companion || '싸피 친구',
  concept: incoming.concept || '조용한 산책'
})

const START = { name: 'SSAFY 역삼캠퍼스', lat: 37.5009, lng: 127.0369, start: true }
const STOPS = ref([])

let map = null
let markers = []
let layersGroup = null

function initMap () {
  map = L.map('map', { zoomControl: true }).setView([37.5045, 127.042], 15)
  // Stadia Alidade Smooth — 부드러운 고급 회색 톤.
  // 개발(localhost)은 보통 키 없이 동작. 배포 시 stadiamaps.com 에서 무료 키 발급 후
  // URL 뒤에 ?api_key=YOUR_KEY 를 붙이세요.
  L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; Stadia Maps &copy; OpenMapTiles &copy; OpenStreetMap',
    maxZoom: 20
  }).addTo(map)
}

function pinIcon (label, isStart) {
  return L.divIcon({
    className: '', iconSize: [36, 46], iconAnchor: [3, 30], popupAnchor: [0, -42],
    html: `<div class="pin ${isStart ? 'start' : ''}"><div class="head"></div><div class="num">${label}</div></div>`
  })
}

function hoverHtml (p) {
  return `<div class="hovercard"><div class="hc-top">
    <div class="hc-cat">${p.cat}</div><div class="hc-name">${p.name}</div>
    <div class="hc-desc">${p.desc}</div></div>
    <div class="hc-foot">머무름 <b>${p.stay || '-'}</b></div></div>`
}

function drawMap () {
  if (!map) return
  markers.forEach(m => map.removeLayer(m)); markers = []
  if (layersGroup) { map.removeLayer(layersGroup); layersGroup = null }

  const seq = [START, ...STOPS.value]
  const ll = seq.map(p => [p.lat, p.lng])

  layersGroup = L.layerGroup([
    L.polyline(ll, { color: '#fff', weight: 8, opacity: 1, lineJoin: 'round' }),
    L.polyline(ll, { color: '#0E1013', weight: 3.5, opacity: 1, dashArray: '1 9', lineCap: 'round' })
  ]).addTo(map)

  seq.forEach((p, i) => {
    const mk = L.marker([p.lat, p.lng], { icon: pinIcon(p.start ? '★' : String(i), p.start), riseOnHover: true }).addTo(map)
    if (!p.start) {
      mk.bindPopup(hoverHtml(p), { closeButton: false, offset: [0, -6] })
      mk.on('mouseover', () => { mk.openPopup(); flashCard(i - 1, true) })
      mk.on('mouseout', () => { mk.closePopup(); flashCard(i - 1, false) })
    }
    markers.push(mk)
  })

  map.fitBounds(L.latLngBounds(ll).pad(0.28))
}

function flashCard (i, on) {
  const cards = document.querySelectorAll('.card')
  if (cards[i]) cards[i].classList.toggle('flash', on)
}
function pinHover (i, on) {
  const el = markers[i]?.getElement()?.querySelector('.pin')
  if (el) el.classList.toggle('pin-hover', on)
}

// ----- 드래그 재정렬 -----
const dragFrom = ref(null)
function onDrop (to) {
  const from = dragFrom.value
  dragFrom.value = null
  if (from === null || from === to) return
  const arr = [...STOPS.value]
  const [item] = arr.splice(from, 1)
  arr.splice(to, 0, item)
  STOPS.value = arr   // 새 배열 재할당 → 확실히 반응성 트리거
}

// ----- 채팅 / refineCourse -----
const chatOpen = ref(false)
const messages = ref([])
const chatInput = ref('')
const chatLogRef = ref(null)

function scrollChat () {
  nextTick(() => { if (chatLogRef.value) chatLogRef.value.scrollTop = chatLogRef.value.scrollHeight })
}

/**
 * 자연어 요청 → 새 코스.
 * 지금은 로컬 mock. 실제로는 백엔드(OpenAI 경유) 엔드포인트를 호출하세요.
 * 예)
 *   const res = await fetch('/api/course/refine', {
 *     method:'POST', headers:{'Content-Type':'application/json'},
 *     body: JSON.stringify({ stops: STOPS.value, request: text, answers })
 *   })
 *   const data = await res.json()      // { stops:[...], message:'...' }
 *   STOPS.value = data.stops
 *   return data.message
 */
async function refineCourse (text) {
  isLoading.value = true
  try {
    const coursePayload = {
      title: `역삼 ${answers.concept} 코스`,
      totalTime: answers.time,
      start: { name: START.name, lat: START.lat, lng: START.lng },
      stops: STOPS.value.map(s => ({ id: s.id, description: s.desc, stay: s.stay }))
    }

    const res = await postJson('/api/course/modify', { request: text, course: coursePayload })
    console.log('modify res', res)

    if (res.course) {
      STOPS.value = mapServerStopsToLocal(res.course.stops)
      if (res.course.start) {
        START.name = res.course.start.name || START.name
        START.lat = res.course.start.lat || START.lat
        START.lng = res.course.start.lng || START.lng
      }
      if (res.course.title) courseTitle.value = res.course.title
      if (res.course.totalTime) answers.time = res.course.totalTime
    }

    return res.message || '변경을 반영했습니다.'
  } catch (err) {
    console.error('modify 실패', err)
    return '변경 실패: 서버 오류'
  } finally {
    isLoading.value = false
    drawMap()
  }
}

async function sendChat (text) {
  const msg = (text ?? '').trim()
  if (!msg) return
  messages.value.push({ who: 'me', text: msg })
  chatInput.value = ''
  const thinking = { who: 'bot', text: '처리 중…', think: true }
  messages.value.push(thinking)
  scrollChat()

  const res = await refineCourse(msg)
  const idx = messages.value.indexOf(thinking)
  if (idx !== -1) messages.value.splice(idx, 1, { who: 'bot', text: res })
  scrollChat()
}

function submitInput () { sendChat(chatInput.value) }
function quickAsk (q) { chatOpen.value = true; sendChat(q) }

function goShareToPosts() {
  router.push({
    path: '/posts/create',
    state: {
      prefill: {
        title: `역삼에서 ${answers.time} · ${answers.concept} 코스`,
        content: `${answers.time} 동안 ${answers.field}에서 ${answers.companion}와 함께 ${answers.concept} 코스 추천합니다.`,
        time: answers.time,
        district: answers.field,
        companion: answers.companion,
        // 게시글 작성 화면의 지도에 그대로 꽂힐 코스 데이터
        course: {
          title: `역삼에서 ${answers.time} · ${answers.concept} 코스`,
          totalTime: answers.time,
          start: { name: START.name, lat: START.lat, lng: START.lng },
          stops: STOPS.value.map(s => ({
            name: s.name,
            category: s.cat,
            description: s.desc,
            stay: s.stay,
            lat: s.lat,
            lng: s.lng
          }))
        }
      }
    }
  })
}

onMounted(async () => {
  initMap()
  isLoading.value = true

  try {
    const payload = {
      time: answers.time,
      field: answers.field,
      companion: answers.companion,
      concept: answers.concept
    }

    const res = await postJson('/api/course/generate', payload)

    console.log('generate res', res)

    if (res.course) {
      STOPS.value = mapServerStopsToLocal(res.course.stops)

      if (res.course.start) {
        START.name = res.course.start.name || START.name
        START.lat = res.course.start.lat || START.lat
        START.lng = res.course.start.lng || START.lng
      }

      if (res.course.title) courseTitle.value = res.course.title
      if (res.course.totalTime) answers.time = res.course.totalTime
    }

    messages.value.push({
      who: 'bot',
      text: '코스를 짜뒀어요. 바꾸고 싶은 부분을 편하게 말해주세요 🙂'
    })

  } catch (err) {
    console.error('generate 실패', err)
    messages.value.push({
      who: 'bot',
      text: '코스 생성에 실패했습니다.'
    })
  } finally {
    isLoading.value = false
    drawMap()
    nextTick(() => map && map.invalidateSize())
  }
})

onBeforeUnmount(() => { if (map) { map.remove(); map = null } })

watch(STOPS, () => drawMap())  // 코스 바뀌면 지도 다시 그림
</script>

<template>
  <div class="page">
    <nav>
      <a class="logo" href="#" @click.prevent="router.push({ name: 'Home' })"><span class="dot"></span>LocalHub</a>
      <ul class="nav-links">
        <li><router-link to="/course">코스 만들기</router-link></li>
        <li><router-link to="/posts">공유 게시판</router-link></li>
        <li><router-link to="/about">소개</router-link></li>
      </ul>
        <div class="nav-tags">
        <span class="tag"><span class="k">Time</span><span class="v">{{ answers.time }}</span></span>
        <span class="tag"><span class="k">Area</span><span class="v">{{ answers.field }}</span></span>
        <span class="tag"><span class="k">With</span><span class="v">{{ answers.companion }}</span></span>
        <span class="tag"><span class="k">Mood</span><span class="v">{{ answers.concept }}</span></span>
      </div>
        <div class="nav-actions">
        <button class="nbtn" @click="router.push({ name: 'course' })">↺ 다시 만들기</button>
        <button
          class="nbtn primary"
          @click="goShareToPosts"
        >게시판에 공유 →</button>
      </div>
    </nav>

    <div class="shell">
      <!-- 1: AI CHAT (fixed column) -->
      <div class="chat-column">
        <div class="chat-panel open">
          <div class="chat-top">
            <div class="t"><span class="live"></span>코스 다듬기</div>
          </div>
          <div class="chat-log" ref="chatLogRef">
            <div v-for="(m, idx) in messages" :key="idx" :class="['cmsg', m.who, { think: m.think }]">
              <template v-if="m.think"><i></i><i></i><i></i></template>
              <template v-else>{{ m.text }}</template>
            </div>
          </div>
          <div class="quick">
            <button @click="quickAsk('근처 카페도 넣어줘')">☕ 카페 추가</button>
            <button @click="quickAsk('더 조용한 곳으로 바꿔줘')">🌿 더 조용하게</button>
            <button @click="quickAsk('시간을 30분으로 줄여줘')">⚡ 30분으로</button>
          </div>
          <div class="chat-input">
            <textarea
              v-model="chatInput" rows="1" placeholder="바꾸고 싶은 걸 말해보세요"
              @keydown.enter.exact.prevent="submitInput"
            ></textarea>
            <button class="send" :disabled="!chatInput.trim()" @click="submitInput">↑</button>
          </div>
        </div>
      </div>

      <!-- 2: 코스 -->
      <aside class="panel">
        <div class="panel-head">
          <div class="kicker">Your Course</div>
          <h1>역삼 탈출 코스</h1>
          <p>SSAFY 역삼캠퍼스에서 출발하는 {{ answers.concept }} 코스예요.</p>
          <div class="meta"><span>총 <b>약 {{ answers.time }}</b></span><span>장소 <b>{{ STOPS.length }}곳</b></span></div>
        </div>
        <div class="cards">
          <div v-if="isLoading" class="loader">코스를 생성 중입니다…</div>

          <div v-else>
            <div v-if="STOPS.length === 0" class="empty">코스가 아직 없습니다.</div>

            <div v-else>
              <div
                v-for="(p, i) in STOPS" :key="p.name + i"
                class="card" draggable="true"
                @dragstart="dragFrom = i"
                @dragover.prevent
                @drop.prevent="onDrop(i)"
                @mouseenter="() => { const mk = markers[i+1]; if (mk){ mk.openPopup(); pinHover(i+1, true) } }"
                @mouseleave="() => { const mk = markers[i+1]; if (mk){ mk.closePopup(); pinHover(i+1, false) } }"
              >
                <div class="idx">{{ i + 1 }}</div>
                <div class="body">
                  <div class="name-row"><span class="name">{{ p.name }}</span><span class="cat">{{ p.cat }}</span></div>
                  <div class="desc">{{ p.desc }}</div>
                  <div class="stay">머무름 <b>{{ p.stay }}</b></div>
                </div>
                <div class="grip">⠿</div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 3: 지도 -->
      <div class="map-wrap">
        <div id="map"></div>
      </div>
    </div>
  </div>
</template>

<!-- 전역: Leaflet이 동적 생성하는 DOM(핀/팝업/컨트롤)은 scoped로 안 먹으므로 전역 처리 -->
<style>
.pin{position:relative;width:36px;height:46px;display:flex;justify-content:center;filter:drop-shadow(0 8px 10px rgba(14,16,19,.22))}
/* 지면에 닿는 작은 그림자 점 — 핀이 떠 있는 느낌을 줌 */
.pin::after{content:"";position:absolute;bottom:1px;left:50%;transform:translateX(-50%);
  width:10px;height:4px;border-radius:50%;background:rgba(14,16,19,.25);filter:blur(1px)}
.pin .head{width:32px;height:32px;border-radius:50% 50% 50% 4px;position:relative;
  background:var(--ink);border:2.5px solid #fff;
  transition:background .25s cubic-bezier(.22,.7,.2,1),transform .2s cubic-bezier(.22,.7,.2,1)}
/* triangular pointer removed */
.pin .num{position:absolute;top:5px;left:0;right:0;text-align:center;color:#fff;
  font-family:'Archivo',sans-serif;font-weight:700;font-size:14px;line-height:20px;pointer-events:none}
.pin.start .head{background:var(--route)}
.pin:hover .head{transform:rotate(45deg) scale(1.1)}
.pin-hover .head{background:var(--route)!important}

.hovercard{background:#fff;border-radius:14px;border:1px solid var(--line);
  box-shadow:0 18px 40px -18px rgba(14,16,19,.45);min-width:210px;overflow:hidden}
.hovercard .hc-top{padding:13px 15px}
.hovercard .hc-cat{font-size:10.5px;font-weight:700;letter-spacing:.06em;color:var(--route);text-transform:uppercase}
.hovercard .hc-name{font-size:15px;font-weight:700;margin-top:3px;letter-spacing:-.01em}
.hovercard .hc-desc{font-size:12.5px;color:var(--ink-60);margin-top:5px;line-height:1.5}
.hovercard .hc-foot{border-top:1px solid var(--line);padding:9px 15px;font-size:11.5px;color:var(--ink-30)}
.hovercard .hc-foot b{color:var(--ink);font-weight:600}

.leaflet-tile-pane{filter:contrast(1.02) brightness(1.01)}
.leaflet-container{font-family:'Pretendard',sans-serif;background:#eef0f2}
.leaflet-popup-content-wrapper{background:transparent;box-shadow:none;padding:0;border-radius:14px}
.leaflet-popup-content{margin:0;width:auto!important}
.leaflet-popup-tip{background:#fff;border:1px solid var(--line)}
.leaflet-popup-close-button{display:none}
.leaflet-control-zoom{border:none!important;box-shadow:0 6px 20px -10px rgba(14,16,19,.3)!important;margin:16px!important}
.leaflet-control-zoom a{border-radius:10px!important;color:var(--ink)!important;
  border:1px solid var(--line)!important;background:#fff!important;width:34px!important;height:34px!important;
  line-height:32px!important;font-size:18px!important}
.leaflet-control-attribution{font-size:10px!important;background:rgba(255,255,255,.7)!important}
</style>

<style scoped>
/* CSS 변수(--route 등)는 전역 style.css의 :root 에 정의됨. 여기서 재정의하지 않는다. */
.page{height:100vh;overflow:hidden;
  font-family:'Pretendard','Archivo',sans-serif;color:var(--ink);background:var(--paper);
  -webkit-font-smoothing:antialiased}

/* NAV */
nav{height:64px;border-bottom:1px solid var(--line);display:flex;align-items:center;
  justify-content:space-between;padding:0 24px;position:relative;z-index:1200;background:#fff}
.logo{display:flex;align-items:center;gap:9px;font-family:'Archivo',sans-serif;font-weight:800;
  letter-spacing:-.03em;font-size:18px;text-decoration:none;color:var(--ink)}
.logo .dot{width:9px;height:9px;border-radius:50%;background:var(--route);box-shadow:0 0 0 4px rgba(3,78,161,.12)}
.nav-links{display:flex;gap:30px;list-style:none;margin-left:18px}
.nav-links a{color:var(--ink-60);text-decoration:none;font-size:14px;font-weight:500;position:relative;padding:4px 0}
.nav-links a::after{content:"";position:absolute;left:0;bottom:0;height:1px;width:0;background:var(--ink);transition:width .3s var(--ease)}
.nav-links a:hover::after{width:100%}
.nav-tags{display:flex;align-items:center;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff}
.nav-tags .tag{display:flex;flex-direction:column;gap:1px;padding:7px 16px;position:relative}
.nav-tags .tag + .tag::before{content:"";position:absolute;left:0;top:20%;bottom:20%;width:1px;background:var(--line)}
.nav-tags .tag .k{font-family:'Archivo',sans-serif;font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-30);font-weight:600}
.nav-tags .tag .v{font-size:13px;font-weight:600;color:var(--ink);letter-spacing:-.01em}
.nav-actions{display:flex;gap:9px}
.nbtn{height:38px;padding:0 15px;border-radius:10px;border:1px solid var(--line-strong);background:#fff;
  font-family:inherit;font-size:13.5px;font-weight:600;color:var(--ink);cursor:pointer;
  display:inline-flex;align-items:center;gap:6px;transition:all .2s var(--ease)}
.nbtn:hover{border-color:var(--ink)}
.nbtn.primary{background:var(--ink);color:#fff;border-color:var(--ink)}
.nbtn.primary:hover{background:var(--route);border-color:var(--route)}

/* LAYOUT */
.shell{display:grid;grid-template-columns:420px 392px 1fr;height:calc(100vh - 64px)}

.chat-column{padding:18px 12px;display:flex;flex-direction:column;gap:12px}
.chat-column .chat-panel{height:calc(100vh - 64px - 36px);display:flex;flex-direction:column}
.chat-panel .chat-log{flex:1;overflow:auto;max-height:none;padding:12px 16px}

/* LEFT */
.panel{border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0;background:#fff}
.panel-head{padding:24px 24px 16px}
.panel-head .kicker{font-family:'Archivo',sans-serif;font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--route);font-weight:600;margin-bottom:8px}
.panel-head h1{font-size:22px;font-weight:700;letter-spacing:-.025em}
.panel-head p{font-size:13.5px;color:var(--ink-60);margin-top:6px;line-height:1.5}
.panel-head .meta{font-size:12.5px;color:var(--ink-30);margin-top:14px;display:flex;gap:14px}
.panel-head .meta b{color:var(--ink);font-weight:600}

.cards{flex:1;overflow-y:auto;padding:4px 18px 24px;min-height:0}
.cards::-webkit-scrollbar{width:7px}
.cards::-webkit-scrollbar-thumb{background:var(--line-strong);border-radius:8px}

.card{position:relative;display:flex;gap:15px;padding:16px 16px 16px 14px;border-radius:16px;
  border:1px solid var(--line);background:#fff;margin-bottom:11px;cursor:grab;
  transition:border-color .2s var(--ease),box-shadow .25s var(--ease),transform .1s var(--ease)}
.card:hover{border-color:var(--line-strong);box-shadow:0 14px 30px -20px rgba(14,16,19,.45)}
.card.flash{border-color:var(--route);box-shadow:0 0 0 3px var(--route-soft)}
.card::before{content:"";position:absolute;left:27px;top:-11px;height:11px;width:1.5px;background:var(--line-strong)}
.card:first-child::before{display:none}
.card .idx{flex:none;width:28px;height:28px;border-radius:50%;border:1.5px solid var(--route);
  color:var(--route);background:#fff;font-family:'Archivo',sans-serif;font-weight:700;font-size:13px;
  display:flex;align-items:center;justify-content:center;margin-top:1px;transition:all .2s var(--ease)}
.card:hover .idx{background:var(--route);color:#fff}
.card .body{flex:1;min-width:0}
.card .name-row{display:flex;align-items:baseline;gap:9px}
.card .name{font-size:16px;font-weight:700;letter-spacing:-.02em}
.card .cat{font-size:11px;font-weight:600;color:var(--ink-30);letter-spacing:.02em}
.card .desc{font-size:13px;color:var(--ink-60);margin-top:6px;line-height:1.55}
.card .stay{font-size:12px;color:var(--ink-30);margin-top:10px}
.card .stay b{color:var(--ink-60);font-weight:600}
.card .grip{position:absolute;top:16px;right:13px;color:var(--line-strong);font-size:15px;line-height:1;user-select:none;transition:color .2s}
.card:hover .grip{color:var(--ink-30)}

/* RIGHT */
.map-wrap{position:relative}
#map{width:100%;height:100%;background:#eef0f2}

.chat-panel{position:relative;right:auto;bottom:auto;z-index:1000;width:100%;max-width:none;
  background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 6px 18px -8px rgba(14,16,19,0.06);
  display:flex;flex-direction:column;overflow:hidden;transform:none;opacity:1;pointer-events:auto;padding:0}
.chat-panel .chat-top{padding:14px 16px}
.chat-top{display:flex;align-items:center;justify-content:space-between;padding:15px 18px;border-bottom:1px solid var(--line)}
.chat-top .t{font-size:14.5px;font-weight:700;display:flex;align-items:center;gap:8px}
.chat-top .t .live{width:7px;height:7px;border-radius:50%;background:var(--route);box-shadow:0 0 0 3px var(--route-soft)}
.chat-top .x{border:0;background:transparent;cursor:pointer;color:var(--ink-30);font-size:20px;line-height:1;padding:2px 4px;border-radius:8px;transition:all .2s}
.chat-top .x:hover{color:var(--ink);background:var(--slab)}

.chat-log{padding:16px 16px 6px;overflow-y:auto;max-height:320px;min-height:180px;display:flex;flex-direction:column;gap:10px}
.chat-log::-webkit-scrollbar{width:6px}
.chat-log::-webkit-scrollbar-thumb{background:var(--line-strong);border-radius:8px}
.cmsg{font-size:14px;line-height:1.55;padding:11px 14px;max-width:86%;animation:pop .35s var(--ease) backwards}
@keyframes pop{from{opacity:0;transform:translateY(8px)}}
.cmsg.me{align-self:flex-end;background:var(--ink);color:#fff;border-radius:16px 16px 5px 16px}
.cmsg.bot{align-self:flex-start;background:var(--slab);color:var(--ink);border-radius:16px 16px 16px 5px}
.cmsg.bot.think{display:inline-flex;gap:4px;align-items:center}
.cmsg.bot.think i{width:5px;height:5px;border-radius:50%;background:var(--ink-30);animation:blink 1.2s infinite}
.cmsg.bot.think i:nth-child(2){animation-delay:.18s}
.cmsg.bot.think i:nth-child(3){animation-delay:.36s}
@keyframes blink{0%,60%,100%{opacity:.25;transform:translateY(0)}30%{opacity:1;transform:translateY(-3px)}}

.quick{display:flex;flex-wrap:wrap;gap:7px;padding:6px 16px 12px}
.quick button{border:1px solid var(--line-strong);background:#fff;border-radius:999px;padding:7px 13px;
  font-family:inherit;font-size:12.5px;font-weight:600;color:var(--ink-60);cursor:pointer;transition:all .18s var(--ease)}
.quick button:hover{border-color:var(--route);color:var(--route);transform:translateY(-1px)}

.chat-input{display:flex;gap:8px;align-items:flex-end;margin:0 16px 16px;border:1px solid var(--line-strong);
  border-radius:14px;padding:6px 6px 6px 15px;transition:border-color .2s,box-shadow .2s}
.chat-input:focus-within{border-color:var(--route);box-shadow:0 0 0 4px var(--route-soft)}
.chat-input textarea{flex:1;border:0;outline:0;resize:none;font-family:inherit;font-size:14px;line-height:1.5;padding:6px 0;max-height:90px;background:transparent}
.chat-input textarea::placeholder{color:var(--ink-30)}
.chat-input .send{flex:none;width:38px;height:38px;border-radius:10px;border:0;cursor:pointer;background:var(--ink);color:#fff;font-size:16px;transition:background .2s,transform .2s}
.chat-input .send:hover:not(:disabled){background:var(--route);transform:translateY(-1px)}
.chat-input .send:disabled{background:var(--line-strong);cursor:not-allowed}

@media(max-width:900px){
  .page{height:auto;overflow:auto}
  .shell{grid-template-columns:1fr;height:auto}
  .map-wrap{height:64vh}
  .panel{border-right:0;border-bottom:1px solid var(--line)}
  .nav-tags{display:none}
  .chat-panel{width:calc(100% - 32px);right:16px;bottom:16px}
}

.loader { padding: 32px; text-align: center; font-weight: 700; color: var(--ink-60); }
.empty  { padding: 24px; text-align: center; color: var(--ink-40); }
</style>