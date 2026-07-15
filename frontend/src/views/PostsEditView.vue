<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const API_BASE_URL = 'https://ssafyescape.onrender.com'

const route = useRoute()
const router = useRouter()

const postId = computed(() => route.params.id)

const post = ref(null)
const loading = ref(false)

const form = ref({
  title: '',
  content: '',
  password: '',
  time: '',
  district: '',
  companion: '',
})

let map = null
let markers = []
let layersGroup = null

const districtOptions = ['강남구', '서초구', '송파구', '강동구', '관악구']
const companionOptions = ['혼자', '싸피 친구', '부모님', '프로님/강사님']

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

const previewContent = computed(() => {
  return form.value.content || '작성한 본문 내용이 이곳에 미리 표시됩니다.'
})

onMounted(async () => {
  const savedPassword = sessionStorage.getItem(`post-edit-password-${postId.value}`)

  if (!savedPassword) {
    alert('비밀번호 확인이 필요합니다.')
    router.push(`/posts/${postId.value}`)
    return
  }

  form.value.password = savedPassword
  await fetchPost()
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }

  markers = []
  layersGroup = null
})

async function fetchPost() {
  loading.value = true

  try {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId.value}`)

    if (!response.ok) {
      throw new Error('게시글 조회 실패')
    }

    const data = await response.json()
    post.value = data.post

    form.value.title = post.value.title || ''
    form.value.content = post.value.content || ''
    form.value.time = post.value.time || ''
    form.value.district = post.value.district || ''
    form.value.companion = post.value.companion || ''
  } catch (error) {
    console.warn('게시글 조회 실패', error)
    alert('게시글을 불러오지 못했습니다.')
    router.push('/posts')
    return
  } finally {
    loading.value = false
  }

  await nextTick()

  if (post.value) {
    try {
      initDetailMap()
    } catch (mapError) {
      console.error('수정 페이지 지도 렌더링 실패:', mapError)
    }
  }
}

function handlePasswordInput(event) {
  form.value.password = event.target.value.replace(/[^0-9]/g, '').slice(0, 4)
}

async function submitEdit() {
  if (!form.value.title.trim()) {
    alert('제목을 입력해주세요.')
    return
  }

  if (!form.value.time.trim()) {
    alert('시간을 입력해주세요.')
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

  const payload = {
    title: form.value.title,
    content: form.value.content,
    password: form.value.password,
    time: form.value.time,
    district: form.value.district,
    companion: form.value.companion,

    // 현재 코스는 course_json에 저장된 데이터를 상세/수정 화면에서 그대로 보여주는 구조라
    // post_places 수정은 사용하지 않는다.
    places: [],
  }

  console.log('게시글 수정 payload:', payload)

  try {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error('게시글 수정 실패 상세:', errorData)
      alert(errorData.detail ? JSON.stringify(errorData.detail, null, 2) : '게시글 수정 실패')
      return
    }

    alert('게시글이 수정되었습니다.')
    router.push(`/posts/${postId.value}`)
  } catch (error) {
    console.error(error)
    alert('게시글 수정 중 오류가 발생했습니다.')
  }
}

async function deletePost() {
  const confirmed = confirm('정말 이 게시글을 삭제하시겠습니까? 삭제 후에는 복구할 수 없습니다.')

  if (!confirmed) return

  try {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId.value}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        password: form.value.password,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error('게시글 삭제 실패 상세:', errorData)
      alert(errorData.detail || '게시글 삭제 실패')
      return
    }

    alert('게시글이 삭제되었습니다.')
    sessionStorage.removeItem(`post-edit-password-${postId.value}`)
    router.push('/posts')
  } catch (error) {
    console.error(error)
    alert('게시글 삭제 중 오류가 발생했습니다.')
  }
}

function cancelEdit() {
  router.push(`/posts/${postId.value}`)
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

  const mapContainer = document.getElementById('editCourseMap')

  if (!mapContainer) {
    console.warn('editCourseMap 요소가 아직 없습니다.')
    return
  }

  if (map) {
    map.remove()
    map = null
  }

  map = L.map('editCourseMap', {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView([course.start.lat, course.start.lng], 15)

  L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', {
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
  <section class="edit-page">
    <div class="breadcrumb">
      <router-link to="/">홈</router-link>
      <span>›</span>
      <router-link to="/posts">공유 게시판</router-link>
      <span>›</span>
      <strong>게시글 수정</strong>
    </div>

    <div class="page-head">
      <h1>게시글 수정</h1>
      <p>게시글의 제목, 본문, 시간, 지역, 동행 정보를 수정할 수 있습니다.</p>
    </div>

    <div v-if="loading" class="loading-box">
      게시글을 불러오는 중입니다.
    </div>

    <div v-else-if="!post" class="empty-box">
      게시글을 찾을 수 없습니다.
    </div>

    <div v-else class="edit-layout">
      <form class="edit-form" @submit.prevent="submitEdit">
        <section class="card">
          <h2>기본 정보</h2>

          <div class="field">
            <label>제목 <span>*</span></label>
            <input v-model="form.title" type="text" />
          </div>

          <div class="row three-columns">
            <div class="field">
              <label>시간 <span>*</span></label>
              <input
                v-model="form.time"
                type="text"
                placeholder="예: 2시간, 반나절, 오후 1시~4시"
              />
            </div>

            <div class="field">
              <label>주요 지역 <span>*</span></label>
              <select v-model="form.district">
                <option
                  v-for="district in districtOptions"
                  :key="district"
                  :value="district"
                >
                  {{ district }}
                </option>
              </select>
            </div>

            <div class="field">
              <label>동행 유형 <span>*</span></label>
              <select v-model="form.companion">
                <option
                  v-for="companion in companionOptions"
                  :key="companion"
                  :value="companion"
                >
                  {{ companion }}
                </option>
              </select>
            </div>

          </div>

          <div class="field">
            <label>본문 <span>*</span></label>
            <div class="textarea-box">
              <textarea
                v-model="form.content"
                maxlength="1000"
                rows="7"
              ></textarea>
              <span>{{ form.content.length }} / 1000</span>
            </div>
          </div>

          <div class="field password-field">
            <label>수정/삭제용 비밀번호 <span>*</span></label>
            <input
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

        <section class="card">
          <div class="course-title-row">
            <h2>선택한 코스</h2>
            <p>{{ detailCourse.title }} · {{ detailCourse.totalTime }}</p>
          </div>

          <div
            v-if="detailCourse.stops && detailCourse.stops.length"
            id="editCourseMap"
            class="course-map"
          ></div>

          <div v-else class="empty-course">
            저장된 코스 정보가 없습니다.
          </div>
        </section>

        <div class="action-row">
          <button type="button" class="cancel-button" @click="cancelEdit">
            취소
          </button>

          <div class="right-actions">
            <button type="button" class="delete-button" @click="deletePost">
              삭제
            </button>

            <button type="submit" class="submit-button">
              수정 완료
            </button>
          </div>
        </div>
      </form>

      <aside class="preview-panel">
        <div class="kicker">Preview</div>
        <h3>{{ form.title || '게시글 제목이 표시됩니다' }}</h3>

        <div class="preview-tags">
          <span>⏱ {{ form.time || '시간 미입력' }}</span>
          <span>⌖ {{ form.district || '지역 미입력' }}</span>
          <span>♙ {{ form.companion || '동행 미입력' }}와 함께</span>
        </div>

        <p class="preview-content">
          {{ previewContent }}
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

#editCourseMap .leaflet-tile-pane {
  filter: contrast(1.02) brightness(1.01);
}

#editCourseMap.leaflet-container {
  font-family: 'Pretendard', sans-serif;
  background: #eef0f2;
}

#editCourseMap .leaflet-popup-content-wrapper {
  background: transparent;
  box-shadow: none;
  padding: 0;
  border-radius: 14px;
}

#editCourseMap .leaflet-popup-content {
  margin: 0;
  width: auto !important;
}

#editCourseMap .leaflet-popup-tip {
  background: #fff;
  border: 1px solid #dbe2ec;
}

#editCourseMap .leaflet-popup-close-button {
  display: none;
}

#editCourseMap .leaflet-control-zoom {
  border: none !important;
  box-shadow: 0 6px 20px -10px rgba(14, 16, 19, 0.3) !important;
  margin: 14px !important;
}

#editCourseMap .leaflet-control-zoom a {
  border-radius: 10px !important;
  color: #111827 !important;
  border: 1px solid #dbe2ec !important;
  background: #fff !important;
  width: 32px !important;
  height: 32px !important;
  line-height: 30px !important;
  font-size: 17px !important;
}

#editCourseMap .leaflet-control-attribution {
  font-size: 10px !important;
  background: rgba(255, 255, 255, 0.7) !important;
}
</style>

<style scoped>
.edit-page {
  --main-color: #034ea1;
  max-width: 1220px;
  margin: 0 auto;
  padding: 40px 24px 90px;
  color: var(--ink, #111827);
}

.breadcrumb {
  display: flex;
  gap: 10px;
  margin-bottom: 26px;
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

.page-head {
  margin-bottom: 24px;
}

.page-head h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 850;
}

.page-head p {
  margin: 10px 0 0;
  color: #6b7280;
  font-size: 14px;
}

.loading-box,
.empty-box {
  padding: 80px;
  border: 1px dashed #dbe2ec;
  border-radius: 18px;
  text-align: center;
  color: #6b7280;
}

.edit-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 28px;
  align-items: start;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card,
.preview-panel {
  border: 1px solid #dbe2ec;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 18px 42px rgba(24, 42, 68, 0.05);
}

.card {
  padding: 22px;
}

.card h2,
.preview-panel h2 {
  margin: 0 0 18px;
  font-size: 18px;
  font-weight: 850;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 18px;
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
  font-weight: 800;
}

.field label span {
  color: #dc2626;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  border: 1px solid #dbe2ec;
  border-radius: 10px;
  background: #fff;
  color: #111827;
  font-size: 14px;
  font-family: inherit;
  box-sizing: border-box;
  outline: none;
}

.field input {
  height: 42px;
  padding: 0 13px;
}

.field select {
  height: 42px;
  padding: 0 40px 0 13px;
  border: 1px solid #dbe2ec;
  border-radius: 10px;
  background-color: #fff;
  color: #111827;
  font-size: 14px;
  font-family: inherit;
  box-sizing: border-box;
  outline: none;
  cursor: pointer;

  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;

  background-image: url("data:image/svg+xml,%3Csvg width='14' height='14' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M6 9L12 15L18 9' stroke='%23111827' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 14px;
}

.field textarea {
  padding: 13px;
  line-height: 1.7;
  resize: vertical;
}

.textarea-box {
  position: relative;
}

.textarea-box span {
  position: absolute;
  right: 12px;
  bottom: 10px;
  color: #8a96a8;
  font-size: 12px;
}

.password-field p {
  margin: 7px 0 0;
  font-size: 12px;
  color: #8a96a8;
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

.action-row {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  margin-top: 10px;
}

.right-actions {
  display: flex;
  gap: 12px;
}

.cancel-button,
.delete-button,
.submit-button {
  height: 46px;
  padding: 0 28px;
  border-radius: 11px;
  font-size: 14px;
  font-weight: 850;
  cursor: pointer;
}

.cancel-button {
  border: 1px solid #dbe2ec;
  background: #fff;
  color: #111827;
}

.delete-button {
  border: 1px solid #dc2626;
  background: #fff;
  color: #dc2626;
}

.submit-button {
  border: 0;
  background: var(--main-color);
  color: #fff;
}

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
  color: var(--main-color);
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

@media (max-width: 1050px) {
  .edit-layout {
    grid-template-columns: 1fr;
  }

  .preview-panel {
    position: static;
  }
}

@media (max-width: 720px) {
  .edit-page {
    padding: 28px 14px 70px;
  }

  .row,
  .three-columns {
    grid-template-columns: 1fr;
  }

  .action-row {
    flex-direction: column;
  }

  .right-actions {
    flex-direction: column;
  }
}
</style>