<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import Papa from 'papaparse';
import { CloudUpload, FileText, X } from 'lucide-vue-next';
import { useLotsStore } from '@/stores/lots';

const API_URL = 'http://82.202.157.12:8001/match';

const router = useRouter();
const lotsStore = useLotsStore();

const fileInput = ref(null);
const selectedFile = ref(null);
const errorMessage = ref('');
const isDragging = ref(false);
const parsedRowsCount = ref(0);
const parsedColumnsCount = ref(0);

const isUploading = ref(false);
const uploadSuccess = ref(false);
const backendError = ref('');
const backendResult = ref(null);

const openFileDialog = () => {
  fileInput.value?.click();
};

const detectDelimiter = (text) => {
  const lines = text
    .replace(/^\uFEFF/, '')
    .split(/\r\n|\n|\r/)
    .filter((line) => line.trim().length > 0);

  const firstLine = lines[0] ?? '';
  const semicolons = (firstLine.match(/;/g) || []).length;
  const commas = (firstLine.match(/,/g) || []).length;

  return semicolons > commas ? ';' : ',';
};

const formatFileSize = (bytes) => {
  if (!bytes) return '0 Б';
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
};

const fileSizeLabel = computed(() => {
  return selectedFile.value ? formatFileSize(selectedFile.value.size) : '';
});

const lotsCount = computed(() => backendResult.value?.lots?.length ?? 0);
const totalLotsFound = computed(() => backendResult.value?.stats?.total_lots_found ?? 0);

const parseCsvText = (text) => {
  return new Promise((resolve, reject) => {
    errorMessage.value = '';
    parsedRowsCount.value = 0;
    parsedColumnsCount.value = 0;

    const cleanText = text.replace(/^\uFEFF/, '');
    const delimiter = detectDelimiter(cleanText);

    Papa.parse(cleanText, {
      header: true,
      delimiter,
      skipEmptyLines: true,
      transformHeader: (header) => String(header ?? '').trim(),
      complete: (results) => {
        const rawFields = results.meta?.fields ?? [];
        const data = Array.isArray(results.data) ? results.data : [];

        if (!rawFields.length) {
          errorMessage.value = 'Не удалось определить заголовки CSV';
          reject(new Error('CSV headers not found'));
          return;
        }

        parsedColumnsCount.value = rawFields.length;
        parsedRowsCount.value = data.length;

        if (!data.length) {
          errorMessage.value = 'CSV прочитан, но строк с данными нет';
          reject(new Error('CSV has no data rows'));
          return;
        }

        if (results.errors?.length) {
          console.warn('Papa.parse errors:', results.errors);
        }

        resolve();
      },
      error: (error) => {
        console.error('Ошибка чтения CSV:', error);
        errorMessage.value = 'Не удалось прочитать CSV-файл';
        selectedFile.value = null;
        parsedRowsCount.value = 0;
        parsedColumnsCount.value = 0;
        reject(error);
      },
    });
  });
};

const sendFileToBackend = async (file) => {
  isUploading.value = true;
  uploadSuccess.value = false;
  backendError.value = '';
  backendResult.value = null;

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(API_URL, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `HTTP ${response.status}`);
    }

    const result = await response.json();

    backendResult.value = result;
    uploadSuccess.value = true;

    lotsStore.setMatchResponse(result, file.name);

    await router.push('/lots');
  } catch (error) {
    console.error('Ошибка отправки файла:', error);
    backendError.value = error?.message || 'Не удалось отправить файл на сервер';
  } finally {
    isUploading.value = false;
  }
};

const validateAndSetFile = async (file) => {
  errorMessage.value = '';
  backendError.value = '';
  uploadSuccess.value = false;
  backendResult.value = null;
  selectedFile.value = null;
  parsedRowsCount.value = 0;
  parsedColumnsCount.value = 0;

  if (!file) return;

  const isCsvByType =
    file.type === 'text/csv' || file.type === 'application/vnd.ms-excel' || file.type === '';
  const isCsvByName = file.name.toLowerCase().endsWith('.csv');

  if (!isCsvByType && !isCsvByName) {
    errorMessage.value = 'Можно загрузить только CSV-файл';
    return;
  }

  try {
    selectedFile.value = file;

    const text = await file.text();
    await parseCsvText(text);

    await sendFileToBackend(file);
  } catch (error) {
    console.error(error);
    if (!errorMessage.value) {
      errorMessage.value = 'Ошибка чтения файла';
    }
    selectedFile.value = null;
  }
};

