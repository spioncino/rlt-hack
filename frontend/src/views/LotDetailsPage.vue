<template>
  <article class="cards">
    <div class="cards__top">
      <div class="cards__main">
        <div class="cards__head">
          <p class="cards__lot">Лот 1</p>
          <p class="cards__deadline">Прием заявок до 27.04.26 10:00:00 (15 дн.) [GMT+3] (по Мск)</p>
        </div>

        <h3 class="cards__title">
          Выполнение работ по ремонту жилых помещений, находящихся в государственной собственности
          города Москвы
        </h3>

        <p class="cards__meta">
          ГКУ города Москвы «Московский центр недвижимости» · ИНН 7705990416
        </p>

        <div class="cards__tags">
          <span v-for="tag in tags" :key="tag" class="cards__tag">
            {{ tag }}
          </span>
        </div>
      </div>

      <div class="cards__summary">
        <div class="cards__status">
          <span class="cards__status-badge">Прием заявок 15 дн</span>
          <button type="button" class="cards__status-icon" aria-label="Добавить в избранное">
            ☆
          </button>
        </div>

        <div class="cards__price-block">
          <p class="cards__price">
            <span class="cards__price-arrow">▼</span>
            386 189 390,00 ₽
          </p>

          <div class="cards__security">
            <div class="cards__security-item">
              <span class="cards__security-label">Обеспечение заявки</span>
              <span class="cards__security-value">19 309 469,50 ₽ (5%)</span>
            </div>

            <div class="cards__security-item">
              <span class="cards__security-label">Обеспечение контракта</span>
              <span class="cards__security-value">77 237 878,00 ₽</span>
            </div>
          </div>

          <div class="cards__actions">
            <button type="button" class="cards__button">Получить обеспечение</button>

            <a href="#" class="cards__action-link" @click.prevent> Стоимость участия </a>
          </div>
        </div>
      </div>
    </div>

    <div class="cards__details">
      <section class="cards__details-card">
        <h4 class="cards__section-title">Этапы</h4>

        <div class="cards__detail-grid">
          <div v-for="stage in stages" :key="stage.label" class="cards__detail-row">
            <p class="cards__detail-term">{{ stage.label }}</p>
            <p class="cards__detail-desc">{{ stage.value }}</p>
          </div>
        </div>
      </section>

      <section class="cards__details-card">
        <h4 class="cards__section-title">Заказчик</h4>

        <div class="cards__detail-grid">
          <div class="cards__detail-row">
            <p class="cards__detail-term">Название организации</p>
            <p class="cards__detail-desc cards__detail-desc--strong">
              ГОСУДАРСТВЕННОЕ КАЗЕННОЕ УЧРЕЖДЕНИЕ ГОРОДА МОСКВЫ «МОСКОВСКИЙ ЦЕНТР НЕДВИЖИМОСТИ» (ИНН
              7705990416)
            </p>
          </div>
        </div>
      </section>

      <section class="cards__details-card cards__details-card--wide">
        <h4 class="cards__section-title">Информация о товаре, работе, услуге</h4>

        <div class="cards__detail-grid">
          <div v-for="item in itemInfo" :key="item.label" class="cards__detail-row">
            <p class="cards__detail-term">{{ item.label }}</p>
            <p class="cards__detail-desc">{{ item.value }}</p>
          </div>
        </div>
      </section>
    </div>
  </article>
</template>

<script setup>
const tags = ['77. г. Москва', '41.20.30.100', 'Текущий ремонт', 'Жилые помещения'];

const stages = [
  { label: 'Дата публикации', value: '10.04.26 17:28:49 (МСК)' },
  { label: 'Окончание подачи заявок', value: '27.04.26 10:00:00 (МСК)' },
  { label: 'Рассмотрение вторых частей', value: '29.04.26 00:00:00 (МСК)' },
  { label: 'Подведение итогов', value: '30.04.26 23:59:59 (МСК)' },
];

const itemInfo = [
  { label: 'Наименование', value: 'Ремонт текущий жилых помещений' },
  { label: 'Цена единицы ТРУ', value: '386 189 390,00 ₽' },
  { label: 'Количество', value: '1' },
  { label: 'Ед. измерения', value: 'Условная единица' },
  { label: 'Цифровой код по классификатору ОКПД2', value: '41.20.30.100' },
  {
    label: 'Описание кода по классификатору',
    value:
      'Работы по возведению жилых зданий, кроме работ по сохранению и воссозданию объектов культурного наследия',
  },
];
</script>

