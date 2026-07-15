<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const API_BASE_URL = 'http://127.0.0.1:8000'

const route = useRoute()
const router = useRouter()

const postId = computed(() => route.params.id)

const form = ref({
  title: '',
  content: '',
  password: '',
  time: '',
  district: '',
  companion: '',
})

const places = ref([])
const selectedPlaces = ref([])
const searchKeyword = ref('')
const draggedIndex = ref(null)

const districtOptions = ['강남구', '서초구', '송파구', '강동구', '관악구']
const companionOptions = ['혼자', '싸피 친구', '부모님', '프로님/강사님']

const filteredPlaces = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()

  return places.value.filter((place) => {
    const title = place.title?.toLowerCase() || ''
    const addr = place.addr1?.toLowerCase() || ''

    return !keyword || title.includes(keyword) || addr.includes(keyword)
  })
})

onMounted(async () => {
  const savedPassword = sessionStorage.getItem(`post-edit-password-${postId.value}`)

  if (!savedPassword) {
    alert('비밀번호 확인이 필요합니다.')
    router.push(`/posts/${postId.value}`)
    return
  }

  form.value.password = savedPassword

  await fetchPlaces()
  await fetchPost()
})

async function fetchPlaces() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/places?limit=100`)

    if (!response.ok) {
      throw new Error('장소 목록 조회 실패')
    }

    places.value = await response.json()
  } catch (error) {
    console.warn('장소 목록 API 연결 실패', error)

    places.value = [
      {
        id: 1,
        title: '멀티캠퍼스 역삼',
        addr1: '서울특별시 강남구 테헤란로 212',
        district: '강남구',
      },
      {
        id: 2,
        title: '코엑스 아쿠아리움',
        addr1: '서울 강남구 영동대로 513',
        district: '강남구',
      },
      {
        id: 3,
        title: '스타필드 코엑스',
        addr1: '서울 강남구 영동대로 513',
        district: '강남구',
      },
    ]
  }
}

async function fetchPost() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId.value}`)

    if (!response.ok) {
      throw new Error('게시글 조회 실패')
    }

    const data = await response.json()
    const post = data.post

    form.value.title = post.title
    form.value.content = post.content
    form.value.time = post.time || ''
    form.value.district = post.district || '강남구'
    form.value.companion = post.companion || '친구'

    selectedPlaces.value = post.places.map((place) => ({
      place_id: place.place_id,
      title: place.title,
      addr1: place.addr1,
      district: place.district,
      note: place.note || '',
    }))
  } catch (error) {
    console.warn('게시글 조회 실패', error)
  }
}

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
    note: '',
  })
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

  if (selectedPlaces.value.length === 0) {
    alert('코스 장소를 최소 1개 이상 선택해주세요.')
    return
  }

  const payload = {
    title: form.value.title,
    content: form.value.content,
    password: form.value.password,
    time: form.value.time,
    district: form.value.district,
    companion: form.value.companion,
    places: selectedPlaces.value.map((place, index) => ({
      place_id: place.place_id,
      seq: index + 1,
      note: place.note,
    })),
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error('게시글 수정 실패')
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
      throw new Error('게시글 삭제 실패')
    }

    alert('게시글이 삭제되었습니다.')
    sessionStorage.removeItem(`post-edit-password-${postId.value}`)
    router.push('/posts')
  } catch (error) {
    console.error(error)
    alert('게시글 삭제 중 오류가 발생했습니다.')
  }
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
      <p>게시글 정보를 수정하고 최신 정보를 반영해보세요.</p>
    </div>

    <div class="edit-layout">
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
        </section>

        <section class="card">
          <div class="section-title">
            <div>
              <h2>코스 장소 선택</h2>
              <p>코스로 추가할 장소를 검색하여 선택하세요.</p>
            </div>

            <button type="button" class="add-place-button">
              + 장소 추가
            </button>
          </div>

          <div class="search-row">
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="장소명, 카테고리, 지역으로 검색하세요"
            />
            <button type="button">검색</button>
          </div>

          <div class="place-grid">
            <button
              v-for="place in filteredPlaces.slice(0, 6)"
              :key="place.id"
              type="button"
              class="place-choice"
              :class="{ selected: isSelected(place.id) }"
              @click="togglePlace(place)"
            >
              <strong>{{ place.title }}</strong>
              <small>{{ place.addr1 }}</small>
            </button>
          </div>

          <div class="selected-title">
            <h3>선택한 코스 ({{ selectedPlaces.length }}/10)</h3>
            <p>드래그하여 순서를 변경할 수 있습니다.</p>
          </div>

          <div class="selected-list">
            <div
              v-for="(place, index) in selectedPlaces"
              :key="place.place_id"
              class="selected-item"
              draggable="true"
              @dragstart="onDragStart(index)"
              @dragover="onDragOver"
              @drop="onDrop(index)"
              @dragend="onDragEnd"
            >
              <div class="drag-handle">⋮⋮</div>
              <span class="seq">{{ index + 1 }}</span>

              <div class="place-info">
                <strong>{{ place.title }}</strong>
                <small>{{ place.addr1 }}</small>
              </div>

              <input
                v-model="place.note"
                type="text"
                placeholder="메모를 입력하세요"
              />

              <button type="button" class="remove-button" @click="removeSelectedPlace(place.place_id)">
                ×
              </button>
            </div>
          </div>
        </section>

        <div class="action-row">
          <button type="button" class="cancel-button" @click="router.push(`/posts/${postId}`)">
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
        <h2>미리보기</h2>
        <p>수정 내용이 반영된 게시글 미리보기입니다.</p>

        <div class="preview-tags">
          <span>{{ form.time || '시간 미입력' }}</span>
          <span>{{ form.district }}</span>
          <span>{{ form.companion }}</span>
        </div>

        <h3>{{ form.title }}</h3>

        <div class="preview-meta">
          <span>{{ form.time || '시간 미입력' }}</span>
          <span>{{ form.companion }} 여행중</span>
          <span>조회 {{ 0 }}</span>
        </div>

        <div class="preview-content">
          {{ form.content }}
        </div>

        <h4>추천 코스</h4>

        <div class="preview-course-list">
          <div
            v-for="(place, index) in selectedPlaces"
            :key="place.place_id"
            class="preview-course"
          >
            <span>{{ index + 1 }}</span>
            <div>
              <strong>{{ place.title }}</strong>
              <small>{{ place.note || '장소 메모 없음' }}</small>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>

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

