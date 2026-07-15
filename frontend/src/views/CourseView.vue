<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const STEPS = [
  {
    key: 'time',
    q: '얼마나 <span class="accent">둘러보실</span> 생각이세요?',
    hint: '남은 시간에 맞춰 들를 장소 수를 정할게요.',
    placeholder: '예) 애매하게 40분쯤 비어요',
    chips: [
      { ico: '⚡', label: '30분', value: '30분 · 가볍게 한 곳' },
      { ico: '☕', label: '1시간', value: '1시간 · 두세 곳' },
      { ico: '🍚', label: '2시간', value: '2시간 · 여유 코스' },
      { ico: '🌙', label: '반나절', value: '반나절 · 제대로' }
    ]
  },
  {
    key: 'field',
    q: '<span class="accent">어느 구에서</span> 돌아다니실 건가요?',
    hint: '강남구 주변을 빠르게 선택하거나, 직접 입력해 주세요.',
    placeholder: '예) 강남구',
    chips: [
      { ico: '📍', label: '강남구', value: '강남구' },
      { ico: '📍', label: '서초구', value: '서초구' },
      { ico: '📍', label: '송파구', value: '송파구' },
      { ico: '📍', label: '강동구', value: '강동구' },
      { ico: '📍', label: '관악구', value: '관악구' }
    ]
  },
  {
    key: 'companion',
    q: '<span class="accent">누구와 함께</span> 가세요?',
    hint: '동행에 맞춰 장소 톤을 바꿔드려요.',
    placeholder: '예) 오랜만에 만난 고등학교 친구',
    chips: [
      { ico: '🧍', label: '혼자', value: '혼자' },
      { ico: '💻', label: '싸피 친구', value: '싸피 친구와' },
      { ico: '👪', label: '부모님', value: '찾아오신 부모님과' },
      { ico: '🎓', label: '프로님과', value: '프로님과 함께' }
    ]
  },
  {
    key: 'concept',
    q: '<span class="accent">어떤 코스</span>였으면 좋겠어요?',
    hint: '떠오르는 게 없으면 아래에서 골라도 되고, 직접 적어도 좋아요.',
    placeholder: '예) 조용히 걷다가 커피 마실 수 있는 곳',
    chips: [
      { ico: '🌿', label: '조용한 산책', value: '조용히 걷기 좋은' },
      { ico: '📸', label: '사진 맛집', value: '사진 찍기 좋은' },
      { ico: '🍜', label: '밥집 위주', value: '맛집 중심' },
      { ico: '🎨', label: '전시·문화', value: '전시·문화 공간' },
      { ico: '🔋', label: '빠른 기분전환', value: '짧고 굵은 기분전환' }
    ]
  }
]

const step = ref(0)
const answers = reactive({})
const input = ref('')
const typing = ref(false)

// 모든 질문에 답했는지 (step 이 마지막을 넘어서면 완료)
const isDone = computed(() => step.value >= STEPS.length)
// 완료가 아닐 때만 현재 질문을 안전하게 참조
const current = computed(() => (isDone.value ? null : STEPS[step.value]))

const fillWidth = computed(() => {
  const denom = STEPS.length - 1
  if (!denom) return '0%'
  const s = Math.min(step.value, STEPS.length - 1)
  return `${Math.round((s / denom) * 100)}%`
})

function selectChip(i) {
  const s = STEPS[step.value]
  const c = s.chips[i]
  recordAnswer(s.key, c.value ?? c.label)
}

function submitText() {
  const v = input.value && input.value.trim()
  if (!v) return
  recordAnswer(STEPS[step.value].key, v)
}

function recordAnswer(key, value) {
  answers[key] = value
  input.value = ''
  step.value++              // ← 핵심: 항상 step 을 올린다 (마지막이면 isDone=true 가 되어 최종 UI 표시)
  if (!isDone.value) {
    typing.value = true     // 다음 질문 전에 타이핑 표시
    setTimeout(() => { typing.value = false }, 500)
  }
}

function handleNextClick() {
  const prompt = `출발지: SSAFY 역삼캠퍼스 / 확보 시간: ${answers.time || ''} / 구: ${answers.field || ''} / 동행: ${answers.companion || ''} / 원하는 코스: ${answers.concept || ''}`
  console.log(prompt)
  router.push({ name: 'course-result', state: { answers: { ...answers } } })
}

onMounted(() => {
  typing.value = true
  setTimeout(() => { typing.value = false }, 420)
})
</script>

