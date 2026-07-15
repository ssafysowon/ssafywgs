<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

// AltHeader removed; use global header from App.vue

const router = useRouter()

const API_BASE_URL = 'http://127.0.0.1:8000'

const MAIN_COLOR = '#034ea1'

const form = ref({
  title: '',
  content: '',
  password: '',
  time: '',
  district: '강남구',
  companion: '혼자',
})

const districtOptions = ['강남구', '서초구', '송파구', '강동구', '관악구']
const companionOptions = ['혼자', '싸피 친구', '부모님', '프로님/강사님']

const prefill = window.history.state?.prefill || {}

console.log('받은 prefill:', prefill)
console.log('받은 companion:', prefill.companion)
console.log('companionOptions:', companionOptions)

if (prefill.time) {
  form.value.time = prefill.time
}

if (prefill.district) {
  form.value.district = prefill.district
}

if (prefill.companion) {
  form.value.companion = prefill.companion
}

// Apply prefill from navigation state (if coming from CourseResult)
const incoming = (window?.history?.state?.prefill) || {}
if (incoming.district) form.value.district = incoming.district
if (incoming.companion) form.value.companion = incoming.companion
if (incoming.title) form.value.title = incoming.title
if (incoming.content) form.value.content = incoming.content

const searchKeyword = ref('')
const places = ref([])
const selectedPlaces = ref([])
const draggedIndex = ref(null)



const fallbackPlaces = [
  {
    id: 1,
    title: '멀티캠퍼스 역삼',
    addr1: '서울 강남구 테헤란로 146 멀티캠퍼스',
    district: '강남구',
  },
  {
    id: 2,
    title: '선정릉',
    addr1: '서울 강남구 선릉로100길 1',
    district: '강남구',
  },
  {
    id: 3,
    title: '코엑스',
    addr1: '서울 강남구 영동대로 513',
    district: '강남구',
  },
  {
    id: 4,
    title: '봉은사',
    addr1: '서울 강남구 봉은사로 531',
    district: '강남구',
  },
  {
    id: 5,
    title: '서울숲',
    addr1: '서울 성동구 뚝섬로 273',
    district: '성동구',
  },
]

const filteredPlaces = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()

  return places.value.filter((place) => {
    const title = place.title?.toLowerCase() || ''
    const addr = place.addr1?.toLowerCase() || ''

    const matchesKeyword =
      !keyword ||
      title.includes(keyword) ||
      addr.includes(keyword)

    return matchesKeyword
  })
})

const previewContent = computed(() => {
  return (
    form.value.content ||
    '작성한 본문 내용이 이곳에 미리 표시됩니다.'
  )
})

