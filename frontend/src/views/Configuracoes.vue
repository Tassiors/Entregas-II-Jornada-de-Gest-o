<template>
  <div class="space-y-6">
    <!-- Cabeçalho das Configurações -->
    <Card>
      <template #header>
        <div class="flex items-center space-x-3">
          <Cog6ToothIcon class="h-7 w-7 text-paper-text" />
          <h1 class="text-2xl font-bold text-paper-text">Configurações</h1>
        </div>
      </template>

      <div v-if="authStore.isAdmin" class="space-y-6">
        <p class="text-gray-600 leading-relaxed text-sm">
          Gerencie seu perfil corporativo, o cadastro de colaboradores autorizados e a concessão de perfis (RBAC), incluindo a associação exclusiva de <strong>Gerentes de Projeto</strong> para a II Jornada de Gestão da <strong>Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC</strong>.
        </p>

        <!-- 1. Perfil do Usuário Logado -->
        <div v-if="authStore.user" class="p-5 bg-white border border-gray-200 rounded-xl shadow-sm space-y-3">
          <div class="flex items-center space-x-2 text-paper-text font-bold text-lg border-b pb-2">
            <UserCircleIcon class="h-6 w-6 text-gray-500" />
            <span>Seu Perfil Corporativo (Active Directory)</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm pt-1">
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">Usuário / Login AD</p>
              <p class="font-bold text-gray-800">{{ authStore.user.username }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">Nome Completo</p>
              <p class="font-medium text-gray-800">{{ authStore.user.displayName?.[0] || authStore.user.username }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">E-mail Corporativo</p>
              <p class="font-medium text-gray-800">{{ authStore.user.email?.[0] || 'Não cadastrado' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase">Setor / Lotação</p>
              <p class="font-medium text-gray-800">{{ authStore.user.department?.[0] || 'UGERC / HC-UFPE' }}</p>
            </div>
          </div>
        </div>

        <!-- 2. Painel de Gestão de Usuários e Perfis (RBAC Local) -->
        <div class="p-5 bg-white border border-gray-200 rounded-xl shadow-sm space-y-4">
          <div class="flex flex-col md:flex-row md:items-center justify-between border-b pb-3 gap-3">
            <div>
              <h2 class="text-lg font-bold text-paper-text flex items-center gap-2">
                <UserGroupIcon class="h-6 w-6 text-gray-600" />
                Usuários do Sistema (RBAC Local)
              </h2>
              <p class="text-xs text-gray-500 mt-0.5">
                Cadastre o login do Active Directory (AD) para autorizar e vincular gestores aos 5 projetos da II Jornada.
              </p>
            </div>
            <div class="flex items-center gap-2">
              <Button variant="secondary" @click="loadUsers" :disabled="isLoadingUsers">
                <span class="text-xs font-semibold">Atualizar Lista</span>
              </Button>
              <Button variant="primary" @click="openAddModal">
                <template #icon>
                  <UserPlusIcon class="h-5 w-5" />
                </template>
                Incluir Usuário
              </Button>
            </div>
          </div>

          <!-- Tabela de Usuários Cadastrados -->
          <div class="overflow-x-auto">
            <div v-if="isLoadingUsers" class="p-8 text-center text-sm text-gray-500">
              Carregando usuários cadastrados...
            </div>
            <table v-else class="w-full text-left text-sm text-gray-600">
              <thead class="bg-gray-50 text-xs uppercase font-semibold text-gray-500 border-b">
                <tr>
                  <th class="py-3 px-4">Login de Rede</th>
                  <th class="py-3 px-4">Nome do Colaborador</th>
                  <th class="py-3 px-4">Perfil de Acesso</th>
                  <th class="py-3 px-4">Projeto Atribuído</th>
                  <th class="py-3 px-4 text-center">Status</th>
                  <th class="py-3 px-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-if="usersList.length === 0">
                  <td colspan="6" class="py-8 text-center text-gray-400 text-sm">
                    Nenhum colaborador cadastrado localmente. Clique em "Incluir Usuário".
                  </td>
                </tr>
                <tr v-for="user in usersList" :key="user.id" class="hover:bg-gray-50/80 transition-colors">
                  <td class="py-3 px-4 font-bold text-gray-800 flex items-center gap-2">
                    <UserIcon class="h-4 w-4 text-gray-400" />
                    {{ user.username }}
                  </td>
                  <td class="py-3 px-4 font-medium text-gray-700">
                    <div>{{ user.nome }}</div>
                    <div v-if="user.email" class="text-xs text-gray-400">{{ user.email }}</div>
                  </td>
                  <td class="py-3 px-4">
                    <span :class="getRoleBadgeClass(user.perfil)" class="px-2.5 py-1 text-xs font-bold rounded-md">
                      {{ getRoleLabel(user.perfil) }}
                    </span>
                  </td>
                  <td class="py-3 px-4">
                    <div v-if="user.perfil === 'GERENTE_PROJETO' && user.projeto_atribuido !== null" class="flex items-center gap-1.5">
                      <span class="px-2 py-0.5 text-xs font-extrabold bg-blue-100 text-blue-800 rounded">
                        P{{ user.projeto_atribuido }}
                      </span>
                      <span class="text-xs text-gray-700 truncate max-w-[200px]" :title="getProjectName(user.projeto_atribuido)">
                        {{ getProjectName(user.projeto_atribuido) }}
                      </span>
                    </div>
                    <span v-else class="text-xs text-gray-400 italic">
                      {{ user.perfil === 'ADMINISTRADOR' ? 'Todos os projetos' : 'Sem restrição' }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span :class="user.ativo ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'" class="px-2 py-0.5 text-xs font-bold rounded">
                      {{ user.ativo ? 'ATIVO' : 'INATIVO' }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-right space-x-2 whitespace-nowrap">
                    <button 
                      @click="openEditModal(user)" 
                      title="Alterar Perfil" 
                      class="px-2.5 py-1 text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-md transition cursor-pointer"
                    >
                      Editar
                    </button>
                    <button 
                      @click="toggleUserStatus(user)" 
                      :class="user.ativo ? 'text-amber-700 hover:bg-amber-50 border-amber-300' : 'text-emerald-700 hover:bg-emerald-50 border-emerald-300'"
                      class="px-2.5 py-1 text-xs font-semibold border rounded-md transition cursor-pointer"
                    >
                      {{ user.ativo ? 'Inativar' : 'Ativar' }}
                    </button>
                    <button 
                      @click="confirmRemoveUser(user)" 
                      title="Excluir Usuário"
                      class="px-2 py-1 text-xs font-semibold text-red-600 hover:text-red-800 hover:bg-red-50 border border-red-200 rounded-md transition cursor-pointer"
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 3. Disponibilidade de Bimestres para Preenchimento -->
        <div class="p-5 bg-white border border-gray-200 rounded-xl shadow-sm space-y-4">
          <div class="flex flex-col md:flex-row md:items-center justify-between border-b pb-3 gap-3">
            <div>
              <h2 class="text-lg font-bold text-paper-text flex items-center gap-2">
                <CalendarDaysIcon class="h-6 w-6 text-indigo-600" />
                Disponibilidade dos Bimestres para Preenchimento
              </h2>
              <p class="text-xs text-gray-500 mt-0.5">
                Defina quais períodos estão abertos para novos preenchimentos. Se um bimestre com relatórios submetidos for desabilitado, as permissões de leitura, edição e exclusão permanecem garantidas para o respectivo gerente do projeto.
              </p>
            </div>
            <Button variant="secondary" @click="loadBimestresConfig" :disabled="isLoadingBimestres">
              <span class="text-xs font-semibold">Atualizar Status</span>
            </Button>
          </div>

          <div v-if="isLoadingBimestres" class="p-6 text-center text-sm text-gray-500">
            Carregando configurações de bimestres...
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="b in bimestresList" 
              :key="b.periodo_code"
              :class="b.ativo ? 'border-emerald-200 bg-emerald-50/20' : 'border-amber-200 bg-amber-50/20'"
              class="p-4 rounded-xl border flex flex-col justify-between space-y-3 transition-all hover:shadow-sm"
            >
              <div class="flex items-start justify-between">
                <div>
                  <span class="text-xs font-bold uppercase tracking-wider text-gray-400">
                    Bimestre {{ Number(b.periodo_code) + 1 }}
                  </span>
                  <h3 class="text-base font-bold text-gray-800">{{ b.periodo_nome }}</h3>
                </div>
                <span 
                  :class="b.ativo ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-amber-100 text-amber-800 border-amber-300'"
                  class="px-2.5 py-1 text-xs font-bold rounded-full border flex items-center gap-1.5"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="b.ativo ? 'bg-emerald-600' : 'bg-amber-600'"></span>
                  {{ b.ativo ? 'Aberto' : 'Desabilitado' }}
                </span>
              </div>

              <div class="pt-2 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                <span class="truncate">
                  {{ b.ativo ? 'Permite novos cadastros' : 'Apenas relatórios prévios' }}
                </span>
                <button
                  @click="toggleBimestreStatus(b)"
                  :disabled="updatingBimestreCode === b.periodo_code"
                  :class="b.ativo ? 'text-amber-700 hover:bg-amber-100 border-amber-300 bg-amber-50/50' : 'text-emerald-700 hover:bg-emerald-100 border-emerald-300 bg-emerald-50/50'"
                  class="ml-2 px-3 py-1.5 font-bold border rounded-lg transition-colors cursor-pointer whitespace-nowrap shadow-xs"
                >
                  {{ updatingBimestreCode === b.periodo_code ? 'Salvando...' : (b.ativo ? 'Desabilitar' : 'Habilitar') }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Informações dos Perfis e Regras RBAC -->
        <div class="p-5 bg-gray-50 border border-gray-200 rounded-xl space-y-3">
          <div class="flex items-center space-x-2 text-paper-text font-bold text-md border-b pb-2">
            <ShieldCheckIcon class="h-5 w-5 text-gray-600" />
            <span>Perfis e Níveis de Permissão no Sistema</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-1">
            <div 
              v-for="roleItem in availableRoles" 
              :key="roleItem.codigo"
              class="p-3 bg-white border border-gray-200 rounded-lg space-y-1"
            >
              <div class="flex items-center justify-between">
                <span :class="roleItem.badgeClass" class="px-2 py-0.5 text-xs font-bold rounded">
                  {{ roleItem.nome }}
                </span>
                <span class="text-[10px] text-gray-400 uppercase font-mono">{{ roleItem.codigo }}</span>
              </div>
              <p class="text-xs text-gray-500 pt-1 leading-relaxed">{{ roleItem.descricao }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="p-6 bg-red-50 border border-red-200 text-red-700 rounded-xl">
        <h2 class="text-lg font-bold">Acesso Restrito ao Menu de Configurações</h2>
        <p class="text-sm mt-1">Este menu é de acesso exclusivo para o perfil de <strong>ADMINISTRADOR</strong>.</p>
      </div>
    </Card>

    <!-- Modal 1: Incluir Novo Usuário AD -->
    <Modal :show="showAddUserModal" @close="closeAddModal">
      <template #header>Incluir Usuário no Sistema</template>
      <form @submit.prevent="saveUser" class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Login de Rede (AD)</label>
          <div class="flex gap-2">
            <input 
              v-model="newUser.username" 
              type="text" 
              required 
              placeholder="Ex: joao.silva"
              @keyup.enter.prevent="searchADUser"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm"
            />
            <Button 
              variant="secondary" 
              type="button" 
              :disabled="isSearchingAD || !newUser.username.trim()" 
              @click="searchADUser"
            >
              <span v-if="isSearchingAD" class="text-xs font-semibold">Buscando...</span>
              <span v-else class="text-xs font-semibold flex items-center gap-1">
                <MagnifyingGlassIcon class="h-4 w-4" />
                Consultar AD
              </span>
            </Button>
          </div>
          <p class="text-xs text-gray-400 mt-1">Digite o login corporativo EBSERHNET (ex: `joao.silva`).</p>
        </div>

        <!-- Banner de Resultado da Consulta AD -->
        <div v-if="adSearchStatus === 'success' && adSearchData" class="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs space-y-1">
          <p class="font-bold flex items-center gap-1 text-sm text-emerald-900">
            <CheckCircleIcon class="h-4 w-4 text-emerald-600 shrink-0" />
            Usuário localizado no Active Directory (EBSERHNET)
          </p>
          <p><strong>Nome Completo:</strong> {{ adSearchData.displayName }}</p>
          <p v-if="adSearchData.email"><strong>E-mail:</strong> {{ adSearchData.email }}</p>
          <p><strong>Lotação / Setor:</strong> {{ adSearchData.department }}</p>
        </div>

        <div v-if="adSearchStatus === 'error'" class="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs flex items-center gap-2">
          <ExclamationTriangleIcon class="h-4 w-4 text-red-500 shrink-0" />
          <span>{{ adErrorMessage }}</span>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Nome Completo do Colaborador</label>
          <input 
            v-model="newUser.nome" 
            type="text" 
            required 
            placeholder="Ex: João da Silva"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">E-mail Corporativo</label>
            <input 
              v-model="newUser.email" 
              type="email" 
              placeholder="Ex: joao.silva@ebserh.gov.br"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">Setor / Lotação</label>
            <input 
              v-model="newUser.departamento" 
              type="text" 
              placeholder="Ex: UGERC / HC-UFPE"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Perfil de Acesso</label>
          <select 
            v-model="newUser.perfil" 
            required 
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm bg-white"
          >
            <option v-for="role in availableRoles" :key="role.codigo" :value="role.codigo">
              {{ role.nome }}
            </option>
          </select>
        </div>

        <!-- Seleção de Projeto Obrigatória para Gerente de Projeto -->
        <div v-if="newUser.perfil === 'GERENTE_PROJETO'" class="p-4 bg-blue-50 border border-blue-200 rounded-xl space-y-2">
          <label class="block text-sm font-bold text-blue-900">
            Projeto Atribuído da II Jornada <span class="text-red-500">*</span>
          </label>
          <select 
            v-model="newUser.projeto_atribuido" 
            required 
            class="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm bg-white font-medium"
          >
            <option value="" disabled>Selecione um dos 5 projetos...</option>
            <option v-for="(p, key) in projectOptions" :key="key" :value="key">
              {{ p.code }} — {{ p.name }}
            </option>
          </select>
          <p class="text-xs text-blue-700">
            O Gerente de Projeto terá permissão para operações CRUD exclusivamente neste projeto.
          </p>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" type="button" @click="closeAddModal">Cancelar</Button>
          <Button variant="primary" type="submit" :disabled="isSavingUser">
            {{ isSavingUser ? 'Gravando...' : 'Incluir Usuário' }}
          </Button>
        </div>
      </form>
    </Modal>

    <!-- Modal 2: Alterar Perfil do Usuário -->
    <Modal :show="showEditUserModal" @close="closeEditModal">
      <template #header>Alterar Perfil de Acesso</template>
      <form v-if="editingUser" @submit.prevent="updateUserRole" class="space-y-4">
        <div class="p-3 bg-gray-50 border rounded-lg space-y-1 text-sm">
          <p><strong class="text-gray-700">Login de Rede:</strong> <span class="font-bold text-gray-900">{{ editingUser.username }}</span></p>
          <p><strong class="text-gray-700">Nome:</strong> {{ editingUser.nome }}</p>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">Selecione o Novo Perfil de Acesso</label>
          <select 
            v-model="editingUser.perfil" 
            required 
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-text focus:outline-none text-sm bg-white"
          >
            <option v-for="role in availableRoles" :key="role.codigo" :value="role.codigo">
              {{ role.nome }}
            </option>
          </select>
        </div>

        <!-- Projeto atribuído se perfil for GERENTE_PROJETO -->
        <div v-if="editingUser.perfil === 'GERENTE_PROJETO'" class="p-4 bg-blue-50 border border-blue-200 rounded-xl space-y-2">
          <label class="block text-sm font-bold text-blue-900">
            Projeto Atribuído da II Jornada <span class="text-red-500">*</span>
          </label>
          <select 
            v-model="editingUser.projeto_atribuido" 
            required 
            class="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm bg-white font-medium"
          >
            <option value="" disabled>Selecione um dos 5 projetos...</option>
            <option v-for="(p, key) in projectOptions" :key="key" :value="key">
              {{ p.code }} — {{ p.name }}
            </option>
          </select>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" type="button" @click="closeEditModal">Cancelar</Button>
          <Button variant="primary" type="submit" :disabled="isSavingUser">
            {{ isSavingUser ? 'Salvando...' : 'Salvar Perfil' }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import Card from '../components/Card.vue';
import Modal from '../components/Modal.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import { 
  Cog6ToothIcon, 
  UserCircleIcon, 
  ShieldCheckIcon, 
  UserGroupIcon, 
  UserPlusIcon, 
  UserIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CalendarDaysIcon
} from '@heroicons/vue/24/outline';

const toast = useToast();
const authStore = useAuthStore();

const showAddUserModal = ref(false);
const showEditUserModal = ref(false);
const isLoadingUsers = ref(false);
const isSavingUser = ref(false);

interface UserRBAC {
  id: number;
  username: string;
  nome: string;
  email?: string;
  departamento?: string;
  perfil: string;
  projeto_atribuido?: string | null;
  ativo: boolean;
}

interface ADUserData {
  exists: boolean;
  username: string;
  displayName: string;
  email: string;
  department: string;
}

const projectOptions: Record<string, { code: string; name: string }> = {
  "0": { code: "P0", name: "Estruturação do Centro de Trauma e Emergência Geral" },
  "1": { code: "P1", name: "Implantação da Linha de Cuidado Cardiovascular" },
  "2": { code: "P2", name: "Otimização do Centro Cirúrgico" },
  "3": { code: "P3", name: "Modernização do Parque Tecnológico e Engenharia Clínica" },
  "4": { code: "P4", name: "Gestão do Conhecimento e Ensino em Saúde" },
};

const availableRoles = [
  { codigo: 'GERENTE_PROJETO', nome: 'Gerente de Projeto', descricao: 'Operações CRUD completas exclusivas para o projeto atribuído na II Jornada.', badgeClass: 'bg-blue-100 text-blue-800' },
  { codigo: 'ADMINISTRADOR', nome: 'Administrador', descricao: 'Acesso total irrestrito a todos os projetos, relatórios e gestão de usuários.', badgeClass: 'bg-purple-100 text-purple-800' },
  { codigo: 'GESTOR_UNIDADE', nome: 'Gestor da Unidade', descricao: 'Acompanhamento estratégico executivo da unidade.', badgeClass: 'bg-indigo-100 text-indigo-800' },
  { codigo: 'CONSULTA', nome: 'Consulta (Somente Leitura)', descricao: 'Visualização pública das métricas e acompanhamentos do painel.', badgeClass: 'bg-gray-100 text-gray-800' },
];

const usersList = ref<UserRBAC[]>([]);

const newUser = ref({
  username: '',
  nome: '',
  email: '',
  departamento: '',
  perfil: 'GERENTE_PROJETO',
  projeto_atribuido: '0',
});

const isSearchingAD = ref(false);
const adSearchStatus = ref<'idle' | 'success' | 'error'>('idle');
const adErrorMessage = ref('');
const adSearchData = ref<ADUserData | null>(null);

const editingUser = ref<UserRBAC | null>(null);

const getRoleBadgeClass = (perfil: string) => {
  const role = availableRoles.find(r => r.codigo === perfil);
  return role ? role.badgeClass : 'bg-gray-100 text-gray-700';
};

const getRoleLabel = (perfil: string) => {
  const role = availableRoles.find(r => r.codigo === perfil);
  return role ? role.nome : perfil;
};

const getProjectName = (projKey: string | null | undefined) => {
  if (projKey === null || projKey === undefined) return '';
  return projectOptions[String(projKey)]?.name || `Projeto ${projKey}`;
};

const loadUsers = async () => {
  isLoadingUsers.value = true;
  try {
    const resp = await api.get<UserRBAC[]>('/api/admin/usuarios');
    usersList.value = resp.data || [];
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Erro ao carregar lista de usuários.');
  } finally {
    isLoadingUsers.value = false;
  }
};

const searchADUser = async () => {
  const username = newUser.value.username.trim();
  if (!username) return;

  isSearchingAD.value = true;
  adSearchStatus.value = 'idle';
  adErrorMessage.value = '';
  adSearchData.value = null;

  try {
    const response = await api.get<ADUserData>(`/api/admin/ad-user-search/${encodeURIComponent(username)}`);
    const data = response.data;

    if (data && data.exists) {
      adSearchStatus.value = 'success';
      adSearchData.value = data;
      newUser.value.nome = data.displayName;
      if (data.email) newUser.value.email = data.email;
      if (data.department) newUser.value.departamento = data.department;
      toast.success(`Usuário ${data.displayName} validado no AD.`);
    } else {
      adSearchStatus.value = 'error';
      adErrorMessage.value = `Usuário '${username}' não foi localizado no Active Directory.`;
      toast.warning(`Usuário '${username}' não localizado no AD.`);
    }
  } catch (err: any) {
    adSearchStatus.value = 'error';
    adErrorMessage.value = err.response?.data?.detail || 'Erro ao consultar o Active Directory.';
    toast.error(adErrorMessage.value);
  } finally {
    isSearchingAD.value = false;
  }
};

const openAddModal = () => {
  showAddUserModal.value = true;
  newUser.value = {
    username: '',
    nome: '',
    email: '',
    departamento: '',
    perfil: 'GERENTE_PROJETO',
    projeto_atribuido: '0',
  };
  adSearchStatus.value = 'idle';
  adSearchData.value = null;
  adErrorMessage.value = '';
};

const closeAddModal = () => {
  showAddUserModal.value = false;
};

const closeEditModal = () => {
  showEditUserModal.value = false;
  editingUser.value = null;
};

const saveUser = async () => {
  if (!newUser.value.username || !newUser.value.nome) {
    toast.warning('Preencha os campos obrigatórios.');
    return;
  }

  if (newUser.value.perfil === 'GERENTE_PROJETO' && !newUser.value.projeto_atribuido) {
    toast.warning('Selecione o projeto atribuído para o Gerente de Projeto.');
    return;
  }

  isSavingUser.value = true;
  try {
    await api.post('/api/admin/usuarios', {
      username: newUser.value.username.trim(),
      nome: newUser.value.nome.trim(),
      email: newUser.value.email.trim() || undefined,
      departamento: newUser.value.departamento.trim() || undefined,
      perfil: newUser.value.perfil,
      projeto_atribuido: newUser.value.perfil === 'GERENTE_PROJETO' ? newUser.value.projeto_atribuido : null,
      ativo: true,
    });
    toast.success(`Usuário ${newUser.value.username} incluído com sucesso!`);
    closeAddModal();
    await loadUsers();
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Erro ao incluir usuário.');
  } finally {
    isSavingUser.value = false;
  }
};

const openEditModal = (user: UserRBAC) => {
  editingUser.value = { ...user };
  showEditUserModal.value = true;
};

const updateUserRole = async () => {
  if (!editingUser.value) return;

  if (editingUser.value.perfil === 'GERENTE_PROJETO' && !editingUser.value.projeto_atribuido) {
    toast.warning('Selecione o projeto atribuído.');
    return;
  }

  isSavingUser.value = true;
  try {
    await api.put(`/api/admin/usuarios/${editingUser.value.id}`, {
      perfil: editingUser.value.perfil,
      projeto_atribuido: editingUser.value.perfil === 'GERENTE_PROJETO' ? editingUser.value.projeto_atribuido : null,
    });
    toast.success('Perfil atualizado com sucesso!');
    closeEditModal();
    await loadUsers();
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Erro ao atualizar perfil.');
  } finally {
    isSavingUser.value = false;
  }
};

const toggleUserStatus = async (user: UserRBAC) => {
  const novoStatus = !user.ativo;
  try {
    await api.put(`/api/admin/usuarios/${user.id}`, {
      ativo: novoStatus,
    });
    user.ativo = novoStatus;
    toast.success(`Usuário ${user.username} ${novoStatus ? 'ativado' : 'inativado'} com sucesso!`);
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Erro ao alterar status.');
  }
};

const confirmRemoveUser = async (user: UserRBAC) => {
  if (confirm(`Deseja realmente excluir o acesso do usuário ${user.username}?`)) {
    try {
      await api.delete(`/api/admin/usuarios/${user.id}`);
      toast.success(`Usuário ${user.username} excluído com sucesso.`);
      await loadUsers();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Erro ao excluir usuário.');
    }
  }
};

interface BimestreConfig {
  id: number;
  periodo_code: string;
  periodo_nome: string;
  ativo: boolean;
  updated_by?: string;
  updated_at?: string;
}

const bimestresList = ref<BimestreConfig[]>([]);
const isLoadingBimestres = ref(false);
const updatingBimestreCode = ref<string | null>(null);

const loadBimestresConfig = async () => {
  isLoadingBimestres.value = true;
  try {
    const resp = await api.get<BimestreConfig[]>('/api/admin/bimestres-config');
    bimestresList.value = resp.data || [];
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Erro ao carregar configurações de bimestres.');
  } finally {
    isLoadingBimestres.value = false;
  }
};

const toggleBimestreStatus = async (b: BimestreConfig) => {
  const novoStatus = !b.ativo;
  updatingBimestreCode.value = b.periodo_code;
  try {
    const resp = await api.put<BimestreConfig>(`/api/admin/bimestres-config/${b.periodo_code}`, {
      ativo: novoStatus,
    });
    b.ativo = resp.data.ativo;
    toast.success(`Bimestre "${b.periodo_nome}" ${b.ativo ? 'habilitado' : 'desabilitado'} com sucesso!`);
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Erro ao alterar status do bimestre.');
  } finally {
    updatingBimestreCode.value = null;
  }
};

onMounted(() => {
  if (authStore.isAdmin) {
    loadUsers();
    loadBimestresConfig();
  }
});
</script>
