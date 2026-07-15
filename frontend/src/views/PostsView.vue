<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
// AltHeader removed; use global header in App.vue

const router = useRouter()

const API_BASE_URL = 'http://127.0.0.1:8000'

const keyword = ref('')
const selectedDistrict = ref('전체')
const selectedCompanion = ref('전체')
const selectedSort = ref('latest')

const posts = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 6
const loading = ref(false)

const districtOptions = ['전체', '강남구', '서초구', '송파구', '강동구', '관악구']
const companionOptions = ['전체', '혼자', '싸피 친구', '부모님', '프로님/강사님과']

const sortOptions = [
  { label: '최신순', value: 'latest' },
  { label: '조회순', value: 'views' },
]

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(total.value / pageSize))
})

const pageNumbers = computed(() => {
  const pages = []
  const max = totalPages.value

  for (let i = 1; i <= max; i += 1) {
    pages.push(i)
  }

  return pages.slice(0, 5)
})

onMounted(() => {
  fetchPosts()
})

async function fetchPosts() {
  loading.value = true

  const params = new URLSearchParams({
    page: currentPage.value,
    size: pageSize,
    sort: selectedSort.value,
  })

  if (keyword.value.trim()) {
    params.append('keyword', keyword.value.trim())
  }

  if (selectedDistrict.value !== '전체') {
    params.append('district', selectedDistrict.value)
  }

  if (selectedCompanion.value !== '전체') {
    params.append('companion', selectedCompanion.value)
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/posts?${params.toString()}`)

    if (!response.ok) {
      const errorData = await response.json()
      console.error('게시글 목록 API 오류:', errorData)
      throw new Error('게시글 목록 API 요청 실패')
    }

    const data = await response.json()

    posts.value = data.items
    total.value = data.total
  } catch (error) {
    console.error('게시글 목록 조회 실패:', error)

    posts.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function searchPosts() {
  currentPage.value = 1
  fetchPosts()
}

function changePage(page) {
  currentPage.value = page
  fetchPosts()
}

function goCreatePage() {
  router.push('/posts/create')
}

function goPostDetail(postId) {
  console.log('상세 페이지로 이동할 게시글 id:', postId)
  router.push(`/posts/${postId}`)
}

function getPostTags(post) {
  const tags = []

  if (post.time) tags.push(post.time)
  if (post.district) tags.push(post.district)
  if (post.companion) tags.push(post.companion)
  tags.push('추천 코스')

  return tags
}

function getShortContent(content) {
  if (!content) return ''
  if (content.length <= 54) return content
  return `${content.slice(0, 54)}...`
}
</script>

<template>
  <section class="post-list-page">
    <div class="page-head">
  <div>
    <h1>코스 게시판</h1>
    <p>
      멀티캠퍼스 역삼 주변과 서울 곳곳의 상황별 코스를 둘러보고,
      나에게 맞는 코스를 찾아보세요.
    </p>
  </div>
</div>

<section class="filter-card">
      <div class="search-area">
        <div class="search-box">
          <input
            v-model="keyword"
            type="text"
            placeholder="제목, 장소명, 키워드로 검색"
            @keyup.enter="searchPosts"
          />
          <button type="button" @click="searchPosts">검색</button>
        </div>

        <div class="filter-group">
          <label>
            주요 지역
            <select v-model="selectedDistrict" @change="searchPosts">
              <option
                v-for="district in districtOptions"
                :key="district"
                :value="district"
              >
                {{ district }}
              </option>
            </select>
          </label>

          <label>
            동행 유형
            <select v-model="selectedCompanion" @change="searchPosts">
              <option
                v-for="companion in companionOptions"
                :key="companion"
                :value="companion"
              >
                {{ companion }}
              </option>
            </select>
          </label>

          <label>
            정렬
            <select v-model="selectedSort" @change="searchPosts">
              <option
                v-for="option in sortOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>
        </div>
      </div>
    </section>

    <div class="list-top">
      <p>총 {{ total }}개의 게시글</p>

      <div class="sort-label">
        정렬
        <strong>{{ selectedSort === 'latest' ? '최신순' : '조회순' }}</strong>
      </div>
    </div>

    <div v-if="loading" class="loading-box">
      게시글을 불러오는 중입니다.
    </div>

    <div v-else-if="posts.length === 0" class="empty-box">
      검색 결과가 없습니다.
    </div>

    <div v-else class="post-grid">
      <article
        v-for="post in posts"
        :key="post.id"
        class="post-card"
        @click="goPostDetail(post.id)"
      >
        <div class="card-main">
          <div class="card-text">
            <div class="card-title-row">
              <h2>{{ post.title }}</h2>
              <button type="button" class="star-button" @click.stop>
                ☆
              </button>
            </div>

            <p class="summary">
              {{ getShortContent(post.content) }}
            </p>

            <div class="tag-row">
              <span
                v-for="tag in getPostTags(post)"
                :key="tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <div class="mini-map">
            <div class="mini-route">
              <span
                v-for="place in post.places.slice(0, 3)"
                :key="place.seq"
              >
                {{ place.seq }}
              </span>
            </div>
          </div>
        </div>

        <div class="route-strip">
          <template
            v-for="(place, index) in post.places.slice(0, 3)"
            :key="place.seq"
          >
            <div class="route-place">
              <span>{{ index + 1 }}</span>
              <strong>{{ place.title }}</strong>
            </div>
            <em v-if="index < post.places.slice(0, 3).length - 1">→</em>
          </template>
        </div>

        <div class="card-footer">
          <span>조회 {{ post.views || 0 }}</span>
          <span>{{ post.created_at || '날짜 없음' }}</span>
          <span>장소 {{ post.place_count || post.places.length }}개</span>
        </div>
      </article>
    </div>

    <div class="pagination">
      <button
        type="button"
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        ‹
      </button>

      <button
        v-for="page in pageNumbers"
        :key="page"
        type="button"
        :class="{ active: currentPage === page }"
        @click="changePage(page)"
      >
        {{ page }}
      </button>

      <button
        type="button"
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        ›
      </button>
    </div>
    </section>
</template>

<style scoped>
.post-list-page {
  --main-color: #034ea1;
  width: 100%;
  max-width: 1220px;
  margin: 0 auto;
  padding: 24px 24px 80px;
  color: var(--ink, #111827);
  box-sizing: border-box;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 28px;
}

.page-head h1 {
  margin: 0;
  color: var(--ink);
  font-size: 40px;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.page-head p {
  margin: 12px 0 0;
  color: var(--ink);
  font-size: 15px;
  line-height: 1.7;
  opacity: 0.6;
}

/* write-button removed */

.filter-card {
  padding: 20px;
  border: 1px solid #dbe2ec;
  border-radius: 18px;
  background: var(--paper);
  box-shadow: 0 18px 42px rgba(24, 42, 68, 0.05);
}

.search-area {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) auto;
  gap: 22px;
  align-items: end;
}

.search-box {
  display: flex;
  height: 46px;
  border: 1px solid #d8dee8;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

.search-box input {
  flex: 1;
  min-width: 0;
  border: 0;
  padding: 0 16px;
  color: var(--ink);
  font-size: 14px;
  font-family: inherit;
  outline: none;
}

.search-box button {
  width: 76px;
  border: 0;
  background: transparent;
  color: var(--main-color);
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
}

.filter-group {
  display: flex;
  gap: 14px;
  align-items: end;
}

.filter-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--ink);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.filter-group select {
  width: 118px;
  height: 46px;
  border: 1px solid #d8dee8;
  border-radius: 12px;
  background: #fff;
  color: var(--ink);
  font-size: 14px;
  font-family: inherit;
  padding: 0 12px;
  outline: none;
}

.filter-group select:focus,
.search-box:focus-within {
  border-color: var(--main-color);
  box-shadow: 0 0 0 3px rgba(3, 78, 161, 0.09);
}

.list-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 24px 2px 16px;
}

.list-top p {
  margin: 0;
  color: var(--ink);
  font-size: 14px;
  font-weight: 700;
}

.sort-label {
  display: flex;
  gap: 8px;
  color: var(--ink);
  font-size: 13px;
  opacity: 0.75;
}

.sort-label strong {
  color: var(--ink);
  opacity: 1;
}

.loading-box,
.empty-box {
  padding: 70px 24px;
  border: 1px dashed #cbd4e1;
  border-radius: 18px;
  color: var(--ink);
  font-size: 15px;
  text-align: center;
  opacity: 0.6;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  justify-content: center;
}

.post-card {
  padding: 16px;
  border: 1px solid #dbe2ec;
  border-radius: 16px;
  background: #fff;
  cursor: pointer;
  transition: 0.18s ease;
  box-shadow: 0 14px 34px rgba(24, 42, 68, 0.045);
}

.post-card:hover {
  transform: translateY(-3px);
  border-color: rgba(3, 78, 161, 0.45);
  box-shadow: 0 18px 38px rgba(3, 78, 161, 0.08);
}

.card-main {
  display: grid;
  grid-template-columns: 1fr 118px;
  gap: 14px;
}

.card-title-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.card-title-row h2 {
  flex: 1;
  margin: 0;
  color: var(--ink);
  font-size: 17px;
  font-weight: 800;
  line-height: 1.38;
  letter-spacing: -0.025em;
}

.star-button {
  width: 26px;
  height: 26px;
  border: 0;
  background: transparent;
  color: #8a96a8;
  font-size: 20px;
  cursor: pointer;
}

.summary {
  min-height: 42px;
  margin: 10px 0 12px;
  color: var(--ink);
  font-size: 13px;
  line-height: 1.6;
  opacity: 0.62;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-row span {
  padding: 5px 10px;
  border-radius: 999px;
  background: #f1f4f8;
  color: var(--ink);
  font-size: 12px;
  font-weight: 700;
  opacity: 0.75;
}

.mini-map {
  position: relative;
  height: 88px;
  border-radius: 13px;
  background:
    linear-gradient(135deg, rgba(3, 78, 161, 0.08), rgba(3, 78, 161, 0.02)),
    repeating-linear-gradient(
      45deg,
      #eef3f8 0,
      #eef3f8 8px,
      #f8fafc 8px,
      #f8fafc 16px
    );
  overflow: hidden;
}

.mini-map::before {
  content: '';
  position: absolute;
  left: 18px;
  top: 44px;
  width: 78px;
  height: 2px;
  background: var(--main-color);
  transform: rotate(-8deg);
}

.mini-route {
  position: absolute;
  inset: 0;
}

.mini-route span {
  position: absolute;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--main-color);
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-route span:nth-child(1) {
  left: 18px;
  top: 45px;
}

.mini-route span:nth-child(2) {
  left: 52px;
  top: 28px;
}

.mini-route span:nth-child(3) {
  right: 16px;
  bottom: 18px;
}

.route-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  margin-top: 14px;
  padding: 9px 10px;
  border: 1px solid #e2e7ef;
  border-radius: 11px;
  background: #fbfcfe;
  overflow: hidden;
}

.route-place {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.route-place span {
  width: 20px;
  height: 20px;
  flex: 0 0 20px;
  border-radius: 50%;
  background: var(--main-color);
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.route-place strong {
  max-width: 92px;
  color: var(--ink);
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-strip em {
  color: #8a96a8;
  font-style: normal;
  font-size: 12px;
}

.card-footer {
  display: flex;
  gap: 18px;
  margin-top: 14px;
  color: var(--ink);
  font-size: 12px;
  opacity: 0.58;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 28px;
}

.pagination button {
  width: 36px;
  height: 36px;
  border: 1px solid #d8dee8;
  border-radius: 9px;
  background: #fff;
  color: var(--ink);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.pagination button.active {
  border-color: var(--main-color);
  background: var(--main-color);
  color: #fff;
}

.pagination button:disabled {
  cursor: not-allowed;
  opacity: 0.35;
}

@media (max-width: 1100px) {
  .post-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .search-area {
    grid-template-columns: 1fr;
  }

  .filter-group {
    flex-wrap: wrap;
  }
}

@media (max-width: 720px) {
  .post-list-page {
    padding: 34px 14px 70px;
  }

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 28px;
  text-align: left;
}

.page-head h1 {
  margin: 0;
  color: var(--ink, #111827);
  font-size: 40px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.04em;
  text-align: left;
}

.page-head p {
  margin: 12px 0 0;
  color: var(--ink, #111827);
  font-size: 15px;
  line-height: 1.7;
  opacity: 0.6;
  text-align: left;
}

  .write-button {
    width: 100%;
  }

  .post-grid {
    grid-template-columns: 1fr;
  }

  .card-main {
    grid-template-columns: 1fr;
  }

  .mini-map {
    height: 100px;
  }

  .filter-group {
    display: grid;
    grid-template-columns: 1fr;
  }

  .filter-group label {
    display: grid;
    grid-template-columns: 70px 1fr;
  }

  .filter-group select {
    width: 100%;
  }
}
</style>