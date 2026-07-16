<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ── 만든 사람들: 실제 팀원 정보로 바꿔 넣으세요 ───────────────
const MAKERS = [
  { name: '정슬기', role: 'DRAGON🐲' },
  { name: '박규은', role: 'HORSE🐴' },
  { name: '소원', role: 'SNAKE🐍' },
]

// 코스 만들기 흐름(실제 4문항 + 결과) — 순서가 정보이므로 번호를 붙임
const STEPS = [
  { n: '01', t: '네 가지 질문에 답하기', d: '남은 시간, 어느 구, 누구와, 어떤 무드. 칩을 누르거나 직접 적어도 돼요.' },
  { n: '02', t: 'AI가 동선을 짜기', d: '역삼에서 갈 수 있는 장소들을 골라, 당신의 한계를 시험합니다.' },
  { n: '03', t: '지도에서 확인하고 다듬기', d: '못하겠다면 수정하세요. AI에게 요구사항을 말하면 바로 반영돼요.' },
  { n: '04', t: '게시판에 공유하기', d: '다른 사람에게 이 멋진 탈출계획을 공유하세요!' },
]

const VALUES = [
  { ico: '🧭', t: '무조건 이 근처로', sub: '  아닐수도...', d: '유명 관광지 목록이 아니라, 출발지에서 갈 수 있는 거리의 장소만 담아요.' },
  { ico: '✨', t: 'AI가 골라주니 편하네!', d: '시간·동행·무드에 맞춰 들를 곳과 동선을 대신 정해드려요. 고민은 저희가.' },
  { ico: '🔁', t: '내가 먼저 갔다올게~', d: '내가 만든 코스를 공유하고, 다른 사람의 계획을 내가 먼저 실행해요!' },
]

let io = null
onMounted(() => {
  const els = document.querySelectorAll('.reveal')
  if (!('IntersectionObserver' in window)) {
    els.forEach(el => el.classList.add('in'))
    return
  }
  io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target) } })
  }, { threshold: 0.16 })
  els.forEach(el => io.observe(el))
})
onBeforeUnmount(() => { if (io) io.disconnect() })
</script>

<template>
  <div class="page">
    <main>
      <!-- HERO -->
      <header class="hero">
        <div class="wrap">
          <div class="eyebrow reveal">About · LocalHub</div>
          <h1 class="reveal">설마 혹시...<br><span class="accent">진짜로</span> 빠지실 거 아니죠?😮</h1>
          <p class="lede reveal">
            <b>싸피에서 탈출할 수 있는 유일한 방법은 취업입니다</b>😉😉
          </p>
          <div class="hero-cta reveal">
            <button class="btn-solid" @click="router.push({ name: 'course' })">그럼에도 불구하고 탈출계획세우기 <span class="arrow">→</span></button>
            <button class="btn-ghost" @click="router.push({ name: 'Posts' })">다른 사람들의 탈출계획 구경하기</button>
          </div>

          <!-- 지도 경로 모티프를 이어받은 라인 -->
          <div class="route-line reveal" aria-hidden="true">
            <span class="node start">★</span>
            <span class="seg"></span><span class="node">1</span>
            <span class="seg"></span><span class="node">2</span>
            <span class="seg"></span><span class="node">3</span>
          </div>
        </div>
      </header>

      <!-- WHY -->
      <section class="why">
        <div class="wrap why-grid">
          <div class="why-head reveal">
            <div class="kicker">Why LocalHub</div>
            <h2>설마... 이미 <span class="accent">무단</span>은 아니시죠?</h2>
          </div>
          <div class="why-body reveal">
            <p>
              점심시간, 집 가기 전, 수업 사이. 지금 당장 나가고 싶은 당신을 위해 준비했어요.
            </p>
            <p>
              LocalHub는 당신의 한계를 시험하는 <b>엄청난 코스</b>를 대신 골라,
              출발부터 마지막 장소까지 <br> 지도 위에 이어드립니다.
            </p>
          </div>
        </div>
      </section>

      <!-- HOW -->
      <section class="how">
        <div class="wrap">
          <div class="sec-head reveal">
            <div class="kicker">How it works</div>
            <h2><span class="accent">엄청난 코스</span>가 당신을 기다립니다!</h2>
          </div>
          <ol class="steps">
            <li v-for="(s, i) in STEPS" :key="s.n" class="step reveal" :style="{ '--i': i }">
              <span class="step-n">{{ s.n }}</span>
              <div class="step-body">
                <h3>{{ s.t }}</h3>
                <p>{{ s.d }}</p>
              </div>
            </li>
          </ol>
        </div>
      </section>

      <!-- VALUES -->
      <section class="values">
        <div class="wrap">
          <div class="sec-head reveal">
            <div class="kicker">What's different</div>
            <h2>뭐가 새로운데?</h2>
          </div>
          <div class="value-grid">
            <article v-for="(v, i) in VALUES" :key="v.t" class="value-card reveal" :style="{ '--i': i }">
              <span class="v-ico">{{ v.ico }}</span>
              <h3>
                {{ v.t }}
                <span v-if="v.sub" class="value-sub">{{ v.sub }}</span>
              </h3>
              <p>{{ v.d }}</p>
            </article>
          </div>
        </div>
      </section>

      <!-- MAKERS -->
      <section class="makers">
        <div class="wrap makers-grid">
          <div class="makers-head reveal">
            <div class="kicker">The makers</div>
            <h2>우리가 누구?</h2>
            <p>
              LocalHub는 SSAFY 역삼캠퍼스의 AI온보딩 바이브코딩 팀 프로젝트로 시작했어요.
              저희가 지금 이 곳을 나가고 싶다는건 아닙니다.
            </p>
          </div>
          <ul class="maker-list reveal">
            <li v-for="m in MAKERS" :key="m.name" class="maker">
              <span class="m-dot"></span>
              <span class="m-name">{{ m.name }}</span>
              <span class="m-role">{{ m.role }}</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- CTA -->
      <section class="cta">
        <div class="wrap cta-in reveal">
          <h2>지금 몇 분 비어 있나요?</h2>
          <p>그 시간에 딱 맞는 코스를 1분 안에 그려드릴게요.</p>
          <button class="btn-solid lg" @click="router.push({ name: 'course' })">코스 만들기 <span class="arrow">→</span></button>
        </div>
      </section>
    </main>

    <footer class="foot">
      <div class="wrap foot-in">
        <a class="logo sm" href="#" @click.prevent="router.push({ name: 'Home' })"><span class="dot"></span>LocalHub</a>
        <span class="foot-copy">SSAFY 역삼캠퍼스 · Local walking courses</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* CSS 변수(--ink, --route 등)는 전역 style.css의 :root 에 정의됨. 여기서 재정의하지 않는다. */
