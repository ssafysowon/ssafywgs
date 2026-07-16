<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const API_BASE_URL = 'https://ssafyescape.onrender.com'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(false)

const showPasswordModal = ref(false)
const password = ref('')
const passwordError = ref('')

let map = null
let markers = []
let layersGroup = null

const detailCourse = computed(() => {
  if (post.value?.course) {
    return post.value.course
  }

  return {
    title: post.value?.title || '공유 코스',
    totalTime: post.value?.time || '',
    start: {
      name: 'SSAFY 역삼캠퍼스',
      lat: 37.5009,
      lng: 127.0369,
    },
    stops: [],
  }
})

onMounted(() => {
  fetchPostDetail()
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }

  markers = []
  layersGroup = null
})

async function fetchPostDetail() {
  loading.value = true

  try {
    console.log('상세 조회 요청 id:', route.params.id)

    const response = await fetch(`${API_BASE_URL}/api/posts/${route.params.id}`)

    if (!response.ok) {
      const errorData = await response.json()
      console.error('게시글 상세 조회 API 오류:', errorData)
      throw new Error('게시글 상세 조회 실패')
    }

    const data = await response.json()
    console.log('게시글 상세 응답:', data)

    post.value = data.post
  } catch (error) {
    console.error('게시글 상세 조회 실패:', error)
    post.value = null
  } finally {
    loading.value = false
  }

  await nextTick()

  if (post.value) {
    try {
      initDetailMap()
    } catch (mapError) {
      console.error('상세 지도 렌더링 실패:', mapError)
    }
  }
}

function goList() {
  router.push('/posts')
}

function openEditPasswordModal() {
  password.value = ''
  passwordError.value = ''
  showPasswordModal.value = true
}

function closePasswordModal() {
  showPasswordModal.value = false
  password.value = ''
  passwordError.value = ''
}

function handlePasswordInput(event) {
  password.value = event.target.value.replace(/[^0-9]/g, '').slice(0, 4)
}

