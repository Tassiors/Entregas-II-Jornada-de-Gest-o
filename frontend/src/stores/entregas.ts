import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { entregasService, DashboardResponse, ProjectDetail } from '../services/entregasService';

export const useEntregasStore = defineStore('entregas', () => {
  const dashboard = ref<DashboardResponse | null>(null);
  const loading = ref<boolean>(false);
  const syncing = ref<boolean>(false);
  const error = ref<string | null>(null);
  const selectedPeriod = ref<string>('all');
  const selectedProjectKey = ref<string>('0');

  const summary = computed(() => dashboard.value?.summary || { total_deliveries: 0, completed: 0, completion_rate: 0 });
  const matrix = computed(() => dashboard.value?.matrix || []);
  const periods = computed(() => dashboard.value?.periods || {});
  const lastSync = computed(() => dashboard.value?.last_sync || '');

  const activeProject = computed<ProjectDetail | null>(() => {
    if (!dashboard.value?.projects_detail) return null;
    return dashboard.value.projects_detail[selectedProjectKey.value] || null;
  });

  async function loadDashboard(forceRefresh = false) {
    loading.value = true;
    error.value = null;
    try {
      const data = await entregasService.getDashboard(selectedPeriod.value, forceRefresh);
      dashboard.value = data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Erro ao carregar dados da Jornada de Gestão.';
      console.error('Erro na store entregas:', err);
    } finally {
      loading.value = false;
    }
  }

  async function syncData() {
    syncing.value = true;
    error.value = null;
    try {
      await entregasService.sync();
      await loadDashboard(true);
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Falha ao sincronizar com o REDCap.';
      console.error('Erro ao sincronizar REDCap:', err);
    } finally {
      syncing.value = false;
    }
  }

  function setPeriod(period: string) {
    selectedPeriod.value = period;
    loadDashboard();
  }

  function setProject(projKey: string) {
    selectedProjectKey.value = projKey;
  }

  return {
    dashboard,
    loading,
    syncing,
    error,
    selectedPeriod,
    selectedProjectKey,
    summary,
    matrix,
    periods,
    lastSync,
    activeProject,
    loadDashboard,
    syncData,
    setPeriod,
    setProject,
  };
});