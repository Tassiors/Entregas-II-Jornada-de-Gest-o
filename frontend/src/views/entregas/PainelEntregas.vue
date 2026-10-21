<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 pb-12">
    <!-- Header Corporativo (Sem o botão 'Preencher Acompanhamento' conforme item 11) -->
    <header class="bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 text-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div class="flex items-center space-x-4">
            <div class="w-14 h-14 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center text-3xl shadow-inner border border-white/20">
              🏥
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold tracking-wider uppercase px-2.5 py-0.5 rounded-full bg-blue-500/30 text-blue-200 border border-blue-400/30">
                  HC-UFPE · EBSERH · UGERC
                </span>
                <span v-if="store.lastSync" class="text-xs text-blue-200/80">
                  Atualizado: {{ store.lastSync }}
                </span>
              </div>
              <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mt-1">
                II Jornada de Gestão HC-UFPE
              </h1>
              <p class="text-sm text-blue-100 font-medium">
                Painel Corporativo de Acompanhamento de Entregas Estratégicas · Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC
              </p>
            </div>
          </div>

          <!-- Botão de Atualização -->
          <div class="flex items-center">
            <button
              @click="handleManualSync"
              :disabled="store.syncing"
              class="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md transition-all duration-200 disabled:opacity-50 cursor-pointer"
              title="Recarregar dados do banco local e REDCap"
            >
              <svg
                :class="['w-4 h-4', { 'animate-spin': store.syncing }]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              <span>{{ store.syncing ? 'Atualizando...' : 'Atualizar Dados' }}</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Conteúdo Principal -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6 sm:mt-8">
      <!-- Loading State -->
      <div v-if="store.loading && !store.dashboard" class="bg-white rounded-2xl p-12 text-center shadow-lg border border-slate-200">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-4"></div>
        <h3 class="text-lg font-bold text-slate-700">Carregando dados da II Jornada...</h3>
        <p class="text-sm text-slate-500">Consolidando informações dos projetos estratégicos</p>
      </div>

      <!-- Error State -->
      <div v-else-if="store.error" class="bg-rose-50 border-l-4 border-rose-500 rounded-xl p-4 shadow-md mb-6">
        <div class="flex items-center gap-3">
          <span class="text-2xl">⚠️</span>
          <div>
            <h4 class="text-sm font-bold text-rose-800">Falha ao carregar dados</h4>
            <p class="text-xs text-rose-700">{{ store.error }}</p>
          </div>
        </div>
      </div>

      <div v-else-if="store.dashboard" class="space-y-6">
        <!-- Matriz de Resumo Executivo por Projeto (Cards Seletores) -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-200/90">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
            <div>
              <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
                <span>🎯</span> Matriz Geral de Entregas dos 5 Projetos
              </h2>
              <p class="text-xs text-slate-500 mt-0.5">
                Visão consolidada da conclusão das entregas E1 e E2 (efeito cascata bimestral aplicado)
              </p>
            </div>
            <div class="flex items-center gap-3 text-xs">
              <span class="inline-flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Concluída</span>
              <span class="inline-flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-slate-300"></span> Em andamento</span>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mt-4">
            <div
              v-for="p in store.matrix"
              :key="p.proj_key"
              @click="store.setProject(p.proj_key)"
              :class="[
                'p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between',
                store.selectedProjectKey === p.proj_key
                  ? 'border-blue-600 bg-blue-50/40 ring-2 ring-blue-500/20 shadow-sm'
                  : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100/60'
              ]"
            >
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span
                    class="px-2 py-0.5 rounded text-[10px] font-black text-white"
                    :style="{ backgroundColor: p.color }"
                  >
                    {{ p.code }}
                  </span>
                  <span class="text-base">{{ p.icon }}</span>
                </div>
                <h3 class="text-xs font-bold text-slate-800 line-clamp-2 leading-snug" :title="p.name">
                  {{ p.short }}
                </h3>
              </div>

              <div class="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold text-white transition-all',
                      p.e1_done ? 'bg-emerald-600 shadow-sm' : 'bg-slate-300 text-slate-600'
                    ]"
                    :title="`E1: ${p.ent1_desc}`"
                  >
                    E1
                  </span>
                  <span
                    :class="[
                      'w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold text-white transition-all',
                      p.e2_done ? 'bg-emerald-600 shadow-sm' : 'bg-slate-300 text-slate-600'
                    ]"
                    :title="`E2: ${p.ent2_desc}`"
                  >
                    E2
                  </span>
                </div>

                <!-- Tag indicativa de metas do projeto -->
                <span
                  v-if="p.e1_done && p.e2_done"
                  class="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs"
                >
                  ✅ 2/2 Metas
                </span>
                <span
                  v-else-if="p.e1_done || p.e2_done"
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200"
                >
                  ⚡ 1/2 Concluída
                </span>
                <span
                  v-else
                  class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-500 border border-slate-200"
                >
                  ⏳ Em andamento
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Detalhamento do Projeto Selecionado -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden">
          <!-- Conteúdo do Projeto Selecionado -->
          <div v-if="store.activeProject" class="p-6 sm:p-8 space-y-8">
            <!-- Banner do Projeto -->
            <div
              class="p-6 rounded-2xl bg-gradient-to-r from-slate-50 via-white to-slate-50 border-l-8 shadow-sm"
              :style="{ borderLeftColor: store.activeProject.color }"
            >
              <div class="flex items-start gap-4">
                <span class="text-3xl p-3 rounded-2xl bg-white shadow-sm border border-slate-200">
                  {{ store.activeProject.icon }}
                </span>
                <div>
                  <div class="flex items-center gap-2">
                    <span
                      class="px-2.5 py-0.5 rounded-full text-xs font-black text-white shadow-sm"
                      :style="{ backgroundColor: store.activeProject.color }"
                    >
                      {{ store.activeProject.code }}
                    </span>
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Projeto Estratégico · II Jornada de Gestão
                    </span>
                  </div>
                  <h2 class="text-xl sm:text-2xl font-bold text-slate-900 mt-1">
                    {{ store.activeProject.name }}
                  </h2>
                </div>
              </div>
            </div>

            <!-- Grade dos 6 Bimestres -->
            <div class="bg-slate-50/80 rounded-2xl p-5 border border-slate-200/80">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div class="flex items-center gap-2">
                  <span class="text-base">📅</span>
                  <span class="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Acompanhamento Bimestral do Ciclo
                  </span>
                </div>
                <span class="text-xs font-bold text-slate-700 bg-white px-3 py-1 rounded-full border border-slate-200">
                  {{ store.activeProject.bimonthly.filter(b => b.entregue).length }} de 6 bimestres informados
                </span>
              </div>

              <!-- Track de Bimestres -->
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                <div
                  v-for="b in store.activeProject.bimonthly"
                  :key="b.code"
                  :class="[
                    'flex flex-col items-center justify-center p-3 rounded-xl border transition-all text-center',
                    b.entregue
                      ? 'bg-emerald-50/80 border-emerald-200 text-emerald-900 shadow-sm'
                      : 'bg-white border-slate-200 text-slate-400 opacity-80',
                    store.selectedPeriod === b.code ? 'ring-2 ring-blue-500 font-bold' : ''
                  ]"
                >
                  <span
                    :class="[
                      'w-7 h-7 rounded-full flex items-center justify-center text-xs font-black mb-1',
                      b.entregue ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-500'
                    ]"
                  >
                    {{ b.num_label }}
                  </span>
                  <span class="text-[11px] font-semibold leading-tight">{{ b.short_name }}</span>
                  <span class="text-[10px] mt-0.5 text-slate-500">
                    {{ b.entregue ? `${b.count} registro(s)` : 'Sem registro' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Descrições Oficiais das Entregas (E1 e E2) -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- E1 -->
              <div
                class="bg-white rounded-2xl p-5 border-t-4 shadow-sm border border-slate-200 flex flex-col justify-between"
                :style="{ borderTopColor: store.activeProject.color }"
              >
                <div>
                  <div class="flex items-center justify-between gap-2 mb-2">
                    <div class="flex items-center gap-2">
                      <span class="text-lg">📦</span>
                      <h3 class="text-xs font-extrabold uppercase tracking-wider text-slate-800">
                        Entrega 1 Pactuada
                      </h3>
                    </div>
                    <!-- Tag de Conclusão E1 -->
                    <span
                      v-if="store.activeProject.e1_done"
                      class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs"
                    >
                      <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                      ✅ Concluída
                    </span>
                    <span
                      v-else
                      class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200"
                    >
                      ⏳ Em andamento
                    </span>
                  </div>
                  <p class="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium">
                    {{ store.activeProject.ent1_desc }}
                  </p>
                </div>
              </div>

              <!-- E2 -->
              <div
                class="bg-white rounded-2xl p-5 border-t-4 shadow-sm border border-slate-200 flex flex-col justify-between"
                :style="{ borderTopColor: store.activeProject.color2 }"
              >
                <div>
                  <div class="flex items-center justify-between gap-2 mb-2">
                    <div class="flex items-center gap-2">
                      <span class="text-lg">📦</span>
                      <h3 class="text-xs font-extrabold uppercase tracking-wider text-slate-800">
                        Entrega 2 Pactuada
                      </h3>
                    </div>
                    <!-- Tag de Conclusão E2 -->
                    <span
                      v-if="store.activeProject.e2_done"
                      class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs"
                    >
                      <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                      ✅ Concluída
                    </span>
                    <span
                      v-else
                      class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200"
                    >
                      ⏳ Em andamento
                    </span>
                  </div>
                  <p class="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium">
                    {{ store.activeProject.ent2_desc }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Linha do Tempo de Evolução e Entregas -->
            <div class="space-y-6">
              <div class="flex items-center gap-2 border-b border-slate-200 pb-3">
                <span class="text-lg">⏱️</span>
                <h3 class="text-sm font-extrabold tracking-wide uppercase text-slate-800">
                  Linha do Tempo de Registros e Evolução
                </h3>
              </div>

              <div v-if="store.activeProject.timeline.length === 0" class="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200 text-slate-500 text-xs">
                Nenhum registro validado encontrado para este projeto no período selecionado.
              </div>

              <div v-else class="space-y-6 relative before:absolute before:inset-0 before:left-3 before:w-0.5 before:bg-slate-200">
                <div
                  v-for="(item, idx) in store.activeProject.timeline"
                  :key="idx"
                  class="relative pl-8 space-y-3"
                >
                  <!-- Marcador de Período -->
                  <div class="flex items-center gap-3">
                    <div
                      class="absolute left-1.5 w-3.5 h-3.5 rounded-full border-2 border-white shadow-sm"
                      :style="{ backgroundColor: store.activeProject.color }"
                    ></div>
                    <span class="px-3 py-1 rounded-full text-xs font-bold text-white shadow-sm" :style="{ backgroundColor: store.activeProject.color }">
                      {{ item.periodo_label }}
                    </span>
                    <span v-if="item.usuario_registro" class="text-[11px] text-slate-400 font-mono">
                      Registrado por: {{ item.usuario_registro }}
                    </span>
                  </div>

                  <!-- Cards de E1 e E2 deste Período -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Card E1 -->
                    <div
                      class="bg-white p-5 rounded-2xl border-t-4 shadow-sm border border-slate-200/90 flex flex-col justify-between"
                      :style="{ borderTopColor: store.activeProject.color }"
                    >
                      <div>
                        <div class="flex items-center justify-between gap-2 mb-2">
                          <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                            Entrega 1
                          </span>
                          <span
                            :class="[
                              'px-2.5 py-0.5 rounded-full text-[11px] font-bold',
                              item.ent1_conc === '0'
                                ? 'bg-emerald-100 text-emerald-800'
                                : item.ent1_conc === '1'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-600'
                            ]"
                          >
                            {{ item.ent1_status }}
                          </span>
                        </div>
                        <p class="text-xs font-semibold text-slate-700 mb-2">
                          {{ store.activeProject.ent1_desc }}
                        </p>
                        <div class="p-3 bg-slate-50 rounded-xl text-xs text-slate-600 leading-relaxed whitespace-pre-line border border-slate-100">
                          {{ item.ent1_txt }}
                        </div>
                      </div>
                    </div>

                    <!-- Card E2 -->
                    <div
                      class="bg-white p-5 rounded-2xl border-t-4 shadow-sm border border-slate-200/90 flex flex-col justify-between"
                      :style="{ borderTopColor: store.activeProject.color2 }"
                    >
                      <div>
                        <div class="flex items-center justify-between gap-2 mb-2">
                          <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                            Entrega 2
                          </span>
                          <span
                            :class="[
                              'px-2.5 py-0.5 rounded-full text-[11px] font-bold',
                              item.ent2_conc === '0'
                                ? 'bg-emerald-100 text-emerald-800'
                                : item.ent2_conc === '1'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-600'
                            ]"
                          >
                            {{ item.ent2_status }}
                          </span>
                        </div>
                        <p class="text-xs font-semibold text-slate-700 mb-2">
                          {{ store.activeProject.ent2_desc }}
                        </p>
                        <div class="p-3 bg-slate-50 rounded-xl text-xs text-slate-600 leading-relaxed whitespace-pre-line border border-slate-100">
                          {{ item.ent2_txt }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Rodapé Corporativo com Nomenclatura UGERC (Item 12) -->
    <footer class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 text-center text-xs text-slate-400">
      <p>Hospital das Clínicas da UFPE · Empresa Brasileira de Serviços Hospitalares (EBSERH)</p>
      <p class="mt-1">Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC · II Jornada de Gestão 2026–2027</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useToast } from 'vue-toastification';
import { useEntregasStore } from '../../stores/entregas';

const route = useRoute();
const toast = useToast();
const store = useEntregasStore();

async function handleManualSync() {
  try {
    await store.syncData();
    toast.success('Dados atualizados com sucesso!');
  } catch (err) {
    toast.error('Erro ao atualizar dados do painel.');
  }
}

onMounted(async () => {
  await store.loadDashboard();
  if (route.query.projeto) {
    store.setProject(String(route.query.projeto));
  }
});
</script>