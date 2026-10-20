import api from './api';

export interface SummaryData {
  total_deliveries: number;
  completed: number;
  completion_rate: number;
}

export interface MatrixItem {
  proj_key: string;
  code: string;
  short: string;
  name: string;
  color: string;
  color2: string;
  icon: string;
  ent1_desc: string;
  ent2_desc: string;
  e1_done: boolean;
  e2_done: boolean;
}

export interface BimonthlyStatusItem {
  code: string;
  num_label: string;
  period_label: string;
  short_name: string;
  entregue: boolean;
  count: number;
}

export interface TimelineEntry {
  periodo_code: string;
  periodo_label: string;
  ent1_txt: string;
  ent2_txt: string;
  ent1_conc: string;
  ent2_conc: string;
  ent1_status: string;
  ent2_status: string;
}

export interface ProjectDetail {
  proj_key: string;
  code: string;
  short: string;
  name: string;
  color: string;
  color2: string;
  icon: string;
  ent1_desc: string;
  ent2_desc: string;
  bimonthly: BimonthlyStatusItem[];
  timeline: TimelineEntry[];
}

export interface DashboardResponse {
  summary: SummaryData;
  matrix: MatrixItem[];
  bimonthly_geral: BimonthlyStatusItem[];
  projects_detail: Record<string, ProjectDetail>;
  periods: Record<string, string>;
  selected_period: string | null;
  last_sync: string;
}

export const entregasService = {
  async getDashboard(periodo?: string, forceRefresh = false): Promise<DashboardResponse> {
    const params: Record<string, any> = {};
    if (periodo && periodo !== 'all') params.periodo = periodo;
    if (forceRefresh) params.force_refresh = true;

    const response = await api.get<DashboardResponse>('/api/v1/entregas-jornada/dashboard', { params });
    return response.data;
  },

  async sync(): Promise<{ status: string; message: string; last_sync: string }> {
    const response = await api.post('/api/v1/entregas-jornada/sync');
    return response.data;
  },
};