<template>
  <div>
    <nav id="nav">
      <div class="wrap nav-in">
        <router-link to="/" class="logo"><span class="dot"></span>LocalHub</router-link>
        <div class="seg">
          <div class="seg-track">
            <span class="seg-fill" :style="{ width: fillWidth }"></span>
            <span
              v-for="(d, i) in STEPS" :key="i"
              class="seg-dot"
              :class="{ done: i < step || isDone, active: !isDone && i === step }"
            ></span>
          </div>
          <span class="seg-count">STEP <b>{{ String(Math.min(step + 1, STEPS.length)).padStart(2, '0') }}</b> / {{ STEPS.length }}</span>
        </div>
      </div>
    </nav>

    <main>
      <div class="chat">
        <!-- 지금까지 답한 것들 + 다음 질문을 순서대로 보여주기 위해
             현재 질문/타이핑은 답변 목록 아래에 렌더 -->
        <template v-for="(k, idx) in Object.keys(answers)" :key="k + idx">
          <div class="row me"><div class="ans">{{ answers[k] }}</div></div>
        </template>

        <!-- 타이핑 -->
        <div v-if="typing" class="row bot typing">
          <div class="block"><i></i><i></i><i></i></div>
        </div>

        <!-- 현재 질문 (완료 전에만) -->
        <div v-else-if="current" class="row bot">
          <div class="block">
            <div class="q" v-html="current.q"></div>
            <div class="q hint" v-text="current.hint"></div>
            <div class="chips">
              <button v-for="(c, i) in current.chips" :key="i" class="chip" @click="selectChip(i)">
                <span class="ico">{{ c.ico }}</span>
                <span>{{ c.label }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 완료 인사 -->
        <div v-else class="row bot">
          <div class="block">
            <div class="q">다 모았어요. 이제 지도에 코스를 그려볼게요 <span class="accent">👇</span></div>
          </div>
        </div>
      </div>
    </main>

    <div class="dock">
      <div class="dock-in">
        <!-- 입력창: 완료 전에만 -->
        <div id="inputWrap" v-if="!isDone">
          <div class="input-row">
            <textarea
              v-model="input" rows="1"
              :placeholder="current ? current.placeholder : ''"
              @keydown.enter.exact.prevent="submitText"
            ></textarea>
            <button class="send" :disabled="!input.trim()" @click="submitText">↑</button>
          </div>
        </div>

        <!-- 최종: 요약 + 다음 버튼 -->
        <div class="final" v-else>
          <div class="summary">
            <span class="tag">⏱ {{ answers.time }}</span>
            <span class="tag">📍 {{ answers.field }}</span>
            <span class="tag">👥 {{ answers.companion }}</span>
            <span class="tag">🎯 {{ answers.concept }}</span>
          </div>
          <button class="btn-next" @click="handleNextClick">지도와 코스 만들기 <span class="arrow">→</span></button>
        </div>
      </div>
      <p class="helper">4개의 질문에 답하면 <b>지도와 함께 코스가 만들어집니다.</b></p>
    </div>
  </div>
</template>

<style scoped>
.wrap.nav-in{max-width:1240px;margin:0 auto;padding:0 24px;height:66px;display:flex;align-items:center;justify-content:space-between}
.logo{display:flex;align-items:center;gap:9px;text-decoration:none;color:var(--ink);font-family:'Archivo',sans-serif;font-weight:800;letter-spacing:-.03em;font-size:19px}
.logo .dot{width:9px;height:9px;border-radius:50%;background:var(--route);box-shadow:0 0 0 4px rgba(3,78,161,.12)}
.seg{display:flex;align-items:center;gap:14px}
.seg-track{display:flex;align-items:center;position:relative;height:14px}
.seg-track::before{content:"";position:absolute;left:5px;right:5px;top:50%;height:1px;transform:translateY(-50%);background:var(--line-strong)}
.seg-fill{position:absolute;left:5px;top:50%;height:1px;transform:translateY(-50%);width:0;background:var(--ink);transition:width .55s var(--ease);z-index:1}
.seg-dot{position:relative;z-index:2;width:9px;height:9px;border-radius:50%;background:#fff;border:1px solid var(--line-strong);margin:0 11px;transition:border-color .45s var(--ease),background .45s var(--ease),transform .45s var(--ease)}
.seg-dot:first-child{margin-left:0}
.seg-dot:last-child{margin-right:0}
.seg-dot.done{background:var(--ink);border-color:var(--ink)}
.seg-dot.active{border-color:var(--ink);background:#fff;transform:scale(1.15)}
.seg-count{font-family:'Archivo',sans-serif;font-size:11px;color:var(--ink-30);font-weight:600;letter-spacing:.14em}
.seg-count b{color:var(--ink);font-weight:700}

.chat{max-width:720px;margin:0 auto;padding:40px 24px 220px;display:flex;flex-direction:column;gap:22px}
.row{display:flex;animation:pop .55s var(--ease) backwards}
@keyframes pop{from{opacity:0;transform:translateY(16px)}}
.row.bot{justify-content:flex-start}
.row.me{justify-content:flex-end}
.bot .block{max-width:92%}
.q{font-size:20px;line-height:1.5;font-weight:600;letter-spacing:-.02em;color:var(--ink)}
.q :deep(.accent),.q .accent{color:var(--route)}
.q.hint{display:block;margin-top:8px;font-size:14px;font-weight:400;color:var(--ink-60);letter-spacing:0}
.chips{display:flex;flex-wrap:wrap;gap:9px;margin-top:18px}
.chip{border:1px solid var(--line-strong);background:#fff;cursor:pointer;font-family:inherit;font-size:14.5px;font-weight:600;color:var(--ink);padding:11px 17px;border-radius:12px;display:inline-flex;align-items:center;gap:8px;transition:border-color .2s var(--ease),color .2s var(--ease),background .2s var(--ease),transform .2s var(--ease),box-shadow .2s var(--ease)}
.chip:hover{border-color:var(--route);color:var(--route);transform:translateY(-2px);box-shadow:0 8px 18px -12px rgba(3,78,161,.5)}
.chip .ico{font-size:15px;line-height:1}
.me .ans{background:var(--ink);color:#fff;padding:13px 18px;border-radius:16px 16px 4px 16px;font-size:15px;line-height:1.5;max-width:84%;font-weight:500}
.typing .block{display:inline-flex;gap:5px;padding:6px 2px}
.typing i{width:7px;height:7px;border-radius:50%;background:var(--ink-30);display:block;animation:blink 1.2s infinite}
.typing i:nth-child(2){animation-delay:.18s}
.typing i:nth-child(3){animation-delay:.36s}
@keyframes blink{0%,60%,100%{opacity:.25;transform:translateY(0)}30%{opacity:1;transform:translateY(-3px)}}

.dock{position:fixed;left:0;right:0;bottom:0;z-index:40;background:linear-gradient(to top,#fff 74%,rgba(255,255,255,0));padding:34px 0 0}
.dock-in{max-width:720px;margin:0 auto;padding:0 24px 14px}
.input-row{display:flex;gap:10px;align-items:flex-end;background:#fff;border:1px solid var(--line-strong);border-radius:16px;padding:8px 8px 8px 18px;transition:border-color .22s var(--ease),box-shadow .22s var(--ease)}
.input-row:focus-within{border-color:var(--route);box-shadow:0 0 0 4px var(--route-soft)}
.input-row textarea{flex:1;border:0;outline:0;resize:none;font-family:inherit;font-size:15px;line-height:1.5;color:var(--ink);max-height:120px;padding:7px 0;background:transparent}
.input-row textarea::placeholder{color:var(--ink-30)}
.send{flex:none;width:42px;height:42px;border-radius:12px;border:0;cursor:pointer;background:var(--ink);color:#fff;font-size:17px;display:flex;align-items:center;justify-content:center;transition:background .2s var(--ease),transform .2s var(--ease)}
.send:hover:not(:disabled){background:var(--route);transform:translateY(-1px)}
.send:disabled{background:var(--line-strong);color:#fff;cursor:not-allowed}
.helper{max-width:720px;margin:11px auto 0;padding:0 24px;font-size:12.5px;color:var(--ink-30);text-align:center}
.helper b{color:var(--ink-60);font-weight:600}
.summary{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;margin-bottom:16px}
.tag{font-size:13px;background:var(--route-soft);color:var(--route);padding:7px 13px;border-radius:999px;font-weight:600}
.btn-next{width:100%;height:54px;border:0;border-radius:15px;cursor:pointer;background:var(--ink);color:#fff;font-family:inherit;font-size:15.5px;font-weight:600;display:flex;align-items:center;justify-content:center;gap:9px;transition:background .25s var(--ease),transform .25s var(--ease),box-shadow .3s var(--ease)}
.btn-next:hover{background:var(--route);transform:translateY(-2px);box-shadow:0 14px 30px -12px rgba(3,78,161,.55)}
.btn-next .arrow{transition:transform .3s var(--ease)}
.btn-next:hover .arrow{transform:translateX(4px)}

@media(max-width:560px){.q{font-size:18px}.bot .block{max-width:100%}.chip{font-size:13.5px;padding:10px 14px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>