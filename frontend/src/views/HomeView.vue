<script setup>
import { onMounted, onBeforeUnmount } from 'vue'

let chipListeners = []
let onScroll = null

function selectTime(t) {
  const DATA = {
    30:  {r:150, msg:'커피 사러 나온 김에. <b>선정릉</b> 한 바퀴 · 도보 2코스'},
    60:  {r:300, msg:'점심을 먹는 대신에. <b>봉은사 → 코엑스 별마당</b> 투어 · 3코스'},
    120: {r:470, msg:'수업 끝나고 세 시간. <b>서울숲</b>까지 · 4코스'},
    240: {r:640, msg:'🚨WARNING🚨 정말 진짜로 떠나시겠습니까? <b>북촌한옥마을</b>으로? · 5코스'}
  }
  const chips = Array.from(document.querySelectorAll('.chip'))
  const ring = document.getElementById('ring')
  const readout = document.getElementById('readout')
  const routes = {
    30: document.getElementById('r30'),
    60: document.getElementById('r60'),
    120: document.getElementById('r120'),
    240: document.getElementById('r240')
  }
  const stops = Array.from(document.querySelectorAll('.stop'))

  chips.forEach(c => c.setAttribute('aria-selected', c.dataset.t === String(t)))
  if (ring) {
    ring.setAttribute('r', DATA[t].r)
    ring.classList.add('on')
  }
  if (readout) readout.innerHTML = DATA[t].msg

  Object.entries(routes).forEach(([k, el]) => {
    if (!el) return
    el.classList.toggle('on', k === String(t))
  })
  stops.forEach(s => s.classList.toggle('on', Number(s.dataset.t) <= t))
}

onMounted(() => {
  // nav border on scroll
  const nav = document.getElementById('nav')
  onScroll = () => nav && nav.classList.toggle('stuck', window.scrollY > 8)
  window.addEventListener('scroll', onScroll)

  // route dash lengths
  document.querySelectorAll('.route').forEach(p => {
    try { p.style.setProperty('--len', p.getTotalLength()) } catch (e) {}
  })

  // chips interaction
  const chips = Array.from(document.querySelectorAll('.chip'))
  chipListeners = chips.map(c => {
    const fn = () => selectTime(Number(c.dataset.t))
    c.addEventListener('click', fn)
    return { el: c, fn }
  })

  // initial select
  setTimeout(() => selectTime(60), 900)
})

onBeforeUnmount(() => {
  // remove chip listeners
  chipListeners.forEach(({ el, fn }) => el.removeEventListener('click', fn))
  chipListeners = []
  if (onScroll) {
    window.removeEventListener('scroll', onScroll)
    onScroll = null
  }
})
</script>

