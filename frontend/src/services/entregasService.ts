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
  id?: number;
  record_id?: string;
  origem?: string;
  periodo_code: string;
  periodo_label: string;
  ent1_txt: string;
  ent2_txt: string;
  ent1_conc: string;
  ent2_conc: string;
  ent1_status: string;
  ent2_status: string;
  usuario_registro?: string;
  updated_at?: string;
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
  e1_done?: boolean;
  e2_done?: boolean;
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

export interface FormProjectMeta {
  code: string;
  short: string;
  name: string;
  color: string;
  color2: string;
  icon: string;
  ent1_desc: string;
  ent2_desc: string;
  field_ent1_conc: string;
  field_ent1_txt: string;
  field_ent2_conc: string;
  field_ent2_txt: string;
}

export interface FormSchemaResponse {
  title: string;
  instructions: string;
  acknowledgement: string;
  projects: Record<string, FormProjectMeta>;
  periods: Record<string, string>;
  conclusion_options: Array<{ value: string; label: string; color: string }>;
  status_options: Array<{ value: string; label: string }>;
}

export interface ExistingRecordResponse {
  exists: boolean;
  record?: {
    record_id: string;
    projeto: string;
    periodo: string;
    ent1_conc: string;
    ent1_txt: string;
    ent2_conc: string;
    ent2_txt: string;
    form_1_complete: string;
  } | null;
  cascade_info?: {
    e1_concluida: boolean;
    e1_periodo: string | null;
    e2_concluida: boolean;
    e2_periodo: string | null;
  };
}

export interface FormularioEntregaPayload {
  record_id?: string | null;
  projeto: string;
  periodo: string;
  ent1_conc: string;
  ent1_txt: string;
  ent2_conc: string;
  ent2_txt: string;
  form_complete?: string;
}

export interface FormSubmitResponse {
  status: string;
  id?: number;
  record_id: string;
  projeto: string;
  periodo: string;
  message: string;
  acknowledgement: string;
}

export interface BimestreStatusItem {
  periodo_code: string;
  periodo_nome: string;
  ativo: boolean;
  has_submission: boolean;
  can_fill: boolean;
}

export const entregasService = {
  async getBimestresStatus(projeto?: string): Promise<Record<string, BimestreStatusItem>> {
    const params: Record<string, any> = {};
    if (projeto) params.projeto = projeto;
    const response = await api.get<Record<string, BimestreStatusItem>>('/api/v1/entregas-jornada/bimestres-status', { params });
    return response.data;
  },

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

  async getFormSchema(): Promise<FormSchemaResponse> {
    const response = await api.get<FormSchemaResponse>('/api/v1/entregas-jornada/form-schema');
    return response.data;
  },

  async findExistingRecord(projeto: string, periodo: string): Promise<ExistingRecordResponse> {
    const response = await api.get<ExistingRecordResponse>('/api/v1/entregas-jornada/registro-existente', {
      params: { projeto, periodo },
    });
    return response.data;
  },

  async submitForm(payload: FormularioEntregaPayload): Promise<FormSubmitResponse> {
    const response = await api.post<FormSubmitResponse>('/api/v1/entregas-jornada/formulario', payload);
    return response.data;
  },

  async listFormularios(projeto?: string, periodo?: string): Promise<any[]> {
    const params: Record<string, any> = {};
    if (projeto) params.projeto = projeto;
    if (periodo) params.periodo = periodo;
    const response = await api.get<any[]>('/api/v1/entregas-jornada/formularios', { params });
    return response.data;
  },

  async getFormularioById(id: number): Promise<any> {
    const response = await api.get<any>(`/api/v1/entregas-jornada/formularios/${id}`);
    return response.data;
  },

  async updateFormulario(id: number, payload: FormularioEntregaPayload): Promise<FormSubmitResponse> {
    const response = await api.put<FormSubmitResponse>(`/api/v1/entregas-jornada/formularios/${id}`, payload);
    return response.data;
  },

  async deleteFormulario(id: number): Promise<any> {
    const response = await api.delete<any>(`/api/v1/entregas-jornada/formularios/${id}`);
    return response.data;
  },
};