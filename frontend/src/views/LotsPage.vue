<script setup>
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { ChevronDown } from 'lucide-vue-next';
import Cards from '../components/ui/Cards.vue';
import { useLotsStore } from '@/stores/lots';

const lotsStore = useLotsStore();

const searchQuery = ref('');
const matchFilter = ref('all');
const sortFilter = ref('default');

const hasSourceData = computed(() => lotsStore.lots.length > 0);

const filteredLots = computed(() => {
  let result = [...lotsStore.lots];

  const q = searchQuery.value.trim().toLowerCase();

  if (q) {
    result = result.filter((lot) => {
      const inPlatform = String(lot.platform_number || '')
        .toLowerCase()
        .includes(q);
      const inPnLot = String(lot.pn_lot || '')
        .toLowerCase()
        .includes(q);
      const inSubject = String(lot.lot_subject || '')
        .toLowerCase()
        .includes(q);
      const inProcedure = String(lot.procedure_name || '')
        .toLowerCase()
        .includes(q);

      return inPlatform || inPnLot || inSubject || inProcedure;
    });
  }

  if (matchFilter.value === '80plus') {
    result = result.filter((lot) => Number(lot.match_score) >= 80);
  } else if (matchFilter.value === '50plus') {
    result = result.filter((lot) => Number(lot.match_score) >= 50);
  } else if (matchFilter.value === 'less50') {
    result = result.filter((lot) => Number(lot.match_score) < 50);
  }

  if (sortFilter.value === 'matchDesc') {
    result.sort((a, b) => Number(b.match_score) - Number(a.match_score));
  } else if (sortFilter.value === 'matchAsc') {
    result.sort((a, b) => Number(a.match_score) - Number(b.match_score));
  } else if (sortFilter.value === 'lotNumber') {
    result.sort((a, b) =>
      String(a.platform_number || '').localeCompare(String(b.platform_number || ''), 'ru'),
    );
  } else if (sortFilter.value === 'subject') {
    result.sort((a, b) =>
      String(a.lot_subject || '').localeCompare(String(b.lot_subject || ''), 'ru'),
    );
  }

  return result;
});
</script>

<template>
  <div class="lots__container">
    <section class="lots__toolbar">
      <input
        v-model="searchQuery"
        class="lots__search-input"
        type="text"
        placeholder="Номер лота, название..."
      />

      <div
        class="lots__select-wrap"
        :class="{ 'lots__select-wrap--active': matchFilter !== 'all' }"
      >
        <select v-model="matchFilter" class="lots__select">
          <option value="all">Совпадение</option>
          <option value="80plus">От 80%</option>
          <option value="50plus">От 50%</option>
          <option value="less50">Ниже 50%</option>
        </select>
        <ChevronDown class="lots__select-icon" :size="16" />
      </div>

      <div
        class="lots__select-wrap"
        :class="{ 'lots__select-wrap--active': sortFilter !== 'default' }"
      >
        <select v-model="sortFilter" class="lots__select">
          <option value="default">Упорядочить</option>
          <option value="lotNumber">По номеру лота</option>
          <option value="subject">По названию лота</option>
          <option value="matchDesc">По совпадению ↓</option>
          <option value="matchAsc">По совпадению ↑</option>
        </select>
        <ChevronDown class="lots__select-icon" :size="16" />
      </div>
    </section>

    <main v-if="filteredLots.length" class="lots__content">
      <Cards v-for="lot in filteredLots" :key="lot.pn_lot" :lot="lot" />
    </main>

    <section v-else class="lots__empty">
      <template v-if="hasSourceData">
        <h2 class="lots__empty-title">Ничего не найдено</h2>
        <p class="lots__empty-text">По текущему запросу или выбранным фильтрам лоты не найдены.</p>
      </template>

      <template v-else>
        <h2 class="lots__empty-title">Нет данных</h2>
        <p class="lots__empty-text">
          Загрузите данные на странице
          <RouterLink to="/" class="lots__empty-link">/</RouterLink>
        </p>
      </template>
    </section>
  </div>
</template>

<style scoped>
.lots__container {
  padding-bottom: 80px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.lots__toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.lots__search-input {
  width: 270px;
  height: 36px;
  padding: 8px 12px;

  border-radius: 12px;
  border: 1px solid #cbd5e1;
  background: #fff;
  outline: none;

  color: #0f172a;
  font-family: Inter, sans-serif;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px;

  transition:
    border-color 0.25s ease,
    box-shadow 0.25s ease,
    transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.lots__search-input::placeholder {
  color: #94a3b8;
  font-family: Inter, sans-serif;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px;
}

.lots__search-input:hover {
  border-color: #8fd8ff;
  box-shadow: 0 6px 16px rgba(5, 165, 255, 0.08);
}

.lots__search-input:focus {
  border-color: #05a5ff;
  box-shadow: 0 0 0 3px rgba(5, 165, 255, 0.12);
}

.lots__select-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;

  min-width: 130px;
  height: 40px;

  padding-right: 34px;

  border-radius: 12px;
  border: 2px solid #dbf2ff;
  background: #fff;

  transition:
    border-color 0.25s ease,
    box-shadow 0.25s ease,
    transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.lots__select-wrap:hover {
  border-color: #8fd8ff;
  box-shadow: 0 6px 16px rgba(5, 165, 255, 0.08);
}

.lots__select-wrap:focus-within {
  border-color: #05a5ff;
  box-shadow: 0 0 0 3px rgba(5, 165, 255, 0.12);
}

.lots__select-wrap--active {
  border-color: #8fd8ff;
  box-shadow: 0 6px 16px rgba(5, 165, 255, 0.08);
}

.lots__select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;

  width: 100%;
  height: 100%;
  padding: 8px 16px;

  border: none;
  outline: none;
  background: transparent;
  cursor: pointer;

  color: #0f172a;
  font-family: Inter, sans-serif;
  font-size: 14px;
  font-style: normal;
  font-weight: 500;
  line-height: 20px;
}

.lots__select-icon {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  pointer-events: none;
  color: #0f172a;
}

.lots__content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.lots__empty {
  min-height: 260px;
  padding: 32px 20px;
  border: 2px dashed #dbf2ff;
  border-radius: 30px;
  background: #fff;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;

  text-align: center;
}

.lots__empty-title {
  margin: 0;
  color: #0f172a;
  font-family: Inter, sans-serif;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.lots__empty-text {
  margin: 0;
  color: #64748b;
  font-family: Inter, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 1.5;
}

.lots__empty-link {
  color: #05a5ff;
  font-weight: 600;
  text-decoration: none;
}

.lots__empty-link:hover {
  text-decoration: underline;
}
</style>