.page{font-family:'Pretendard','Archivo',sans-serif;color:var(--ink);background:var(--paper);
  -webkit-font-smoothing:antialiased;min-height:100vh}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}

/* footer 로고 (전역 nav 로고와 별개, 이 파일 안에서만 사용) */
.logo{display:flex;align-items:center;gap:9px;font-family:'Archivo',sans-serif;font-weight:800;
  letter-spacing:-.03em;font-size:18px;text-decoration:none;color:var(--ink)}
.logo.sm{font-size:16px}
.logo .dot{width:9px;height:9px;border-radius:50%;background:var(--route);box-shadow:0 0 0 4px rgba(3,78,161,.12)}

/* shared buttons */
.btn-solid{height:50px;padding:0 24px;border:0;border-radius:14px;cursor:pointer;background:var(--ink);
  color:#fff;font-family:inherit;font-size:15px;font-weight:600;display:inline-flex;align-items:center;gap:9px;
  transition:background .25s var(--ease),transform .25s var(--ease),box-shadow .3s var(--ease)}
.btn-solid:hover{background:var(--route);transform:translateY(-2px);box-shadow:0 16px 32px -14px rgba(3,78,161,.55)}
.btn-solid.lg{height:56px;padding:0 30px;font-size:16px}
.btn-solid .arrow{transition:transform .3s var(--ease)}
.btn-solid:hover .arrow{transform:translateX(4px)}
.btn-ghost{height:50px;padding:0 22px;border:1px solid var(--line-strong);border-radius:14px;cursor:pointer;
  background:#fff;font-family:inherit;font-size:15px;font-weight:600;color:var(--ink);
  transition:border-color .2s var(--ease),color .2s var(--ease)}
.btn-ghost:hover{border-color:var(--route);color:var(--route)}

/* eyebrow / kicker / headings */
.eyebrow,.kicker{font-family:'Archivo',sans-serif;font-size:11.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--route);font-weight:600}
h2{font-size:30px;font-weight:700;letter-spacing:-.03em;line-height:1.2}
.accent{color:var(--route)}

/* HERO */
.hero{padding:56px 0 8px;border-bottom:1px solid var(--line);background:#fff}
.hero .eyebrow{margin-bottom:16px}
.hero h1{font-size:clamp(34px,6vw,58px);font-weight:800;letter-spacing:-.04em;line-height:1.06}
.hero .lede{max-width:600px;margin-top:20px;font-size:16.5px;line-height:1.7;color:var(--ink-60)}
.hero-cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:30px}
.route-line{display:flex;align-items:center;margin:56px 0 0;padding-bottom:4px}
.route-line .node{flex:none;width:30px;height:30px;border-radius:50%;background:#fff;border:1.5px solid var(--route);
  color:var(--route);font-family:'Archivo',sans-serif;font-weight:700;font-size:12px;
  display:flex;align-items:center;justify-content:center}