const handleFileChange = async (event) => {
  const file = event.target.files?.[0];
  await validateAndSetFile(file);
};

const handleDragEnter = () => {
  isDragging.value = true;
};

const handleDragOver = (event) => {
  event.preventDefault();
  isDragging.value = true;
};

const handleDragLeave = (event) => {
  const currentTarget = event.currentTarget;
  const relatedTarget = event.relatedTarget;

  if (currentTarget && !currentTarget.contains(relatedTarget)) {
    isDragging.value = false;
  }
};

const handleDrop = async (event) => {
  event.preventDefault();
  isDragging.value = false;

  const file = event.dataTransfer?.files?.[0];
  await validateAndSetFile(file);
};

const clearFile = () => {
  selectedFile.value = null;
  errorMessage.value = '';
  backendError.value = '';
  uploadSuccess.value = false;
  backendResult.value = null;
  parsedRowsCount.value = 0;
  parsedColumnsCount.value = 0;
  lotsStore.clearLots();

  if (fileInput.value) {
    fileInput.value.value = '';
  }
};
</script>

<template>
  <section class="upload">
    <div
      class="upload-card"
      :class="{
        'upload-card--dragging': isDragging,
        'upload-card--error': errorMessage || backendError,
      }"
      @dragenter="handleDragEnter"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <input
        ref="fileInput"
        class="hidden-input"
        type="file"
        accept=".csv,text/csv"
        @change="handleFileChange"
      />

      <div class="upload-card__top">
        <div class="upload-card__heading">
          <h2 class="upload-card__title">Загрузка номенклатуры</h2>
          <p class="upload-card__subtitle">Перетащите CSV-файл сюда или выберите его вручную</p>
        </div>

        <div class="upload-card__badge">CSV</div>
      </div>

      <div class="upload-card__body">
        <div class="upload-card__left">
          <template v-if="selectedFile">
            <p class="upload-card__metric">
              {{ parsedRowsCount || '—' }}
            </p>
            <p class="upload-card__label">строк загружено</p>
          </template>

          <template v-else>
            <figure class="upload-card__icon">
              <CloudUpload :size="96" />
            </figure>
          </template>
        </div>

        <div class="upload-card__right">
          <template v-if="selectedFile">
            <div class="file-card">
              <div class="file-card__content">
                <FileText :size="28" />
                <div class="file-card__meta">
                  <p class="file-card__name">{{ selectedFile.name }}</p>
                  <p class="file-card__info">
                    {{ fileSizeLabel }} · {{ parsedColumnsCount || '—' }} колонок
                  </p>
                </div>
              </div>

              <button type="button" class="icon-button" @click="clearFile" aria-label="Убрать файл">
                <X :size="18" />
              </button>
            </div>
          </template>

          <template v-else>
            <button type="button" class="upload-button" @click="openFileDialog">
              Загрузить номенклатуру
            </button>
          </template>

          <p v-if="errorMessage" class="upload-card__error">
            {{ errorMessage }}
          </p>

          <p v-else-if="backendError" class="upload-card__error">
            Ошибка бэкенда: {{ backendError }}
          </p>

          <p v-else-if="isUploading" class="upload-card__hint">Отправляем файл на сервер...</p>

          <p v-else-if="uploadSuccess" class="upload-card__hint upload-card__hint--success">
            Файл отправлен. Найдено лотов: {{ lotsCount }} / {{ totalLotsFound }}
          </p>

          <p v-else-if="selectedFile" class="upload-card__hint upload-card__hint--success">
            Файл принят и прочитан на фронте
          </p>

          <p v-else class="upload-card__hint">
            Поддерживаются CSV с разделителем <strong>;</strong> и <strong>,</strong>
          </p>
        </div>
      </div>

      <div v-if="backendResult?.lots?.length" class="result-card">
        <h3 class="result-card__title">Первые результаты</h3>

        <div v-for="lot in backendResult.lots.slice(0, 3)" :key="lot.pn_lot" class="result-item">
          <p class="result-item__title">
            {{ lot.lot_subject }}
          </p>
          <p class="result-item__meta">{{ lot.pn_lot }} · {{ lot.match_score }}%</p>
          <p class="result-item__text">
            {{ lot.summary || 'Описание отсутствует' }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.upload {
  width: 100%;
}

.hidden-input {
  display: none;
}

.upload-card {
  width: 100%;
  min-height: 418px;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 36px;
  background: #d9edf9;
  border-radius: 30px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background-color 0.2s ease;
}

.upload-card--dragging {
  transform: scale(1.01);
  box-shadow: 0 0 0 2px #8cc6ea inset;
  background: #cde6f5;
}

.upload-card--error {
  background: #f6dddd;
}

.upload-card__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.upload-card__heading {
  max-width: 760px;
}

.upload-card__title {
  margin: 0 0 8px;
  font-size: 32px;
  line-height: 1.05;
  font-weight: 700;
  color: #111111;
}

.upload-card__subtitle {
  margin: 0;
  font-size: 18px;
  line-height: 1.3;
  color: #2b2b2b;
}

.upload-card__badge {
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
  white-space: nowrap;
}

.upload-card__body {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  flex: 1;
}

.upload-card__left,
.upload-card__right {
  display: flex;
  flex-direction: column;
}

.upload-card__left {
  justify-content: flex-end;
  min-width: 220px;
}

.upload-card__right {
  align-items: flex-end;
  gap: 14px;
  flex: 1;
}

.upload-card__icon {
  margin: 0;
  display: flex;
  align-items: center;
  color: #111111;
}

.upload-card__metric {
  margin: 0;
  font-size: 72px;
  line-height: 0.95;
  font-weight: 500;
  color: #000000;
}

.upload-card__label {
  margin: 8px 0 0;
  font-size: 22px;
  line-height: 1.1;
  color: #111111;
}

.upload-button {
  padding: 14px 32px;
  border: none;
  border-radius: 16px;
  background: #ffffff;
  color: #111111;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  transition:
    transform 0.15s ease,
    opacity 0.15s ease;
}

.upload-button:hover {
  transform: translateY(-1px);
}

.file-card {
  width: 100%;
  max-width: 520px;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.72);
  border-radius: 20px;
}