<template>
  <div class="home">
    <nav id="nav">
      <div class="wrap nav-in">
        <a href="#" class="logo"><span class="dot"></span>LocalHub</a>
        <ul class="nav-links">
          <li><router-link to="/course">코스 만들기</router-link></li>
          <li><a href="#">공유 게시판</a></li>
          <li><a href="#">소개</a></li>
        </ul>
        <span class="nav-spacer" aria-hidden="true"></span>
      </div>
    </nav>

    <header>
      <div class="wrap">
        <div class="eyebrow rv d1">
          <span class="pulse"></span> NOW · <b>SSAFY 역삼캠퍼스</b>
        </div>

        <h1>
          <span class="rv d2" style="display:block">싸피탈출<em>,</em></span>
          <span class="l2 rv d3">당장 현실이 될 수 있습니다.</span>
        </h1>

        <p class="sub rv d4">
          지금 가능한 시간을 선택하세요.<br>
          LocalHub가 가장 어울리는 코스를 지도 위에 그려드립니다.
        </p>

        <div class="cta rv d5">
          <router-link to="/course" class="btn">체험하기 <span class="arrow">→</span></router-link>
          <a href="#" class="btn ghost">공유된 코스 보기</a>
        </div>

        <div class="picker rv d5">
          <span class="picker-label">지금 얼마나 시간있으세요?</span>
          <div class="chips" role="tablist" aria-label="확보 가능한 시간">
            <button class="chip" role="tab" data-t="30"  aria-selected="false">30분</button>
            <button class="chip" role="tab" data-t="60"  aria-selected="true">1시간</button>
            <button class="chip" role="tab" data-t="120" aria-selected="false">2시간</button>
            <button class="chip" role="tab" data-t="240" aria-selected="false">반나절</button>
          </div>
          <p class="readout" id="readout"></p>
        </div>
      </div>

      <div class="stage">
        <div class="plane">
          <svg viewBox="0 0 1280 620" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <defs>
              <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
                <path d="M80 0H0V80" fill="none" stroke="var(--road)" stroke-width="1"/>
              </pattern>
            </defs>

            <rect x="0" y="0" width="1280" height="620" fill="#FBFBFC"/>
            <rect x="0" y="0" width="1280" height="620" fill="url(#grid)" opacity=".55"/>

            <path d="M0 300 H1280" stroke="#fff" stroke-width="26"/>
            <path d="M0 300 H1280" stroke="var(--road)" stroke-width="1"/>
            <path d="M300 0 V620" stroke="#fff" stroke-width="22"/>
            <path d="M300 0 V620" stroke="var(--road)" stroke-width="1"/>
            <path d="M880 0 V620" stroke="#fff" stroke-width="22"/>
            <path d="M880 0 V620" stroke="var(--road)" stroke-width="1"/>

            <g fill="var(--slab)">
              <rect x="60" y="90" width="150" height="120" rx="4"/>
              <rect x="380" y="60" width="180" height="150" rx="4"/>
              <rect x="640" y="120" width="120" height="90" rx="4"/>
              <rect x="960" y="70" width="200" height="130" rx="4"/>
              <rect x="120" y="400" width="110" height="120" rx="4"/>
              <rect x="420" y="380" width="160" height="100" rx="4"/>
              <rect x="700" y="430" width="120" height="110" rx="4"/>
              <rect x="960" y="380" width="180" height="90" rx="4"/>
            </g>

            <g fill="var(--park)">
              <rect x="480" y="220" width="220" height="130" rx="10"/>
              <rect x="1000" y="230" width="190" height="110" rx="10"/>
              <rect x="60" y="240" width="130" height="90" rx="10"/>
            </g>

            <g fill="#C9DEC5">
              <circle cx="520" cy="250" r="9"/><circle cx="556" cy="292" r="12"/>
              <circle cx="620" cy="248" r="10"/><circle cx="668" cy="310" r="13"/>
              <circle cx="596" cy="330" r="9"/>
              <circle cx="1040" cy="262" r="11"/><circle cx="1092" cy="308" r="13"/>
              <circle cx="1150" cy="266" r="9"/>
              <circle cx="96" cy="270" r="10"/><circle cx="150" cy="308" r="12"/>
            </g>

            <g>
              <rect x="196" y="120" width="46" height="46" fill="#EDEEF1"/>
              <rect x="196" y="106" width="46" height="14" fill="#DDDFE4"/>
              <rect x="756" y="446" width="52" height="52" fill="#EDEEF1"/>
              <rect x="756" y="432" width="52" height="14" fill="#DDDFE4"/>
              <rect x="1094" y="106" width="40" height="40" fill="#EDEEF1"/>
              <rect x="1094" y="94" width="40" height="12" fill="#DDDFE4"/>
            </g>

            <circle class="ring" id="ring" cx="190" cy="360" r="150"/>
            <circle class="ring" id="ring2" cx="190" cy="360" r="150" opacity="0"/>

            <path class="route" id="r30"  d="M190 360 L280 330 L330 268"/>
            <path class="route" id="r60"  d="M190 360 L300 336 L360 300 L470 292 L534 274"/>
            <path class="route" id="r120" d="M190 360 L300 340 L400 316 L560 300 L700 262 L806 216"/>
            <path class="route" id="r240" d="M190 360 L300 344 L420 330 L580 306 L740 268 L900 216 L1040 178 L1104 150"/>

            <g>
              <circle cx="190" cy="360" r="26" fill="var(--route)" opacity=".1"/>
              <circle cx="190" cy="360" r="11" fill="#fff" stroke="var(--ink)" stroke-width="5"/>
              <text x="190" y="410" text-anchor="middle" font-family="Pretendard" font-size="14" font-weight="700" fill="#0E1013">SSAFY 역삼캠퍼스</text>
              <text x="190" y="430" text-anchor="middle" font-family="Archivo" font-size="11" letter-spacing="1.5" fill="#9AA1A9">START</text>
            </g>

            <g class="stop" data-t="30">
              <path d="M330 268 l0 -0" />
              <circle cx="330" cy="268" r="7" fill="var(--ink)"/>
              <circle cx="330" cy="268" r="3" fill="#fff"/>
              <text x="330" y="248" text-anchor="middle">선정릉 산책</text>
            </g>
            <g class="stop" data-t="60">
              <circle cx="534" cy="274" r="7" fill="var(--ink)"/>
              <circle cx="534" cy="274" r="3" fill="#fff"/>
              <text x="534" y="254" text-anchor="middle">봉은사 · 별마당</text>
            </g>
            <g class="stop" data-t="120">
              <circle cx="806" cy="216" r="7" fill="var(--ink)"/>
              <circle cx="806" cy="216" r="3" fill="#fff"/>
              <text x="806" y="196" text-anchor="middle">서울숲</text>
            </g>
            <g class="stop" data-t="240">
              <circle cx="1104" cy="150" r="7" fill="var(--ink)"/>
              <circle cx="1104" cy="150" r="3" fill="#fff"/>
              <text x="1104" y="130" text-anchor="middle">북촌한옥마을</text>
            </g>
          </svg>
        </div>
      </div>
    </header>

    <!-- footer removed for this page -->
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,500;0,600;0,800;1,800&display=swap');
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