.edit-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 350px;
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
.field textarea,
.search-row input,
.selected-item input {
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

.field input,
.field select,
.search-row input,
.selected-item input {
  height: 42px;
  padding: 0 13px;
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

.add-place-button,
.search-row button {
  height: 42px;
  border: 1px solid var(--main-color);
  border-radius: 10px;
  background: #fff;
  color: var(--main-color);
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 16px;
}

.section-title h2 {
  margin: 0;
}

.section-title p {
  margin: 8px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.search-row {
  display: grid;
  grid-template-columns: 1fr 76px;
  gap: 10px;
  margin-bottom: 14px;
}

.place-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 9px;
  margin-bottom: 18px;
}

.place-choice {
  padding: 12px;
  border: 1px solid #dbe2ec;
  border-radius: 12px;
  background: #fff;
  text-align: left;
  cursor: pointer;
}

.place-choice.selected {
  border-color: var(--main-color);
  background: rgba(3, 78, 161, 0.05);
}

.place-choice strong {
  display: block;
  font-size: 13px;
}

.place-choice small {
  display: block;
  margin-top: 6px;
  color: #6b7280;
  font-size: 11px;
  line-height: 1.4;
}

.selected-title {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 10px;
}

.selected-title h3 {
  margin: 0;
  font-size: 15px;
}

.selected-title p {
  margin: 0;
  color: #6b7280;
  font-size: 12px;
}

.selected-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-item {
  display: grid;
  grid-template-columns: 24px 30px 1fr 280px 30px;
  gap: 10px;
  align-items: center;
  padding: 10px;
  border: 1px solid #dbe2ec;
  border-radius: 12px;
}

.drag-handle {
  color: #8a96a8;
  cursor: grab;
  letter-spacing: -4px;
}

.seq {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--main-color);
  color: #fff;
  font-size: 12px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}

.place-info strong {
  display: block;
  font-size: 13px;
}

.place-info small {
  display: block;
  margin-top: 3px;
  color: #6b7280;
  font-size: 11px;
}

.remove-button {
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 50%;
  background: rgba(3, 78, 161, 0.08);
  color: var(--main-color);
  font-size: 18px;
  cursor: pointer;
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

.preview-panel > p {
  margin: -8px 0 18px;
  color: #6b7280;
  font-size: 13px;
}

.preview-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.preview-tags span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(3, 78, 161, 0.06);
  color: var(--main-color);
  font-size: 12px;
  font-weight: 800;
}

.preview-panel h3 {
  margin: 0 0 12px;
  font-size: 22px;
  line-height: 1.4;
}

.preview-meta {
  display: flex;
  gap: 12px;
  color: #6b7280;
  font-size: 12px;
}

.preview-content {
  margin: 18px 0 26px;
  color: #374151;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-line;
}

.preview-panel h4 {
  margin: 0 0 14px;
  font-size: 16px;
}

.preview-course-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-course {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 10px;
}

.preview-course span {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--main-color);
  color: #fff;
  font-size: 12px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-course strong {
  display: block;
  font-size: 14px;
}

.preview-course small {
  display: block;
  margin-top: 4px;
  color: #6b7280;
  font-size: 12px;
}

@media (max-width: 1050px) {
  .edit-layout {
    grid-template-columns: 1fr;
  }

  .preview-panel {
    position: static;
  }

  .error-message {
    grid-column: auto;
  }
}

@media (max-width: 720px) {
  .edit-page {
    padding: 28px 14px 70px;
  }

  .row,
  .three-columns,
  .place-grid {
    grid-template-columns: 1fr;
  }
  .selected-item {
    grid-template-columns: 24px 30px 1fr 30px;
  }

  .selected-item input {
    grid-column: 3 / 5;
  }

  .action-row {
    flex-direction: column;
  }

  .right-actions {
    flex-direction: column;
  }
}
</style>