onMounted(async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/places?limit=100`)

    if (!response.ok) {
      throw new Error('관광지 목록 API 응답 실패')
    }

    const data = await response.json()

    places.value = data.length > 0 ? data : fallbackPlaces
  } catch (error) {
    console.warn('관광지 API 연결 전이므로 예시 데이터를 사용합니다.', error)
    places.value = fallbackPlaces
  }
})

function isSelected(placeId) {
  return selectedPlaces.value.some((place) => place.place_id === placeId)
}

function togglePlace(place) {
  const index = selectedPlaces.value.findIndex(
    (selected) => selected.place_id === place.id
  )

  if (index >= 0) {
    selectedPlaces.value.splice(index, 1)
    return
  }

  selectedPlaces.value.push({
    place_id: place.id,
    title: place.title,
    addr1: place.addr1,
    district: place.district,
    note: getDefaultNote(place.title),
  })
}

function getDefaultNote(title) {
  const noteMap = {
    '멀티캠퍼스 역삼': '의외로 주변에 맛집과 카페가 많아요!',
    선정릉: '도심 속에서 조용히 산책하기 좋아요.',
    코엑스: '전시도 보고 쇼핑도 즐길 수 있어요!',
    봉은사: '조용한 분위기에서 마음이 차분해져요.',
    서울숲: '산책하면서 쉬기 좋은 장소예요.',
  }

  return noteMap[title] || ''
}

function removeSelectedPlace(placeId) {
  selectedPlaces.value = selectedPlaces.value.filter(
    (place) => place.place_id !== placeId
  )
}

function onDragStart(index) {
  draggedIndex.value = index
}

function onDragOver(event) {
  event.preventDefault()
}

function onDrop(dropIndex) {
  if (draggedIndex.value === null) return
  if (draggedIndex.value === dropIndex) return

  const copiedList = [...selectedPlaces.value]
  const draggedItem = copiedList.splice(draggedIndex.value, 1)[0]

  copiedList.splice(dropIndex, 0, draggedItem)

  selectedPlaces.value = copiedList
  draggedIndex.value = null
}

function onDragEnd() {
  draggedIndex.value = null
}

function handlePasswordInput(event) {
  const onlyNumber = event.target.value.replace(/[^0-9]/g, '').slice(0, 4)
  form.value.password = onlyNumber
}

async function submitPost() {
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

  if (selectedPlaces.value.length === 0) {
    alert('코스 장소를 최소 1개 이상 선택해주세요.')
    return
  }

  console.log('selectedPlaces:', selectedPlaces.value)

  const payload = {
    title: form.value.title,
    content: form.value.content,
    password: form.value.password,
    time: form.value.time,
    companion: form.value.companion,
    district: form.value.district,
    place_ids: selectedPlaces.value.map((place) => place.place_id),
  }

  console.log('게시글 작성 payload:', payload)
  
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
  <section class="post-create-page" :style="{ '--main-color': MAIN_COLOR }">
    <div class="page-header">
      <h1>나만의 코스를 공유해보세요</h1>
      <p>
        멀티캠퍼스 역삼 주변을 중심으로 나만의 이동 경로와 리뷰를 공유해보세요.
      </p>
    </div>

    <div class="page-layout">
      <form class="form-column" @submit.prevent="submitPost">
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

          <div class="row three-columns">
            <div class="field">
              <label for="time">시간</label>
              <input
                id="time"
                v-model="form.time"
                type="text"
                placeholder="예: 2시간, 반나절, 오후 1시~4시"
              />
            </div>

            <div class="field">
              <label for="district">주요 지역</label>
              <select id="district" v-model="form.district">
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
              <label for="companion">동행 유형</label>
              <select id="companion" v-model="form.companion">
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

        <section class="card">
          <div class="section-title">
            <h2>코스 장소 선택</h2>
            <p>선택한 장소는 아래 선택한 코스에 자동으로 추가됩니다.</p>
          </div>

          <div class="search-box">
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="장소명 또는 키워드로 검색하세요"
            />
            <span>⌕</span>
          </div>

          <div class="place-grid">
            <button
              v-for="place in filteredPlaces.slice(0, 10)"
              :key="place.id"
              type="button"
              class="place-card"
              :class="{ selected: isSelected(place.id) }"
              @click="togglePlace(place)"
            >
              <div class="place-top">
                <strong>⌖ {{ place.title }}</strong>
                <span class="check">
                  {{ isSelected(place.id) ? '✓' : '' }}
                </span>
              </div>
              <p>{{ place.addr1 || '주소 정보 없음' }}</p>
            </button>
          </div>
        </section>

        <section class="card">
          <div class="course-title-row">
            <h2>선택한 코스</h2>
            <p>☷ 드래그해서 순서를 변경하세요</p>
          </div>

          <div v-if="selectedPlaces.length === 0" class="empty-course">
            아직 선택한 장소가 없습니다.
            위의 장소 카드를 선택하면 이곳에 코스가 추가됩니다.
          </div>

          <div v-else class="selected-course-list">
            <div
              v-for="(place, index) in selectedPlaces"
              :key="place.place_id"
              class="selected-course-item"
              draggable="true"
              :class="{ dragging: draggedIndex === index }"
              @dragstart="onDragStart(index)"
              @dragover="onDragOver"
              @drop="onDrop(index)"
              @dragend="onDragEnd"
            >
              <div class="seq">{{ index + 1 }}</div>

              <div class="selected-info">
                <strong>⌖ {{ place.title }}</strong>
                <small>{{ place.addr1 }}</small>
              </div>

              <input
                v-model="place.note"
                type="text"
                placeholder="장소별 메모를 입력하세요"
              />

              <button
                type="button"
                class="remove-button"
                @click="removeSelectedPlace(place.place_id)"
              >
                ×
              </button>

              <div class="drag-handle">⋮⋮</div>
            </div>
          </div>
        </section>

        <div class="button-row">
          <button type="button" class="cancel-button" @click="router.push('/posts')">
            취소
          </button>
          <button type="submit" class="submit-button">
            게시글 작성하기
          </button>
        </div>
      </form>

      <aside class="preview-panel">
        <h2>미리보기</h2>

        <h3>
          {{ form.title || '게시글 제목이 표시됩니다' }}
        </h3>

        <div class="preview-tags">
          <span>⏱ {{ form.time || '시간 미입력' }}</span>
          <span>⌖ {{ form.district || '지역 미선택' }}</span>
          <span>♙ {{ form.companion || '동행 미선택' }}와 함께</span>
        </div>

        <p class="preview-content">
          {{ previewContent }}
        </p>

        <div class="preview-course">
          <h4>선택한 코스</h4>

          <div v-if="selectedPlaces.length === 0" class="preview-empty">
            선택한 장소가 없습니다.
          </div>

          <div
            v-for="(place, index) in selectedPlaces"
            :key="place.place_id"
            class="preview-course-item"
          >
            <div class="preview-seq">{{ index + 1 }}</div>
            <div>
              <strong>{{ place.title }}</strong>
              <small>{{ place.addr1 }}</small>
              <p>{{ place.note || '장소 메모 없음' }}</p>
            </div>
          </div>
        </div>

        <div class="preview-help">
          ⓘ 미리보기는 실제 게시글과 다를 수 있습니다.
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.post-create-page {
  max-width: 1220px;
  margin: 0 auto;
  padding: 52px 24px 90px;
  color: var(--ink);
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  font-size: 38px;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.page-header p {
  margin: 12px 0 0;
  font-size: 15px;
  color: var(--ink);
  opacity: 0.58;
}

.page-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 24px;
  align-items: start;
}

.form-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card,
.preview-panel {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--paper);
  box-shadow: 0 18px 42px rgba(24, 42, 68, 0.05);
}

.card {
  padding: 22px;
}

.card h2,
.preview-panel h2 {
  margin: 0 0 18px;
  font-size: 18px;
  font-weight: 800;
}

.section-title {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-title h2 {
  margin: 0;
}

.section-title p {
  margin: 0;
  font-size: 12px;
  color: var(--main-color);
  opacity: 0.8;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.three-columns {
  grid-template-columns: 1fr 1fr 1fr;
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
.field select,
.field textarea,
.search-box input,
.selected-course-item input {
  width: 100%;
  border: 1px solid #d8dee8;
  border-radius: 10px;
  background: #fff;
  color: var(--ink);
  font-family: inherit;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.field input,
.field select,
.search-box input {
  height: 42px;
  padding: 0 13px;
}

.field textarea {
  padding: 13px;
  line-height: 1.6;
  resize: vertical;
}

.field input:focus,
.field select:focus,
.field textarea:focus,
.search-box input:focus,
.selected-course-item input:focus {
  border-color: var(--main-color);
  box-shadow: 0 0 0 3px rgba(3, 78, 161, 0.1);
}

.textarea-box {
  position: relative;
}

.textarea-box span {
  position: absolute;
  right: 12px;
  bottom: 10px;
  font-size: 12px;
  color: var(--ink);
  opacity: 0.45;
}

.password-field p {
  margin: 7px 0 0;
  font-size: 12px;
  color: var(--main-color);
}

.search-box {
  position: relative;
  max-width: 420px;
  margin-bottom: 16px;
}

.search-box span {
  position: absolute;
  right: 13px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--main-color);
  font-weight: 700;
}

.place-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.place-card {
  min-height: 86px;
  padding: 13px;
  border: 1px solid #d8dee8;
  border-radius: 13px;
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition: 0.18s ease;
}

.place-card:hover {
  transform: translateY(-2px);
  border-color: var(--main-color);
}

.place-card.selected {
  border-color: var(--main-color);
  background: rgba(3, 78, 161, 0.045);
}

.place-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.place-card strong {
  color: var(--main-color);
  font-size: 13px;
}

.place-card p {
  margin: 8px 0 0;
  color: var(--ink);
  font-size: 12px;
  line-height: 1.4;
  opacity: 0.58;
}

.check {
  width: 20px;
  height: 20px;
  flex: 0 0 20px;
  border: 1px solid #cbd4e1;
  border-radius: 50%;
  color: #fff;
  background: #fff;
  font-size: 12px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.place-card.selected .check {
  border-color: var(--main-color);
  background: var(--main-color);
}

.course-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.course-title-row h2 {
  margin: 0;
}

.course-title-row p {
  margin: 0;
  color: var(--main-color);
  font-size: 12px;
  font-weight: 700;
  opacity: 0.75;
}

.empty-course {
  padding: 32px;
  border: 1px dashed #cbd4e1;
  border-radius: 14px;
  color: var(--ink);
  font-size: 14px;
  text-align: center;
  line-height: 1.6;
  opacity: 0.55;
}

.selected-course-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-course-item {
  display: grid;
  grid-template-columns: 32px minmax(150px, 1fr) minmax(220px, 1.2fr) 32px 28px;
  gap: 12px;
  align-items: center;
  padding: 11px 12px;
  border: 1px solid #d8dee8;
  border-radius: 13px;
  background: #fff;
  transition: 0.18s ease;
}

.selected-course-item:hover {
  border-color: var(--main-color);
  box-shadow: 0 8px 18px rgba(3, 78, 161, 0.08);
}

.selected-course-item.dragging {
  opacity: 0.45;
}

.seq,
.preview-seq {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--main-color);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
}

.selected-info strong {
  display: block;
  color: var(--ink);
  font-size: 13px;
}

.selected-info small {
  display: block;
  margin-top: 3px;
  color: var(--ink);
  font-size: 11px;
  opacity: 0.5;
}

.selected-course-item input {
  height: 38px;
  padding: 0 12px;
}

.remove-button {
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 50%;
  background: rgba(3, 78, 161, 0.08);
  color: var(--main-color);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
}

.drag-handle {
  color: var(--ink);
  opacity: 0.35;
  font-size: 18px;
  cursor: grab;
  user-select: none;
  letter-spacing: -4px;
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
  height: 54px;
  border-radius: 13px;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
}

.cancel-button {
  border: 1px solid var(--main-color);
  background: #fff;
  color: var(--main-color);
}

.submit-button {
  border: 0;
  background: var(--main-color);
  color: #fff;
  box-shadow: 0 12px 28px rgba(3, 78, 161, 0.22);
}

.preview-panel {
  position: sticky;
  top: 84px;
  padding: 24px;
}

.preview-panel h3 {
  margin: 10px 0 16px;
  font-size: 23px;
  line-height: 1.35;
  letter-spacing: -0.03em;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}

.preview-tags span {
  padding: 7px 11px;
  border: 1px solid #d8dee8;
  border-radius: 999px;
  color: var(--main-color);
  font-size: 12px;
  font-weight: 700;
  background: rgba(3, 78, 161, 0.035);
}

.preview-content {
  margin: 0;
  color: var(--ink);
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-line;
  opacity: 0.78;
}

.preview-course {
  margin-top: 26px;
}

.preview-course h4 {
  margin: 0 0 14px;
  font-size: 15px;
  font-weight: 800;
}

.preview-empty {
  padding: 20px;
  border: 1px dashed #cbd4e1;
  border-radius: 12px;
  font-size: 13px;
  opacity: 0.5;
  text-align: center;
}

.preview-course-item {
  position: relative;
  display: grid;
  grid-template-columns: 30px 1fr;
  gap: 12px;
  padding-bottom: 18px;
}

.preview-course-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 14px;
  top: 30px;
  width: 1px;
  height: calc(100% - 18px);
  border-left: 1px dashed rgba(3, 78, 161, 0.35);
}

.preview-course-item strong {
  display: block;
  color: var(--ink);
  font-size: 14px;
}

.preview-course-item small {
  display: block;
  margin-top: 3px;
  color: var(--ink);
  font-size: 11px;
  opacity: 0.5;
}

.preview-course-item p {
  margin: 9px 0 0;
  padding: 10px 12px;
  border: 1px solid #d8dee8;
  border-radius: 10px;
  background: rgba(3, 78, 161, 0.035);
  color: var(--ink);
  font-size: 12px;
  opacity: 0.78;
}

.preview-help {
  margin-top: 12px;
  color: var(--main-color);
  font-size: 12px;
  opacity: 0.72;
}

@media (max-width: 1100px) {
  .page-layout {
    grid-template-columns: 1fr;
  }

  .preview-panel {
    position: static;
  }

  .place-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 720px) {
  .post-create-page {
    padding: 34px 14px 70px;
  }

  .page-header h1 {
    font-size: 30px;
  }

  .row,
  .three-columns {
    grid-template-columns: 1fr;
  }

  .place-grid {
    grid-template-columns: 1fr;
  }

  .selected-course-item {
    grid-template-columns: 32px 1fr 28px;
  }

  .selected-course-item input {
    grid-column: 2 / 4;
  }

  .drag-handle {
    grid-column: 3;
    grid-row: 1;
  }

  .button-row {
    grid-template-columns: 1fr;
  }
}
</style>