/* 공통 변수(--ink,--route,--line,--slab,--paper,--ease)는 전역 style.css :root 에 있음.
     여기서는 이 컴포넌트에서만 쓰는 지도 전용 변수만 둔다. */
  .home{
    --park:#E6F0E4;
    --road:#DEE1E5;
    min-height:100vh;
    display:flex;
    flex-direction:column;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{
    background:var(--paper);
    color:var(--ink);
    font-family:'Pretendard','Archivo',-apple-system,sans-serif;
    -webkit-font-smoothing:antialiased;
    overflow-x:hidden;
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
  .btn{
    display:inline-flex;align-items:center;gap:8px;
    height:42px;padding:0 20px;border-radius:999px;border:1px solid var(--route);
    background:var(--route);color:#fff;font-size:14px;font-weight:600;font-family:inherit;
    cursor:pointer;text-decoration:none;
    transition:transform .25s var(--ease),background .25s var(--ease),box-shadow .3s var(--ease);
  }
  .btn:hover{transform:translateY(-2px);background:#2420E8;border-color:#2420E8;box-shadow:0 10px 24px -10px rgba(46,43,255,.45)}
  .btn:active{transform:translateY(0)}
  .btn .arrow{transition:transform .3s var(--ease)}
  .btn:hover .arrow{transform:translateX(3px)}
  .btn.ghost{background:transparent;color:var(--ink);border-color:var(--line)}
  .btn.ghost:hover{border-color:var(--ink);box-shadow:none}
  .btn.sm{height:38px;padding:0 16px;font-size:13px}

  header{padding:150px 0 0;text-align:center;position:relative;flex:1}
  .eyebrow{
    display:inline-flex;align-items:center;gap:8px;
    font-family:'Archivo',sans-serif;font-size:11px;font-weight:600;
    letter-spacing:.16em;text-transform:uppercase;color:var(--ink-60);
    border:1px solid var(--line);border-radius:999px;padding:7px 14px;margin-bottom:26px;
  }
  .eyebrow b{color:var(--ink);font-weight:600}
  .pulse{
    width:6px;height:6px;border-radius:50%;background:var(--route);
    animation:pulse 2s infinite;
  }
  @keyframes pulse{
    0%{box-shadow:0 0 0 0 rgba(46,43,255,.45)}
    70%{box-shadow:0 0 0 7px rgba(46,43,255,0)}
    100%{box-shadow:0 0 0 0 rgba(46,43,255,0)}
  }
  h1{
    font-size:clamp(52px,9.2vw,124px);
    line-height:.92;letter-spacing:-.045em;font-weight:900;
  }
  h1 .l2{
    display:block;font-size:clamp(24px,3.5vw,46px);
    font-weight:700;letter-spacing:-.035em;color:var(--ink);
    margin-top:18px;
  }
  h1 em{
    font-family:'Archivo',sans-serif;font-style:italic;font-weight:800;
    color:var(--route);
  }
  .sub{
    max-width:520px;margin:26px auto 0;
    color:var(--ink-60);font-size:16px;line-height:1.65;
  }
  .cta{display:flex;gap:12px;justify-content:center;margin-top:34px}

  .rv{opacity:0;transform:translateY(22px);animation:rv .9s var(--ease) forwards}
  @keyframes rv{to{opacity:1;transform:none}}
  .d1{animation-delay:.05s}.d2{animation-delay:.16s}.d3{animation-delay:.28s}
  .d4{animation-delay:.4s}.d5{animation-delay:.52s}

  .picker{margin-top:64px;display:flex;flex-direction:column;align-items:center;gap:14px}
  .picker-label{
    font-family:'Archivo',sans-serif;font-size:11px;letter-spacing:.16em;
    text-transform:uppercase;color:var(--ink-30);font-weight:600;
  }
  .chips{
    display:inline-flex;padding:5px;gap:4px;
    border:1px solid var(--line);border-radius:999px;background:#fff;
    box-shadow:0 14px 40px -24px rgba(14,16,19,.35);
  }
  .chip{
    border:0;background:transparent;cursor:pointer;
    font-family:inherit;font-size:14px;font-weight:600;color:var(--ink-60);
    padding:10px 20px;border-radius:999px;
    transition:color .3s var(--ease),background .3s var(--ease);
  }
  .chip:hover{color:var(--route)}
  .chip[aria-selected="true"]{background:var(--route);color:#fff}
  .chip:focus-visible{outline:2px solid var(--route);outline-offset:2px}
  .readout{
    font-size:13px;color:var(--ink-60);min-height:20px;
    transition:opacity .3s var(--ease);
  }
  .readout b{color:var(--ink);font-weight:600}

  .stage{
    margin-top:56px;
    perspective:1600px;
    padding-bottom:40px;
    -webkit-mask-image:linear-gradient(to bottom,#000 62%,transparent 100%);
            mask-image:linear-gradient(to bottom,#000 62%,transparent 100%);
  }
  .plane{
    transform:rotateX(52deg) rotateZ(-16deg) scale(1.12);
    transform-origin:50% 30%;
    animation:tilt 1.3s var(--ease) .5s backwards;
  }
  @keyframes tilt{
    from{opacity:0;transform:rotateX(66deg) rotateZ(-16deg) scale(1.02) translateY(60px)}
  }
  .plane svg{width:100%;height:auto;display:block;overflow:visible}
  .ring{
    fill:none;stroke:var(--route);stroke-width:1.5;stroke-dasharray:6 8;
    opacity:0;transition:opacity .6s var(--ease),r .9s var(--ease);
  }
  .ring.on{opacity:.35}
  .route{
    fill:none;stroke:var(--ink);stroke-width:5;stroke-linecap:round;stroke-linejoin:round;
    stroke-dasharray:var(--len);stroke-dashoffset:var(--len);
    transition:stroke-dashoffset 1.1s var(--ease);
  }
  .route.on{stroke-dashoffset:0}
  .stop{opacity:0;transform-box:fill-box;transform-origin:center bottom;
    transition:opacity .45s var(--ease),transform .45s var(--ease);transform:translateY(6px) scale(.85)}
  .stop.on{opacity:1;transform:none}
  .stop text{font-family:'Pretendard',sans-serif;font-size:13px;font-weight:600;fill:var(--ink)}

  footer{border-top:1px solid var(--line);margin-top:20px;padding:56px 0 40px}
  .foot-top{display:flex;justify-content:space-between;gap:40px;flex-wrap:wrap;padding-bottom:40px}
  .foot-title{font-size:20px;font-weight:700;letter-spacing:-.03em;max-width:320px;line-height:1.4}
  .foot-cols{display:flex;gap:64px}
  .foot-cols h4{font-family:'Archivo',sans-serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-30);margin-bottom:14px;font-weight:600}
  .foot-cols a{display:block;text-decoration:none;color:var(--ink-60);font-size:14px;margin-bottom:9px;transition:color .2s}
  .foot-cols a:hover{color:var(--ink)}
  .foot-bottom{
    border-top:1px solid var(--line);padding-top:24px;
    display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;
    font-size:13px;color:var(--ink-30);
  }
  .foot-bottom .src{color:var(--ink-60)}

  @media(max-width:820px){
    .nav-links{display:none}
    header{padding-top:120px}
    .plane{transform:rotateX(48deg) rotateZ(-12deg) scale(1.5)}
    .chips{flex-wrap:wrap;justify-content:center;border-radius:20px}
    .chip{padding:9px 14px;font-size:13px}
    .cta{flex-direction:column;align-items:center}
    .foot-cols{gap:36px}
  }
  @media(prefers-reduced-motion:reduce){
    *{animation:none!important;transition:none!important}
    .route{stroke-dashoffset:0}
  }
</style>