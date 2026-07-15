<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
// AltHeader removed; use global header in App.vue

const router = useRouter()

const API_BASE_URL = 'https://ssafyescape.onrender.com'

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
const companionOptions = ['전체', '혼자', '싸피 친구', '부모님', '프로님/강사님']

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

/* ------------------------------------------------------------------
   카드 썸네일(미니맵) 전용 헬퍼
   - 순수 표시용이며 fetch/pagination 등 기존 데이터 로직에는 관여하지 않음
   - HomeView 의 지도 일러스트와 같은 톤(도로/블록/파크 + 브랜드 블루 루트)으로
     카드 썸네일을 그리기 위한 좌표만 제공한다.
------------------------------------------------------------------- */
const MAP_POINTS = [
  [30, 68],
  [82, 24],
  [132, 58],
]

function mapPoint(index) {
  return MAP_POINTS[index] || MAP_POINTS[MAP_POINTS.length - 1]
}

function mapRoutePath(post) {
  const count = Math.min(post.places?.length || 0, 3)
  if (count < 2) return ''
  return MAP_POINTS.slice(0, count)
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p[0]} ${p[1]}`)
    .join(' ')
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

          <div class="card-media">
            <svg
              class="mini-map"
              viewBox="0 0 160 96"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <defs>
                <pattern id="mapGrid" width="18" height="18" patternUnits="userSpaceOnUse">
                  <path d="M18 0H0V18" fill="none" stroke="var(--line)" stroke-width="1" />
                </pattern>
              </defs>

              <rect width="160" height="96" rx="14" fill="var(--paper)" />
              <rect width="160" height="96" rx="14" fill="url(#mapGrid)" opacity=".55" />

              <g fill="var(--slab)">
                <rect x="8" y="8" width="26" height="20" rx="4" />
                <rect x="120" y="12" width="30" height="22" rx="4" />
                <rect x="12" y="60" width="24" height="24" rx="4" />
                <rect x="108" y="64" width="30" height="20" rx="4" />
              </g>

              <g fill="var(--park)">
                <circle cx="60" cy="14" r="6" />
                <circle cx="98" cy="82" r="7" />
                <circle cx="16" cy="46" r="5" />
              </g>

              <path
                :d="mapRoutePath(post)"
                fill="none"
                stroke="var(--route)"
                stroke-width="2.4"
                stroke-linecap="round"
                stroke-linejoin="round"
                opacity=".9"
              />

              <g
                v-for="(place, index) in post.places.slice(0, 3)"
                :key="'pin-' + place.seq"
              >
                <circle
                  :cx="mapPoint(index)[0]"
                  :cy="mapPoint(index)[1]"
                  r="9.5"
                  fill="var(--route)"
                  stroke="#fff"
                  stroke-width="2"
                />
                <text
                  :x="mapPoint(index)[0]"
                  :y="mapPoint(index)[1] + 3"
                  text-anchor="middle"
                  font-family="Archivo, Pretendard, sans-serif"
                  font-size="9"
                  font-weight="700"
                  fill="#fff"
                >{{ index + 1 }}</text>
              </g>
            </svg>
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
/* 전역 토큰(--ink,--ink-60,--ink-30,--line,--line-strong,--route,--route-soft,
   --paper,--slab,--ease)은 src/style.css :root 에 정의되어 있음.
   이 컴포넌트에서는 미니맵 일러스트 전용 변수만 로컬로 둔다(HomeView와 동일 값). */
.post-list-page {
  --park: #E6F0E4;
  --road: #DEE1E5;
  width: 100%;
  max-width: 1220px;
  margin: 0 auto;
  padding: 24px 24px 80px;
  color: var(--ink);
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
  font-family: 'Archivo', 'Pretendard', sans-serif;
  font-size: 40px;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.page-head p {
  margin: 12px 0 0;
  color: var(--ink-60);
  font-size: 15px;
  line-height: 1.7;
}

.filter-card {
  padding: 20px;
  border: 1px solid var(--line-strong);
  border-radius: 18px;
  background: var(--paper);
  box-shadow: 0 14px 40px -24px rgba(14, 16, 19, 0.18);
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
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  overflow: hidden;
  background: var(--paper);
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease);
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
  background: transparent;
}

.search-box input::placeholder {
  color: var(--ink-30);
}

.search-box button {
  width: 76px;
  border: 0;
  background: transparent;
  color: var(--route);
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
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  background: var(--paper);
  color: var(--ink);
  font-size: 14px;
  font-family: inherit;
  padding: 0 12px;
  outline: none;
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease);
}

.filter-group select:focus,
.search-box:focus-within {
  border-color: var(--route);
  box-shadow: 0 0 0 4px var(--route-soft);
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
  color: var(--ink-60);
  font-size: 13px;
}

.sort-label strong {
  color: var(--ink);
  font-weight: 700;
}

.loading-box,
.empty-box {
  padding: 70px 24px;
  border: 1px dashed var(--line-strong);
  border-radius: 18px;
  color: var(--ink-60);
  font-size: 15px;
  text-align: center;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  justify-content: center;
}

.post-card {
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: var(--paper);
  cursor: pointer;
  transition: transform .18s var(--ease), border-color .18s var(--ease), box-shadow .18s var(--ease);
  box-shadow: 0 14px 34px -26px rgba(14, 16, 19, 0.3);
}

.post-card:hover {
  transform: translateY(-3px);
  border-color: var(--route);
  box-shadow: 0 18px 40px -22px rgba(3, 78, 161, 0.28);
}

.card-main {
  display: grid;
  grid-template-columns: 1fr 130px;
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
  color: var(--ink-30);
  font-size: 20px;
  cursor: pointer;
  transition: color .2s var(--ease);
}

.star-button:hover {
  color: var(--route);
}

.summary {
  min-height: 42px;
  margin: 10px 0 12px;
  color: var(--ink-60);
  font-size: 13px;
  line-height: 1.6;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-row span {
  padding: 5px 10px;
  border-radius: 999px;
  background: var(--slab);
  color: var(--ink-60);
  font-size: 12px;
  font-weight: 700;
}

.tag-row span:last-child {
  background: var(--route-soft);
  color: var(--route);
}

/* ── 카드 썸네일(미니맵) ─────────────────────────────────────── */
.card-media {
  flex: none;
}

.mini-map {
  display: block;
  width: 130px;
  height: 96px;
  border-radius: 14px;
  border: 1px solid var(--line);
  overflow: hidden;
}

.route-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  margin-top: 14px;
  padding: 9px 10px;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: var(--slab);
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
  background: var(--route);
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
  color: var(--ink-30);
  font-style: normal;
  font-size: 12px;
}

.card-footer {
  display: flex;
  gap: 18px;
  margin-top: 14px;
  color: var(--ink-30);
  font-size: 12px;
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
  border: 1px solid var(--line-strong);
  border-radius: 9px;
  background: var(--paper);
  color: var(--ink);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: border-color .2s var(--ease), background .2s var(--ease), color .2s var(--ease);
}

.pagination button:hover:not(:disabled) {
  border-color: var(--route);
  color: var(--route);
}

.pagination button.active {
  border-color: var(--route);
  background: var(--route);
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
    font-size: 32px;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.04em;
    text-align: left;
  }

  .page-head p {
    margin: 12px 0 0;
    font-size: 15px;
    line-height: 1.7;
    text-align: left;
  }

  .post-grid {
    grid-template-columns: 1fr;
  }

  .card-main {
    grid-template-columns: 1fr;
  }

  .card-media {
    order: -1;
  }

  .mini-map {
    width: 100%;
    height: 120px;
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