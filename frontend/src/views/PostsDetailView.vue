<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const API_BASE_URL = 'http://127.0.0.1:8000'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(false)

const showPasswordModal = ref(false)
const password = ref('')
const passwordError = ref('')

onMounted(() => {
  fetchPostDetail()
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
          <span>장소 {{ post.place_count || post.places?.length || 0 }}개</span>
        </div>

        <hr />

        <p class="content">
          {{ post.content }}
        </p>

        <hr />

        <section class="course-section">
          <h2>추천 코스</h2>

          <div class="course-list">
            <template
              v-for="(place, index) in post.places"
              :key="place.seq || place.place_id || index"
            >
              <div class="course-card">
                <div class="course-head">
                  <span>{{ index + 1 }}</span>
                  <strong>{{ place.title }}</strong>
                </div>
                <p class="addr">{{ place.addr1 || '주소 정보 없음' }}</p>
                <p class="note">{{ place.note || '장소 메모가 없습니다.' }}</p>
              </div>

              <div
                v-if="index < post.places.length - 1"
                class="arrow"
              >
                →
              </div>
            </template>
          </div>
        </section>

        <div class="bottom-actions">
          <button type="button" class="list-button" @click="goList">
            목록으로
          </button>
        </div>
      </article>

      <aside class="side-card">
        <h2>게시물 정보</h2>

        <dl>
          <div>
            <dt>지역</dt>
            <dd>{{ post.district || '-' }}</dd>
          </div>

          <div>
            <dt>동행</dt>
            <dd>{{ post.companion || '-' }}</dd>
          </div>

          <div>
            <dt>작성일</dt>
            <dd>{{ post.created_at || '-' }}</dd>
          </div>

          <div>
            <dt>조회수</dt>
            <dd>{{ post.views || 0 }}</dd>
          </div>
        </dl>
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
  grid-template-columns: minmax(0, 1fr) 320px;
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
  margin: 0 0 20px;
  font-size: 20px;
  font-weight: 850;
}

.course-list {
  display: grid;
  grid-template-columns: 1fr 32px 1fr 32px 1fr;
  gap: 12px;
  align-items: center;
}

.course-card {
  min-height: 128px;
  padding: 20px;
  border: 1px solid #dbe2ec;
  border-radius: 15px;
  background: #fff;
}

.course-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.course-head span {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--main-color);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 900;
}

.course-head strong {
  color: #111827;
  font-size: 15px;
  font-weight: 850;
}

.addr {
  margin: 12px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.note {
  margin: 10px 0 0;
  color: #374151;
  font-size: 13px;
  line-height: 1.6;
}

.arrow {
  color: var(--main-color);
  font-size: 28px;
  font-weight: 800;
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
  padding: 26px;
}

.side-card h2 {
  margin: 0 0 24px;
  font-size: 19px;
  font-weight: 850;
}

.side-card dl {
  margin: 0;
}

.side-card dl div {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
}

.side-card dt {
  color: #6b7280;
  font-size: 14px;
}

.side-card dd {
  margin: 0;
  color: #374151;
  font-size: 14px;
  font-weight: 700;
}

.loading-box,
.empty-box {
  padding: 80px;
  border: 1px dashed #dbe2ec;
  border-radius: 18px;
  text-align: center;
  color: #6b7280;
}

@media (max-width: 1000px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .course-list {
    grid-template-columns: 1fr;
  }

  .arrow {
    transform: rotate(90deg);
  }
}

    .modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: 100;
    background: rgba(17, 24, 39, 0.36);
    display: flex;
    align-items: center;
    justify-content: center;
    }

    .password-modal {
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
</style>