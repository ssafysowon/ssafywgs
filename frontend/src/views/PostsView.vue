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

/*
  카드 썸네일과 코스 요약은 새 저장 구조인 post.course.stops를 우선 사용한다.
  예전 게시글처럼 post.course가 없는 경우에는 기존 post.places를 fallback으로 사용한다.
*/
function getCourseStops(post) {
  if (post.course?.stops?.length) {
    return post.course.stops
  }

  if (post.places?.length) {
    return post.places.map((place) => ({
      name: place.title,
      title: place.title,
      category: place.district || '',
      description: place.addr1 || '',
      stay: place.note || '',
      lat: place.lat,
      lng: place.lng,
      seq: place.seq,
    }))
  }

  return []
}

function getStopTitle(stop) {
  return stop.name || stop.title || '장소명 없음'
}

function getPlaceCount(post) {
  return getCourseStops(post).length || post.place_count || 0
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
  const count = Math.min(getCourseStops(post).length, 3)
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
        <div class="kicker">Community · LocalHub</div>
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
          <button type="button" @click="searchPosts">검색<span class="arrow">→</span></button>
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

              <g fill="var(--block)">
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
                v-for="(stop, index) in getCourseStops(post).slice(0, 3)"
                :key="'pin-' + post.id + '-' + index"
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
                >
                  {{ index + 1 }}
                </text>
              </g>
            </svg>
          </div>
        </div>

        <div
          v-if="getCourseStops(post).length"
          class="route-strip"
        >
          <template
            v-for="(stop, index) in getCourseStops(post).slice(0, 3)"
            :key="'route-' + post.id + '-' + index"
          >
            <div class="route-place">
              <span>{{ index + 1 }}</span>
              <strong>{{ getStopTitle(stop) }}</strong>
            </div>
            <span
              v-if="index < post.places.slice(0, 3).length - 1"
              class="route-seg"
              aria-hidden="true"
            ></span>
            <em v-if="index < getCourseStops(post).slice(0, 3).length - 1">→</em>
          </template>
        </div>

        <div
          v-else
          class="route-strip empty-route"
        >
          저장된 코스 정보가 없습니다.
        </div>

        <div class="card-footer">
          <span>조회 <b>{{ post.views || 0 }}</b></span>
          <span>{{ post.created_at || '날짜 없음' }}</span>
          <span>장소 <b>{{ post.place_count || post.places.length }}개</b></span>
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
  --block: #E8EAEE;
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
  align-items: flex-end;
  gap: 24px;
  margin-bottom: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--line);
}

.kicker {
  font-family: 'Archivo', sans-serif;
  font-size: 11.5px;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--route);
  font-weight: 600;
  margin-bottom: 12px;
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
  max-width: 520px;
  margin: 12px 0 0;
  color: var(--ink-60);
  font-size: 15px;
  line-height: 1.7;
}

.btn-solid {
  flex: none;
  height: 50px;
  padding: 0 22px;
  border: 0;
  border-radius: 14px;
  background: var(--ink);
  color: #fff;
  font-family: inherit;
  font-size: 14.5px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  transition: background .25s var(--ease), transform .25s var(--ease), box-shadow .3s var(--ease);
}

.btn-solid:hover {
  background: var(--route);
  transform: translateY(-2px);
  box-shadow: 0 16px 32px -16px rgba(14, 16, 19, .35);
}

.btn-solid .arrow {
  transition: transform .3s var(--ease);
}

.btn-solid:hover .arrow {
  transform: translateX(4px);
}

.filter-card {
  padding: 22px 24px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 14px 40px -26px rgba(14, 16, 19, 0.16);
}

.search-area {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) auto;
  gap: 22px;
  align-items: end;
}

.search-box {
  display: flex;
  height: 48px;
  border: 1px solid var(--line-strong);
  border-radius: 14px;
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
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 6px 6px 6px 0;
  padding: 0 18px;
  border: 0;
  border-radius: 10px;
  background: var(--ink);
  color: #fff;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  transition: background .2s var(--ease), transform .2s var(--ease);
}

.search-box button:hover {
  background: var(--route);
  transform: translateY(-1px);
}

