<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<template>
  <header class="header">
    <div class="header--wrap">
      <img src="../assets/logo.svg" alt="Логотип" class="header__logo" @click="router.push('/')" />

      <nav class="top-nav">
        <RouterLink to="/lots" class="top-nav__link"> Лоты и закупки </RouterLink>
        <RouterLink to="/" class="top-nav__link"> Номенклатуры </RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  width: 100%;
  max-width: 100%;
  height: 78px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #dbf2ff;
  background: #fff;
  box-shadow: 0 0.5px 15px 0 rgba(0, 0, 0, 0.25);
  gap: 24px;
  overflow: hidden;
}

.header--wrap {
  width: 1200px;

  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 64px;
}

.header--wrap img {
  width: 223px;
  height: 36px;

  cursor: pointer;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 64px;
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
}

.top-nav__link {
  position: relative;
  display: inline-flex;
  align-items: center;
  height: 80px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  white-space: nowrap;
  flex: 0 0 auto;

  transition: 0.2s;

  color: black !important;
}

.top-nav__link:hover {
  color: rgba(5, 165, 255, 1) !important;
}

.top-nav__link.router-link-active {
  color: rgba(5, 165, 255, 1) !important;
}
</style>