async function verifyPassword() {
  if (!/^[0-9]{4}$/.test(password.value)) {
    passwordError.value = '비밀번호는 숫자 4자리입니다.'
    return
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/posts/${route.params.id}/verify-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        password: password.value,
      }),
    })

    if (!response.ok) {
      throw new Error('비밀번호 확인 실패')
    }

    sessionStorage.setItem(`post-edit-password-${route.params.id}`, password.value)
    router.push(`/posts/${route.params.id}/edit`)
  } catch (error) {
    console.error(error)
    passwordError.value = '비밀번호가 일치하지 않습니다.'
  }
}

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
    <div class="hc-cat">${s.category || ''}</div><div class="hc-name">${s.name || ''}</div>
    <div class="hc-desc">${s.description || ''}</div></div>
    <div class="hc-foot">머무름 <b>${s.stay || '-'}</b></div></div>`
}

function initDetailMap() {
  const course = detailCourse.value

  if (!course?.start || !course?.stops?.length) {
    return
  }

  if (map) {
    map.remove()
    map = null
  }

  map = L.map('detailCourseMap', {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView([course.start.lat, course.start.lng], 15)

  const apiKey = import.meta.env.VITE_STADIA_API_KEY
  const tileUrl = apiKey
    ? `https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=${apiKey}`
    : 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'

  L.tileLayer(tileUrl, {
    attribution: '&copy; Stadia Maps &copy; OpenMapTiles &copy; OpenStreetMap',
    maxZoom: 20,
  }).addTo(map)

  const seq = [{ ...course.start, isStart: true }, ...course.stops]
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

  markers = []

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
</script>

<template>
  <section class="detail-page">
    <div class="breadcrumb">
      <router-link to="/">홈</router-link>
      <span>›</span>
      <router-link to="/posts">공유 게시판</router-link>
      <span>›</span>
      <strong>게시글 상세</strong>
    </div>

    <div v-if="loading" class="loading-box">
      게시글을 불러오는 중입니다.
    </div>

    <div v-else-if="!post" class="empty-box">
      게시글을 찾을 수 없습니다.
    </div>

    <div v-else class="detail-layout">
      <article class="detail-card">
        <div class="tag-row">
          <span v-if="post.time">{{ post.time }}</span>
          <span v-if="post.district">{{ post.district }}</span>
          <span v-if="post.companion">{{ post.companion }}</span>
          <span>추천 코스</span>
        </div>

        <div class="title-row">
          <h1>{{ post.title }}</h1>
          <button type="button" class="edit-button" @click="openEditPasswordModal">
            수정
          </button>
        </div>

        <div class="meta-row">
          <span>작성일 {{ post.created_at || '날짜 없음' }}</span>
          <span>조회 {{ post.views || 0 }}</span>
          <span>장소 {{ detailCourse.stops?.length || post.place_count || 0 }}개</span>
        </div>

        <hr />

        <p class="content">
          {{ post.content }}
        </p>

        <hr />

        <section class="course-section">
          <div class="course-title-row">
            <h2>선택한 코스</h2>
            <p>{{ detailCourse.title }} · {{ detailCourse.totalTime }}</p>
          </div>

          <div
            v-if="detailCourse.stops && detailCourse.stops.length"
            id="detailCourseMap"
            class="course-map"
          ></div>

          <div v-else class="empty-course">
            저장된 코스 정보가 없습니다.
          </div>
        </section>

        <div class="bottom-actions">
          <button type="button" class="list-button" @click="goList">
            목록으로
          </button>
        </div>
      </article>

      <aside class="side-card">
        <div class="kicker">Preview</div>
        <h3>{{ post.title }}</h3>

        <div class="preview-tags">
          <span v-if="post.time">⏱ {{ post.time }}</span>
          <span v-if="post.district">⌖ {{ post.district }}</span>
          <span v-if="post.companion">♙ {{ post.companion }}와 함께</span>
        </div>

        <p class="preview-content">
          {{ post.content }}
        </p>

        <div class="preview-course">
          <h4>선택한 코스</h4>

          <div
            v-if="detailCourse.stops && detailCourse.stops.length"
            class="preview-cards"
          >
            <div
              v-for="(s, i) in detailCourse.stops"
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

          <div v-else class="preview-empty">
            저장된 코스 정보가 없습니다.
          </div>
        </div>

        <div class="preview-help">ⓘ 미리보기는 실제 게시글과 다를 수 있습니다.</div>
      </aside>
    </div>

    <div v-if="showPasswordModal" class="modal-backdrop">
      <div class="password-modal">
        <h2>게시글 비밀번호 확인</h2>
        <p>게시글 수정을 위해 작성 시 입력한 4자리 비밀번호를 입력해주세요.</p>

        <input
          :value="password"
          type="password"
          inputmode="numeric"
          maxlength="4"
          placeholder="4자리 숫자"
          @input="handlePasswordInput"
          @keyup.enter="verifyPassword"
        />

        <p v-if="passwordError" class="error-message">
          {{ passwordError }}
        </p>

        <div class="modal-actions">
          <button type="button" class="cancel-button" @click="closePasswordModal">
            취소
          </button>

          <button type="button" class="confirm-button" @click="verifyPassword">
            확인
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

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
  background: var(--ink, #111827);
  border: 2.5px solid #fff;
  transition: transform 0.2s ease;
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
  background: var(--route, #034ea1);
}

.pin:hover .head {
  transform: rotate(45deg) scale(1.1);
}

.hovercard {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #dbe2ec;
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
  color: #034ea1;
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
  color: #6b7280;
  margin-top: 4px;
  line-height: 1.5;
}

.hovercard .hc-foot {
  border-top: 1px solid #dbe2ec;
  padding: 8px 14px;
  font-size: 11px;
  color: #9ca3af;
}

.hovercard .hc-foot b {
  color: #111827;
  font-weight: 600;
}

#detailCourseMap .leaflet-tile-pane {
  filter: contrast(1.02) brightness(1.01);
}

#detailCourseMap.leaflet-container {
  font-family: 'Pretendard', sans-serif;
  background: #eef0f2;
}

#detailCourseMap .leaflet-popup-content-wrapper {
  background: transparent;
  box-shadow: none;
  padding: 0;
  border-radius: 14px;
}

#detailCourseMap .leaflet-popup-content {
  margin: 0;
  width: auto !important;
}

#detailCourseMap .leaflet-popup-tip {
  background: #fff;
  border: 1px solid #dbe2ec;
}

#detailCourseMap .leaflet-popup-close-button {
  display: none;
}

#detailCourseMap .leaflet-control-zoom {
  border: none !important;
  box-shadow: 0 6px 20px -10px rgba(14, 16, 19, 0.3) !important;
  margin: 14px !important;
}

#detailCourseMap .leaflet-control-zoom a {
  border-radius: 10px !important;
  color: #111827 !important;
  border: 1px solid #dbe2ec !important;
  background: #fff !important;
  width: 32px !important;
  height: 32px !important;
  line-height: 30px !important;
  font-size: 17px !important;
}

#detailCourseMap .leaflet-control-attribution {
  font-size: 10px !important;
  background: rgba(255, 255, 255, 0.7) !important;
}
</style>

<style scoped>
.detail-page {
  --main-color: #034ea1;
  max-width: 1220px;
  margin: 0 auto;
  padding: 40px 24px 90px;
  color: var(--ink, #111827);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
  color: #8a96a8;
  font-size: 13px;
}

.breadcrumb a {
  color: #6b7280;
  text-decoration: none;
}

.breadcrumb strong {
  color: #111827;
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 28px;
  align-items: start;
}

.detail-card,
.side-card {
  border: 1px solid #dbe2ec;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 18px 42px rgba(24, 42, 68, 0.05);
}

.detail-card {
  padding: 34px;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 22px;
}

.tag-row span {
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(3, 78, 161, 0.06);
  color: var(--main-color);
  font-size: 13px;
  font-weight: 800;
}

.title-row {
  display: flex;
  justify-content: space-between;
  gap: 24px;
}

.title-row h1 {
  margin: 0;
  color: #111827;
  font-size: 34px;
  font-weight: 850;
  line-height: 1.32;
  letter-spacing: -0.04em;
}

.edit-button {
  min-width: 74px;
  height: 44px;
  border: 0;
  border-radius: 10px;
  background: var(--main-color);
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 22px;
  margin-top: 24px;
  color: #6b7280;
  font-size: 14px;
}

.detail-card hr {
  margin: 30px 0;
  border: 0;
  border-top: 1px solid #e5e7eb;
}

.content {
  color: #1f2937;
  font-size: 16px;
  line-height: 2.1;
  white-space: pre-line;
}

.course-section h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 850;
}

.course-title-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.course-title-row p {
  margin: 0;
  color: var(--main-color);
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

.empty-course,
.preview-empty {
  padding: 24px;
  border: 1px dashed #dbe2ec;
  border-radius: 14px;
  color: #6b7280;
  text-align: center;
}

.bottom-actions {
  margin-top: 34px;
}

.list-button {
  height: 44px;
  padding: 0 22px;
  border: 1px solid #dbe2ec;
  border-radius: 10px;
  background: #fff;
  color: #111827;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}

.side-card {
  position: sticky;
  top: 84px;
  padding: 24px;
}

.side-card .kicker {
  font-family: 'Archivo', sans-serif;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--main-color);
  font-weight: 600;
  margin-bottom: 8px;
}

.side-card h3 {
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
  border: 1px solid #dbe2ec;
  border-radius: 999px;
  color: var(--main-color);
  font-size: 12px;
  font-weight: 600;
  background: rgba(3, 78, 161, 0.06);
}

.preview-content {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-line;
}

.preview-course {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #dbe2ec;
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
  border: 1px solid #dbe2ec;
  background: #fff;
}

.pv-card::before {
  content: "";
  position: absolute;
  left: 23px;
  top: -6px;
  height: 6px;
  width: 1.5px;
  background: #cbd5e1;
}

.pv-card:first-child::before {
  display: none;
}

.pv-idx {
  flex: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1.5px solid var(--main-color);
  color: var(--main-color);
  background: #fff;
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
  color: #111827;
}

.pv-cat {
  font-size: 10.5px;
  font-weight: 600;
  color: #9ca3af;
}

.pv-desc {
  font-size: 12.5px;
  color: #6b7280;
  margin-top: 4px;
  line-height: 1.5;
}

.pv-stay {
  font-size: 11.5px;
  color: #9ca3af;
  margin-top: 8px;
}

.pv-stay b {
  color: #6b7280;
  font-weight: 600;
}

.preview-help {
  margin-top: 18px;
  color: #9ca3af;
  font-size: 12px;
}

.loading-box,
.empty-box {
  padding: 80px;
  border: 1px dashed #dbe2ec;
  border-radius: 18px;
  text-align: center;
  color: #6b7280;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: rgba(17, 24, 39, 0.36);
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-modal {
  position: relative;
  z-index: 100000;
  width: 360px;
  padding: 28px;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18);
}

.password-modal h2 {
  margin: 0;
  color: #111827;
  font-size: 20px;
  font-weight: 850;
}

.password-modal p {
  margin: 12px 0 18px;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
}

.password-modal input {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  border: 1px solid #dbe2ec;
  border-radius: 10px;
  font-size: 15px;
  box-sizing: border-box;
  outline: none;
}

.password-modal input:focus {
  border-color: #034ea1;
  box-shadow: 0 0 0 3px rgba(3, 78, 161, 0.1);
}

.error-message {
  margin: 10px 0 0 !important;
  color: #dc2626 !important;
  font-size: 13px !important;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button,
.confirm-button {
  flex: 1;
  height: 42px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}

.cancel-button {
  border: 1px solid #dbe2ec;
  background: #fff;
  color: #111827;
}

.confirm-button {
  border: 0;
  background: #034ea1;
  color: #fff;
}

@media (max-width: 1000px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .side-card {
    position: static;
  }
}

@media (max-width: 720px) {
  .detail-page {
    padding: 34px 14px 70px;
  }

  .title-row {
    flex-direction: column;
  }

  .title-row h1 {
    font-size: 28px;
  }

  .course-map {
    height: 260px;
  }
}
</style>