.route-line .node.start{background:var(--route);border-color:var(--route);color:#fff}
.route-line .seg{width:64px;max-width:12vw;height:0;border-top:1.5px dashed var(--line-strong)}

/* WHY */
.why{padding:72px 0}
.why-grid{display:grid;grid-template-columns:.8fr 1.2fr;gap:40px;align-items:start}
.why-head h2{margin-top:12px}
.why-body p{font-size:16.5px;line-height:1.8;color:var(--ink-60)}
.why-body p + p{margin-top:16px}
.why-body b{color:var(--ink);font-weight:600}

/* section head */
.sec-head{margin-bottom:34px}
.sec-head h2{margin-top:12px}

/* HOW */
.how{padding:12px 0 78px}
.steps{list-style:none;margin:0;padding:0;display:grid;gap:0}
.step{position:relative;display:flex;gap:20px;padding:22px 0 22px 4px}
.step + .step{border-top:1px solid var(--line)}
.step-n{flex:none;width:52px;font-family:'Archivo',sans-serif;font-weight:800;font-size:26px;
  letter-spacing:-.02em;color:var(--route);line-height:1.1}
.step-body h3{font-size:18px;font-weight:700;letter-spacing:-.02em}
.step-body p{margin-top:7px;font-size:15px;line-height:1.65;color:var(--ink-60);max-width:640px}

/* VALUES */
.values{padding:78px 0;border-top:1px solid var(--line);background:#fff}
.value-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.value-card{border:1px solid var(--line);border-radius:18px;padding:26px 24px;background:var(--paper);
  transition:border-color .2s var(--ease),box-shadow .25s var(--ease),transform .2s var(--ease)}
.value-card:hover{border-color:var(--line-strong);transform:translateY(-3px);box-shadow:0 18px 38px -24px rgba(14,16,19,.4)}
.v-ico{font-size:26px;line-height:1}
.value-card h3{margin-top:16px;font-size:17px;font-weight:700;letter-spacing:-.02em}
.value-card p{margin-top:9px;font-size:14.5px;line-height:1.65;color:var(--ink-60)}

/* MAKERS */
.makers{padding:78px 0}
.makers-grid{display:grid;grid-template-columns:1fr 1fr;gap:44px;align-items:center}
.makers-head h2{margin-top:12px}
.makers-head p{margin-top:14px;font-size:16px;line-height:1.75;color:var(--ink-60);max-width:440px}
.maker-list{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.maker{display:flex;align-items:center;gap:14px;padding:16px 18px;border:1px solid var(--line);
  border-radius:14px;background:#fff;transition:border-color .2s var(--ease)}
.maker:hover{border-color:var(--line-strong)}
.m-dot{width:9px;height:9px;border-radius:50%;background:var(--route);flex:none;box-shadow:0 0 0 4px var(--route-soft)}
.m-name{font-size:15px;font-weight:600}
.m-role{margin-left:auto;font-family:'Archivo',sans-serif;font-size:11.5px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-30);font-weight:600}

/* CTA */
.cta{padding:0 0 88px}
.cta-in{border:1px solid var(--line);border-radius:24px;background:var(--ink);color:#fff;
  padding:56px 40px;text-align:center}
.cta-in h2{color:#fff}
.cta-in p{margin-top:12px;font-size:16px;color:rgba(255,255,255,.66)}
.cta-in .btn-solid{margin-top:26px;background:#fff;color:var(--ink)}
.cta-in .btn-solid:hover{background:var(--route);color:#fff}

/* FOOTER */
.foot{border-top:1px solid var(--line);background:#fff;padding:26px 0}
.foot-in{display:flex;align-items:center;justify-content:space-between;gap:16px}
.foot-copy{font-size:12.5px;color:var(--ink-30)}

/* reveal on scroll */
.reveal{opacity:0;transform:translateY(18px);transition:opacity .6s var(--ease),transform .6s var(--ease);
  transition-delay:calc(var(--i, 0) * 70ms)}
.reveal.in{opacity:1;transform:none}

/* responsive */
@media(max-width:820px){
  .nav-links{display:none}
  .why-grid,.makers-grid{grid-template-columns:1fr;gap:22px}
  .value-grid{grid-template-columns:1fr}
  h2{font-size:26px}
  .hero{padding:56px 0 4px}
  .cta-in{padding:44px 24px}
}
@media(max-width:560px){
  .route-line .seg{width:34px}
  .step-n{width:42px;font-size:22px}
}
@media(prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important}
  .reveal{opacity:1;transform:none}
}
.value-sub {
  font-size: 12px;
  font-weight: 500;
  color: var(--ink-60);
}
</style>