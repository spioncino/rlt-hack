<script setup>
import { computed } from 'vue';

const props = defineProps({
  lot: {
    type: Object,
    required: true,
  },
});

const matchPercent = computed(() => {
  return Math.round(Number(props.lot.match_score || 0));
});

const currentCount = computed(() => {
  return Number(props.lot.matched_products || 0);
});

const totalCount = computed(() => {
  return Number(props.lot.total_products || 0);
});

const tagsList = computed(() => {
  if (!props.lot.tags) return [];
  return String(props.lot.tags)
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
    .slice(0, 8);
});

const formattedDate = computed(() => {
  const raw = props.lot.publish_date;
  if (!raw) return '—';

  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;

  return date.toLocaleDateString('ru-RU');
});

const matchBadgeText = computed(() => {
  const type = props.lot.match_type;

  if (type === 'exact') return 'Точное совпадение';
  if (type === 'strong') return 'Сильное совпадение';
  if (type === 'medium') return 'Среднее совпадение';
  if (type === 'weak') return 'Слабое совпадение';

  return 'Совпадение найдено';
});
</script>

<template>
  <div class="cards">
    <div class="cards__top">
      <div class="cards__main">
        <h3 class="cards__title">
          {{ lot.lot_subject || lot.procedure_name }}
        </h3>

        <p class="cards__meta">
          {{ lot.platform_number }} (Лот {{ lot.lot_number }}) · {{ lot.pn_lot }}
        </p>

        <div class="cards__tags">
          <span v-for="tag in tagsList" :key="tag" class="cards__tag">
            {{ tag }}
          </span>
        </div>
      </div>

      <div class="cards__status">
        <span class="cards__status-badge">{{ matchBadgeText }}</span>
        <span class="cards__status-icon"></span>
      </div>
    </div>

    <div class="cards__bottom">
      <div class="cards__stats">
        <div class="cards__stat">
          <p
            class="cards__percent"
            :class="matchPercent >= 50 ? 'cards__percent--good' : 'cards__percent--bad'"
          >
            {{ matchPercent }}%
          </p>
          <p class="cards__label">совпадение</p>
        </div>

        <div class="cards__stat">
          <p class="cards__count">
            <span class="cards__count-current">{{ currentCount }}</span>
            <span class="cards__count-total">/{{ totalCount }}</span>
          </p>
          <p class="cards__label">товаров</p>
        </div>
      </div>

      <div class="cards__date-block">
        <p class="cards__date">{{ formattedDate }}</p>
        <p class="cards__label">дата публикации</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cards {
  width: 100%;
  min-height: 300px;
  padding: 18px 20px;
  border: 2px solid #dbf2ff;
  border-radius: 30px;
  background: #fff;

  display: flex;
  flex-direction: column;
  gap: 36px;

  font-family: Inter, sans-serif;
  cursor: pointer;
  will-change: transform, border-color, box-shadow;
  transition:
    transform 0.25s cubic-bezier(0.22, 1, 0.36, 1),
    border-color 0.25s ease,
    box-shadow 0.25s ease;
}

.cards:hover {
  transform: translateY(-4px);
  border-color: #8fd8ff;
  box-shadow: 0 10px 24px rgba(5, 165, 255, 0.12);
}

.cards__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.cards__main {
  min-width: 0;
  flex: 1;
}

.cards__title {
  max-width: 934px;
  width: 100%;
  margin: 0 0 12px;

  color: #000;
  font-size: 20px;
  font-weight: 600;
  line-height: normal;
}

.cards__meta {
  margin: 0 0 16px;

  color: #6e6e6e;
  font-size: 14px;
  font-weight: 400;
  line-height: normal;
}

.cards__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cards__tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  padding: 0 12px;

  border-radius: 8px;
  background: #dbf2ff;

  color: #05a5ff;
  font-size: 14px;
  font-weight: 500;
  line-height: normal;
  white-space: nowrap;
}

.cards__status {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  flex-shrink: 0;
}

.cards__status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  padding: 0 12px;

  border-radius: 8px;
  background: #ebf7ed;

  color: #16a163;
  font-size: 14px;
  font-weight: 500;
  line-height: normal;
  white-space: nowrap;
}

.cards__status-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #dbf2ff;
  flex-shrink: 0;
}

.cards__bottom {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
}

.cards__stats {
  display: flex;
  align-items: flex-end;
  gap: 48px;
}

.cards__stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cards__percent,
.cards__date,
.cards__count {
  margin: 0;
  font-weight: 500;
  line-height: normal;
}

.cards__percent {
  font-size: 45px;
}

.cards__percent--good {
  color: #16a163;
}

.cards__percent--bad {
  color: #a14016;
}

.cards__label {
  margin: 0;
  color: #000;
  font-size: 24px;
  font-weight: 400;
  line-height: normal;
}

.cards__count {
  display: inline-flex;
  align-items: baseline;
  gap: 0;
}

.cards__count-current {
  color: #000;
  font-size: 45px;
  font-weight: 500;
  line-height: normal;
}

.cards__count-total {
  color: #6e6e6e;
  font-size: 24px;
  font-weight: 500;
  line-height: normal;
}

.cards__date-block {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
  text-align: right;
}

.cards__date {
  color: #000;
  font-size: 45px;
}
</style>
