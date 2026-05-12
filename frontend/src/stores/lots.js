import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useLotsStore = defineStore('lots', () => {
  const lots = ref([]);
  const stats = ref(null);
  const sourceFileName = ref('');

  const setMatchResponse = (payload, fileName = '') => {
    lots.value = Array.isArray(payload?.lots) ? payload.lots : [];
    stats.value = payload?.stats ?? null;
    sourceFileName.value = fileName;
  };

  const clearLots = () => {
    lots.value = [];
    stats.value = null;
    sourceFileName.value = '';
  };

  return {
    lots,
    stats,
    sourceFileName,
    setMatchResponse,
    clearLots,
  };
});