.search-box button .arrow {
  font-size: 13px;
  transition: transform .2s var(--ease);
}

.search-box button:hover .arrow {
  transform: translateX(3px);
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
  color: var(--ink-30);
  font-family: 'Archivo', sans-serif;
  font-size: 10.5px;
  letter-spacing: .08em;
  text-transform: uppercase;
  font-weight: 700;
  white-space: nowrap;
}

.filter-group select {
  width: 118px;
  height: 46px;
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  background: #fff;
  color: var(--ink);
  font-size: 13.5px;
  font-weight: 600;
  font-family: inherit;
  padding: 0 12px;
  outline: none;
  cursor: pointer;
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease), color .2s var(--ease);
}

.filter-group select:hover {
  border-color: var(--route);
  color: var(--route);
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
  margin: 28px 2px 16px;
}

.list-top p {
  margin: 0;
  color: var(--ink);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.sort-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--ink-30);
  font-family: 'Archivo', sans-serif;
  font-size: 11px;
  letter-spacing: .06em;
  text-transform: uppercase;
  font-weight: 600;
}

.sort-label strong {
  color: var(--ink);
  font-family: 'Pretendard', sans-serif;
  font-size: 13px;
  font-weight: 700;
  text-transform: none;
  letter-spacing: -0.01em;
}

.loading-box,
.empty-box {
  padding: 76px 24px;
  border: 1px dashed var(--line-strong);
  border-radius: 20px;
  background: var(--block);
  color: var(--ink-60);
  font-size: 15px;
  font-weight: 500;
  text-align: center;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  justify-content: center;
}

.post-card {
  position: relative;
  overflow: hidden;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: #fff;
  cursor: pointer;
  transition: transform .2s var(--ease), border-color .2s var(--ease), box-shadow .25s var(--ease);
  box-shadow: 0 10px 26px -22px rgba(14, 16, 19, 0.22);
}

.post-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--route);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform .35s var(--ease);
}

.post-card:hover {
  transform: translateY(-4px);
  border-color: var(--line-strong);
  box-shadow: 0 18px 36px -20px rgba(14, 16, 19, 0.24);
}

.post-card:hover::before {
  transform: scaleX(1);
}

.card-main {
  display: grid;
  grid-template-columns: 1fr 130px;
  gap: 14px;
}

.card-title-row {
  display: flex;
  align-items: flex-start;
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
  padding: 5px 11px;
  border-radius: 999px;
  border: 1px solid var(--line-strong);
  background: #fff;
  color: var(--ink-60);
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.tag-row span:last-child {
  border-color: var(--route);
  background: var(--route);
  color: #fff;
}

/* 카드 썸네일(미니맵) */
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
  gap: 10px;
  min-height: 42px;
  margin-top: 14px;
  padding: 10px 12px;
  border: 1px dashed var(--line-strong);
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
}

.empty-route {
  justify-content: center;
  color: var(--ink-30);
  font-size: 12px;
  font-weight: 700;
}

.route-place {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
}

.route-place span {
  width: 20px;
  height: 20px;
  flex: 0 0 20px;
  border-radius: 50%;
  background: var(--route);
  color: #fff;
  font-family: 'Archivo', sans-serif;
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
  font-weight: 700;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-seg {
  flex: none;
  width: 18px;
  height: 0;
  border-top: 1.5px dashed var(--line-strong);
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  color: var(--ink-30);
  font-size: 12px;
}

.card-footer span {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-footer span:not(:last-child)::after {
  content: '';
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--line-strong);
}

.card-footer b {
  color: var(--ink-60);
  font-weight: 700;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 32px;
}

.pagination button {
  width: 38px;
  height: 38px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  background: #fff;
  color: var(--ink);
  font-family: 'Archivo', sans-serif;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  transition: border-color .2s var(--ease), background .2s var(--ease), color .2s var(--ease), transform .2s var(--ease);
}

.pagination button:hover:not(:disabled):not(.active) {
  border-color: var(--route);
  color: var(--route);
  transform: translateY(-1px);
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
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
    margin-bottom: 26px;
    padding-bottom: 22px;
    text-align: left;
  }

  .page-head .btn-solid {
    justify-content: center;
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