import { createRouter, createWebHistory } from 'vue-router';

const HomePage = () => import('@/views/HomePage.vue');
const LotsPage = () => import('@/views/LotsPage.vue');
const LotDetailsPage = () => import('@/views/LotDetailsPage.vue');
const NotFoundPage = () => import('@/views/NotFoundPage.vue');

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/lots',
      name: 'lots',
      component: LotsPage,
    },
    {
      path: '/lots/:id',
      name: 'lot-details',
      component: LotDetailsPage,
      props: true,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundPage,
    },
  ],
});

export default router;
