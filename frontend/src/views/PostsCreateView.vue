<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()

// 로컬 테스트용
// const API_BASE_URL = 'http://127.0.0.1:8000'

const API_BASE_URL = 'https://ssafyescape.onrender.com'

// ── 이전 화면(CourseResultView)에서 넘어온 값 ─────────────────────────
const incoming = window?.history?.state?.prefill || {}

// 코스에 대한 요약 정보(시간/지역/동행)는 이전 화면에서 확정된 값이라
// 여기서는 수정하지 않고 "표시"만 한다.
const courseMeta = reactive({
  time: incoming.time || '1시간',
  district: incoming.district || '강남구',
  companion: incoming.companion || '싸피 친구',
})

// 지도에 그대로 꽂힐 코스 데이터 (title/totalTime/start/stops)
const fallbackCourse = {
  title: '역삼 힐링 산책 코스',
  totalTime: '1시간',
  start: {
    name: 'SSAFY 역삼캠퍼스',
    lat: 37.5009,
    lng: 127.0369,
  },
  stops: [
    {
      name: '선릉·정릉',
      category: '왕릉 산책',
      description: '도심 속에서 조용히 산책하기 좋은 장소',
      stay: '20분',
      lat: 37.5088,
      lng: 127.0490,
    },
    {
      name: '최인아책방',
      category: '독립서점',
      description: '조용히 책을 읽기 좋은 공간',
      stay: '15분',
      lat: 37.5045,
      lng: 127.0405,
    },
    {
      name: '테헤란로 커피',
      category: '카페',
      description: '산책 후 쉬어가기 좋은 로스터리',
      stay: '20분',
      lat: 37.5006,
      lng: 127.0360,
    },
  ],
}

const courseData = incoming.course || fallbackCourse

// ── 폼 (제목 / 본문 / 비밀번호만 사용자가 직접 다룸) ───────────────────
const form = ref({
  title: incoming.title || `${courseData.title}`,
  content: incoming.content || '',
  password: '',
})

const previewContent = computed(() => {
  return form.value.content || '작성한 본문 내용이 이곳에 미리 표시됩니다.'
})

function handlePasswordInput(e) {
  form.value.password = e.target.value.replace(/[^0-9]/g, '').slice(0, 4)
}

// ── 지도 (읽기 전용: 이전 화면에서 확정한 코스에 핀만 꽂아 보여줌) ─────
let map = null
let markers = []
let layersGroup = null

function pinIcon(label, isStart) {
  return L.divIcon({
    className: '',
    iconSize: [36, 46],
    iconAnchor: [18, 44],
    popupAnchor: [0, -42],
    html: `<div class="pin ${isStart ? 'start' : ''}"><div class="head"></div><div class="num">${label}</div></div>`,
  })
}

function hoverHtml(s) {
  return `<div class="hovercard"><div class="hc-top">
    <div class="hc-cat">${s.category || ''}</div><div class="hc-name">${s.name}</div>
    <div class="hc-desc">${s.description || ''}</div></div>
    <div class="hc-foot">머무름 <b>${s.stay || '-'}</b></div></div>`
}

function initMap() {
  if (!courseData?.start || !courseData?.stops?.length) return

  map = L.map('postCourseMap', {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView([courseData.start.lat, courseData.start.lng], 15)

  L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; Stadia Maps &copy; OpenMapTiles &copy; OpenStreetMap',
    maxZoom: 20,
  }).addTo(map)

  const seq = [{ ...courseData.start, isStart: true }, ...courseData.stops]
  const ll = seq.map((p) => [p.lat, p.lng])

  layersGroup = L.layerGroup([
    L.polyline(ll, {
      color: '#fff',
      weight: 8,
      opacity: 1,
      lineJoin: 'round',
    }),
    L.polyline(ll, {
      color: '#0E1013',
      weight: 3.5,
      opacity: 1,
      dashArray: '1 9',
      lineCap: 'round',
    }),
  ]).addTo(map)

  seq.forEach((p, i) => {
    const mk = L.marker([p.lat, p.lng], {
      icon: pinIcon(p.isStart ? '★' : String(i), p.isStart),
    }).addTo(map)

    if (!p.isStart) {
      mk.bindPopup(hoverHtml(p), {
        closeButton: false,
        offset: [0, -6],
      })
    }

    markers.push(mk)
  })

  map.fitBounds(L.latLngBounds(ll).pad(0.25))
}