.file-card__content {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.file-card__meta {
  min-width: 0;
}

.file-card__name {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
  color: #111111;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-card__info {
  margin: 0;
  font-size: 14px;
  color: #4b4b4b;
}

.icon-button {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  border: none;
  border-radius: 12px;
  background: #ffffff;
  cursor: pointer;
}

.upload-card__hint,
.upload-card__error {
  margin: 0;
  font-size: 16px;
  text-align: right;
}

.upload-card__hint {
  color: #333333;
}

.upload-card__hint--success {
  color: #1c7f3e;
}

.upload-card__error {
  color: #b42318;
}

.result-card {
  margin-top: 8px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.72);
  border-radius: 20px;
}

.result-card__title {
  margin: 0 0 14px;
  font-size: 20px;
  font-weight: 700;
}

.result-item + .result-item {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.result-item__title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
}

.result-item__meta {
  margin: 0 0 6px;
  font-size: 14px;
  color: #4b4b4b;
}

.result-item__text {
  margin: 0;
  font-size: 14px;
  color: #222;
}

@media (max-width: 900px) {
  .upload-card {
    padding: 24px;
  }

  .upload-card__top,
  .upload-card__body {
    flex-direction: column;
    align-items: stretch;
  }

  .upload-card__right {
    align-items: stretch;
  }

  .upload-card__hint,
  .upload-card__error {
    text-align: left;
  }

  .upload-card__metric {
    font-size: 56px;
  }

  .upload-card__title {
    font-size: 26px;
  }
}
</style>