<style scoped>
.cards {
  width: 100%;
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
  gap: 24px;
}

.cards__main {
  min-width: 0;
  flex: 1;
}

.cards__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.cards__lot {
  position: relative;
  margin: 0;
  padding-left: 16px;

  color: #000;
  font-size: 14px;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
}

.cards__lot::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #79c65e;
  transform: translateY(-50%);
}

.cards__deadline {
  margin: 0;

  color: #6e6e6e;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
}

.cards__title {
  width: 100%;
  margin: 0 0 12px;

  color: #000;
  font-size: 20px;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
}

.cards__meta {
  margin: 0 0 16px;

  color: #6e6e6e;
  font-size: 14px;
  font-style: normal;
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
  min-height: 32px;
  padding: 0 12px;

  border-radius: 8px;
  background: #dbf2ff;

  color: #05a5ff;
  font-size: 14px;
  font-style: normal;
  font-weight: 500;
  line-height: normal;
  white-space: nowrap;
}

.cards__summary {
  width: 100%;
  max-width: 340px;
  flex-shrink: 0;

  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
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
  font-style: normal;
  font-weight: 500;
  line-height: normal;
  white-space: nowrap;
}

.cards__status-icon {
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 8px;
  background: #dbf2ff;
  color: #05a5ff;
  flex-shrink: 0;
  cursor: pointer;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  font-size: 16px;
  line-height: 1;
}

.cards__price-block {
  width: 100%;

  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 14px;
}

.cards__price {
  margin: 0;

  display: inline-flex;
  align-items: center;
  gap: 8px;

  color: #000;
  font-size: 45px;
  font-style: normal;
  font-weight: 500;
  line-height: 1;
  text-align: right;
}

.cards__price-arrow {
  color: #a14016;
  font-size: 16px;
  transform: translateY(-4px);
}

.cards__security {
  width: 100%;

  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cards__security-item {
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid #dbf2ff;
  background: #f8fdff;

  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.cards__security-label {
  color: #6e6e6e;
  font-size: 13px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
}

.cards__security-value {
  color: #000;
  font-size: 18px;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
  text-align: right;
}

.cards__actions {
  width: 100%;

  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.cards__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 16px;

  border: 0;
  border-radius: 10px;
  background: #16a163;

  color: #fff;
  font-size: 14px;
  font-style: normal;
  font-weight: 500;
  line-height: normal;
  cursor: pointer;
}

.cards__action-link {
  color: #05a5ff;
  font-size: 14px;
  font-style: normal;
  font-weight: 500;
  line-height: normal;
  text-decoration: none;
}

.cards__details {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.cards__details-card {
  padding: 18px;
  border: 1px solid #dbf2ff;
  border-radius: 24px;
  background: #f8fdff;
}

.cards__details-card--wide {
  grid-column: 1 / -1;
}

.cards__section-title {
  margin: 0 0 16px;

  color: #000;
  font-size: 18px;
  font-style: normal;
  font-weight: 600;
  line-height: normal;
}

.cards__detail-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cards__detail-row {
  display: grid;
  grid-template-columns: minmax(180px, 240px) 1fr;
  gap: 12px;
  align-items: start;
}

.cards__detail-term {
  margin: 0;

  color: #6e6e6e;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 1.45;
}

.cards__detail-desc {
  margin: 0;

  color: #000;
  font-size: 14px;
  font-style: normal;
  font-weight: 500;
  line-height: 1.45;
}

.cards__detail-desc--strong {
  font-weight: 600;
}

@media (max-width: 1100px) {
  .cards__top {
    flex-direction: column;
  }

  .cards__summary {
    max-width: none;
    align-items: flex-start;
  }

  .cards__price-block,
  .cards__actions {
    align-items: flex-start;
  }

  .cards__security-item {
    align-items: flex-start;
  }

  .cards__price,
  .cards__security-value {
    text-align: left;
  }

  .cards__details {
    grid-template-columns: 1fr;
  }

  .cards__details-card--wide {
    grid-column: auto;
  }
}

@media (max-width: 700px) {
  .cards {
    padding: 16px;
    gap: 24px;
    border-radius: 24px;
  }

  .cards__title {
    font-size: 18px;
  }

  .cards__price {
    font-size: 32px;
  }

  .cards__detail-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>