onMounted(() => {
  initMap()
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }

  markers = []
  layersGroup = null
})

// ── 제출 ───────────────────────────────────────────────────────────
async function submitPost() {
  if (!form.value.title.trim()) {
    alert('제목을 입력해주세요.')
    return
  }

  if (!form.value.content.trim()) {
    alert('본문을 입력해주세요.')
    return
  }

  if (!/^[0-9]{4}$/.test(form.value.password)) {
    alert('비밀번호는 숫자 4자리로 입력해주세요.')
    return
  }

  if (!courseData.stops?.length) {
    alert('공유할 코스 정보가 없습니다. 코스 만들기부터 다시 시작해주세요.')
    return
  }

  const payload = {
    title: form.value.title,
    content: form.value.content,
    password: form.value.password,
    time: courseMeta.time,
    district: courseMeta.district,
    companion: courseMeta.companion,

    // DB의 post_places 연결은 현재 쓰지 않으므로 빈 배열
    place_ids: [],

    // 상세 페이지에서 지도와 오른쪽 코스 여정을 그대로 보여주기 위한 코스 원본 데이터
    course: courseData,
  }

  console.log('게시글 작성 payload:', payload)
  console.log('요청 주소:', `${API_BASE_URL}/api/posts`)

  try {
    const response = await fetch(`${API_BASE_URL}/api/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error('게시글 작성 실패 상세:', errorData)
      alert(errorData.detail ? JSON.stringify(errorData.detail, null, 2) : '게시글 작성 실패')
      return
    }

    const data = await response.json()
    console.log('게시글 작성 성공:', data)

    alert('게시글이 작성되었습니다.')
    router.push({ name: 'Posts' })
  } catch (error) {
    console.error(error)
    alert('게시글 작성 API 연결 전이거나 오류가 발생했습니다. 콘솔에서 전송 데이터를 확인해주세요.')
    console.log('전송 데이터:', payload)
  }
}
</script>

<template>
  <section class="post-create-page">
    <div class="page-header">
      <div class="kicker">Share Your Course</div>
      <h1>나만의 코스를 공유해보세요</h1>
      <p>멀티캠퍼스 역삼 주변을 중심으로 나만의 이동 경로와 리뷰를 공유해보세요.</p>
    </div>

    <div class="page-layout">
      <form class="form-column" @submit.prevent="submitPost">
        <!-- 게시글 정보 -->
        <section class="card">
          <h2>게시글 정보</h2>

          <div class="field">
            <label for="title">제목</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              placeholder="회사 근처에서 즐기는 역삼 반나절 코스 추천!"
            />
          </div>

          <!-- 이전 화면에서 확정된 값 — 수정 대상 아님, 표시만 -->
          <div class="meta-chips">
            <span class="chip">
              <span class="k">Time</span>
              <span class="v">{{ courseMeta.time }}</span>
            </span>

            <span class="chip">
              <span class="k">Area</span>
              <span class="v">{{ courseMeta.district }}</span>
            </span>

            <span class="chip">
              <span class="k">With</span>
              <span class="v">{{ courseMeta.companion }}</span>
            </span>
          </div>

          <div class="field">
            <label for="content">본문</label>
            <div class="textarea-box">
              <textarea
                id="content"
                v-model="form.content"
                maxlength="1000"
                rows="7"
                placeholder="코스를 추천하는 이유, 이동 팁, 분위기, 주의할 점 등을 작성해주세요."
              ></textarea>
              <span>{{ form.content.length }}/1000</span>
            </div>
          </div>

          <div class="field password-field">
            <label for="password">수정/삭제용 비밀번호</label>
            <input
              id="password"
              :value="form.password"
              type="password"
              inputmode="numeric"
              maxlength="4"
              placeholder="4자리 숫자 입력"
              @input="handlePasswordInput"
            />
            <p>비밀번호는 숫자 4자리로 입력해주세요.</p>
          </div>
        </section>

        <!-- 선택한 코스 → 지도로 표시 (읽기 전용) -->
        <section class="card">
          <div class="course-title-row">
            <h2>선택한 코스</h2>
            <p>{{ courseData.title }}</p>
          </div>

          <div id="postCourseMap" class="course-map"></div>
        </section>

        <div class="button-row">
          <button
            type="button"
            class="cancel-button"
            @click="router.push('/posts')"
          >
            취소
          </button>

          <button type="submit" class="submit-button">
            게시글 작성하기
          </button>
        </div>
      </form>

      <aside class="preview-panel">
        <div class="kicker">Preview</div>
        <h3>{{ form.title || '게시글 제목이 표시됩니다' }}</h3>

        <div class="preview-tags">
          <span>⏱ {{ courseMeta.time }}</span>
          <span>⌖ {{ courseMeta.district }}</span>
          <span>♙ {{ courseMeta.companion }}와 함께</span>
        </div>

        <p class="preview-content">{{ previewContent }}</p>

        <div class="preview-course">
          <h4>선택한 코스</h4>

          <div class="preview-cards">
            <div
              v-for="(s, i) in courseData.stops"
              :key="s.name + i"
              class="pv-card"
            >
              <div class="pv-idx">{{ i + 1 }}</div>

              <div class="pv-body">
                <div class="pv-name-row">
                  <span class="pv-name">{{ s.name }}</span>
                  <span class="pv-cat">{{ s.category }}</span>
                </div>

                <div class="pv-desc">{{ s.description }}</div>

                <div class="pv-stay">
                  머무름 <b>{{ s.stay }}</b>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="preview-help">ⓘ 미리보기는 실제 게시글과 다를 수 있습니다.</div>
      </aside>
    </div>
  </section>
</template>

<!-- 전역: Leaflet이 동적 생성하는 DOM(핀/팝업/컨트롤)은 scoped로 안 먹으므로 전역 처리 -->
<style>
.pin {
  position: relative;
  width: 36px;
  height: 46px;
  display: flex;
  justify-content: center;
  filter: drop-shadow(0 8px 10px rgba(14, 16, 19, 0.22));
}

.pin::after {
  content: "";
  position: absolute;
  bottom: 1px;
  left: 50%;
  transform: translateX(-50%);
  width: 10px;
  height: 4px;
  border-radius: 50%;
  background: rgba(14, 16, 19, 0.25);
  filter: blur(1px);
}

.pin .head {
  width: 32px;
  height: 32px;
  border-radius: 50% 50% 50% 4px;
  transform: rotate(45deg);
  background: var(--ink);
  border: 2.5px solid #fff;
  transition: transform 0.2s var(--ease);
}

.pin .num {
  position: absolute;
  top: 5px;
  left: 0;
  right: 0;
  text-align: center;
  color: #fff;
  font-family: 'Archivo', sans-serif;
  font-weight: 700;
  font-size: 14px;
  line-height: 20px;
  pointer-events: none;
}

.pin.start .head {
  background: var(--route);
}

.pin:hover .head {
  transform: rotate(45deg) scale(1.1);
}

.hovercard {
  background: #fff;
  border-radius: 14px;
  border: 1px solid var(--line);
  box-shadow: 0 18px 40px -18px rgba(14, 16, 19, 0.45);
  min-width: 200px;
  overflow: hidden;
}

.hovercard .hc-top {
  padding: 12px 14px;
}

.hovercard .hc-cat {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--route);
  text-transform: uppercase;
}

.hovercard .hc-name {
  font-size: 14.5px;
  font-weight: 700;
  margin-top: 3px;
  letter-spacing: -0.01em;
}

.hovercard .hc-desc {
  font-size: 12px;
  color: var(--ink-60);
  margin-top: 4px;
  line-height: 1.5;
}

.hovercard .hc-foot {
  border-top: 1px solid var(--line);
  padding: 8px 14px;
  font-size: 11px;
  color: var(--ink-30);
}

.hovercard .hc-foot b {
  color: var(--ink);
  font-weight: 600;
}

#postCourseMap .leaflet-tile-pane {
  filter: contrast(1.02) brightness(1.01);
}

#postCourseMap.leaflet-container {
  font-family: 'Pretendard', sans-serif;
  background: #eef0f2;
}

#postCourseMap .leaflet-popup-content-wrapper {
  background: transparent;
  box-shadow: none;
  padding: 0;
  border-radius: 14px;
}

#postCourseMap .leaflet-popup-content {
  margin: 0;
  width: auto !important;
}

#postCourseMap .leaflet-popup-tip {
  background: #fff;
  border: 1px solid var(--line);
}

#postCourseMap .leaflet-popup-close-button {
  display: none;
}

#postCourseMap .leaflet-control-zoom {
  border: none !important;
  box-shadow: 0 6px 20px -10px rgba(14, 16, 19, 0.3) !important;
  margin: 14px !important;
}

#postCourseMap .leaflet-control-zoom a {
  border-radius: 10px !important;
  color: var(--ink) !important;
  border: 1px solid var(--line) !important;
  background: #fff !important;
  width: 32px !important;
  height: 32px !important;
  line-height: 30px !important;
  font-size: 17px !important;
}

#postCourseMap .leaflet-control-attribution {
  font-size: 10px !important;
  background: rgba(255, 255, 255, 0.7) !important;
}
</style>

<style scoped>
/* CSS 변수(--ink,--route,--line 등)는 전역 style.css :root 에 정의됨. 여기서 재정의하지 않는다. */
.post-create-page {
  max-width: 1220px;
  margin: 0 auto;
  padding: 52px 24px 90px;
  color: var(--ink);
  font-family: 'Pretendard', 'Archivo', sans-serif;
}

.page-header {
  margin-bottom: 30px;
}

.page-header .kicker {
  font-family: 'Archivo', sans-serif;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--route);
  font-weight: 600;
  margin-bottom: 10px;
}

.page-header h1 {
  margin: 0;
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -0.035em;
}

.page-header p {
  margin: 12px 0 0;
  font-size: 15px;
  color: var(--ink-60);
}

.page-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 24px;
  align-items: start;
}

.form-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 카드 — 중성 잉크톤 그림자로 통일 (붉은/이질적인 색조 제거) */
.card,
.preview-panel {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper);
  box-shadow: 0 14px 34px -22px rgba(14, 16, 19, 0.35);
}

.card {
  padding: 22px;
}

.card h2,
.preview-panel h3 {
  margin: 0 0 18px;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.field {
  margin-bottom: 16px;
}

.field:last-child {
  margin-bottom: 0;
}

.field label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 700;
}

.field input,
.field textarea {
  width: 100%;
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  background: #fff;
  color: var(--ink);
  font-family: inherit;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease);
}

.field input {
  height: 44px;
  padding: 0 14px;
}

.field textarea {
  padding: 13px;
  line-height: 1.6;
  resize: vertical;
}

.field input:focus,
.field textarea:focus {
  border-color: var(--route);
  box-shadow: 0 0 0 4px var(--route-soft);
}

.textarea-box {
  position: relative;
}

.textarea-box span {
  position: absolute;
  right: 12px;
  bottom: 10px;
  font-size: 12px;
  color: var(--ink-30);
}

.password-field p {
  margin: 7px 0 0;
  font-size: 12px;
  color: var(--ink-30);
}

/* 이전 화면에서 넘어온 값 — 읽기 전용 칩 */
.meta-chips {
  display: flex;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  margin-bottom: 16px;
  width: fit-content;
}

.meta-chips .chip {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 9px 16px;
  position: relative;
}

.meta-chips .chip + .chip::before {
  content: "";
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 1px;
  background: var(--line);
}

.meta-chips .chip .k {
  font-family: 'Archivo', sans-serif;
  font-size: 9.5px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ink-30);
  font-weight: 600;
}

.meta-chips .chip .v {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
}

.course-title-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.course-title-row h2 {
  margin: 0;
}

.course-title-row p {
  margin: 0;
  color: var(--route);
  font-size: 12.5px;
  font-weight: 600;
}

.course-map {
  width: 100%;
  height: 340px;
  border-radius: 14px;
  overflow: hidden;
  background: #eef0f2;
}

.button-row {
  display: grid;
  grid-template-columns: 1fr 1.15fr;
  gap: 12px;
  max-width: 480px;
  margin: 10px auto 0;
  width: 100%;
}

.cancel-button,
.submit-button {
  height: 52px;
  border-radius: 14px;
  font-size: 15.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.25s var(--ease), transform 0.25s var(--ease),
    box-shadow 0.3s var(--ease), border-color 0.2s var(--ease);
}

.cancel-button {
  border: 1px solid var(--line-strong);
  background: #fff;
  color: var(--ink);
}

.cancel-button:hover {
  border-color: var(--ink);
  transform: translateY(-2px);
}

.submit-button {
  border: 0;
  background: var(--ink);
  color: #fff;
  box-shadow: 0 14px 30px -14px rgba(14, 16, 19, 0.5);
}

.submit-button:hover {
  background: var(--route);
  transform: translateY(-2px);
  box-shadow: 0 16px 34px -14px rgba(3, 78, 161, 0.5);
}

/* 미리보기 */
.preview-panel {
  position: sticky;
  top: 84px;
  padding: 24px;
}

.preview-panel .kicker {
  font-family: 'Archivo', sans-serif;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--route);
  font-weight: 600;
  margin-bottom: 8px;
}

.preview-panel h3 {
  margin: 0 0 16px;
  font-size: 21px;
  line-height: 1.35;
  letter-spacing: -0.02em;
  font-weight: 800;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}

.preview-tags span {
  padding: 7px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--route);
  font-size: 12px;
  font-weight: 600;
  background: var(--route-soft);
}

.preview-content {
  margin: 0;
  color: var(--ink-60);
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-line;
}

.preview-course {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
}

.preview-course h4 {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 700;
}

.preview-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pv-card {
  position: relative;
  display: flex;
  gap: 12px;
  padding: 13px 13px 13px 12px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: #fff;
}

.pv-card::before {
  content: "";
  position: absolute;
  left: 23px;
  top: -6px;
  height: 6px;
  width: 1.5px;
  background: var(--line-strong);
}

.pv-card:first-child::before {
  display: none;
}

.pv-idx {
  flex: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1.5px solid var(--route);
  color: var(--route);
  background: #fff;
  font-family: 'Archivo', sans-serif;
  font-weight: 700;
  font-size: 11.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}

.pv-body {
  flex: 1;
  min-width: 0;
}

.pv-name-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.pv-name {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--ink);
}

.pv-cat {
  font-size: 10.5px;
  font-weight: 600;
  color: var(--ink-30);
  letter-spacing: 0.02em;
}

.pv-desc {
  font-size: 12.5px;
  color: var(--ink-60);
  margin-top: 4px;
  line-height: 1.5;
}

.pv-stay {
  font-size: 11.5px;
  color: var(--ink-30);
  margin-top: 8px;
}

.pv-stay b {
  color: var(--ink-60);
  font-weight: 600;
}

.preview-help {
  margin-top: 18px;
  color: var(--ink-30);
  font-size: 12px;
}

@media (max-width: 1100px) {
  .page-layout {
    grid-template-columns: 1fr;
  }

  .preview-panel {
    position: static;
  }
}

@media (max-width: 720px) {
  .post-create-page {
    padding: 34px 14px 70px;
  }

  .page-header h1 {
    font-size: 28px;
  }

  .button-row {
    grid-template-columns: 1fr;
  }

  .course-map {
    height: 260px;
  }
}
</style>