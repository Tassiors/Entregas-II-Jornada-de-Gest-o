<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 pb-16">
    <!-- Header Corporativo (Sem botão Voltar ao Painel conforme item 6) -->
    <header class="bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 text-white shadow-lg">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center space-x-4">
          <div class="w-13 h-13 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center text-3xl shadow-inner border border-white/20 p-2.5">
            📋
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold tracking-wider uppercase px-2.5 py-0.5 rounded-full bg-blue-500/30 text-blue-200 border border-blue-400/30">
                HC-UFPE · EBSERH · UGERC
              </span>
              <span v-if="recordId" class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-400/20 text-amber-200 border border-amber-400/30">
                Registro Local #{{ recordId }}
              </span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mt-1">
              Formulário de Entregas
            </h1>
            <p class="text-xs sm:text-sm text-blue-100 font-medium">
              II Jornada de Gestão do HC-UFPE · Unidade de Gestão da Estratégia, de Riscos e Controles Internos - UGERC
            </p>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-6 sm:mt-8">
      <!-- Card de Instruções Institucionais -->
      <div class="bg-white rounded-2xl p-6 shadow-md border border-slate-200/90 mb-6">
        <div class="flex items-start gap-4">
          <div class="p-2.5 bg-blue-50 text-blue-700 rounded-xl shrink-0">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="text-sm text-slate-600 leading-relaxed space-y-2">
            <h2 class="text-base font-bold text-slate-800">
              {{ schema?.title || 'Acompanhamento Entregas II Jornada de Gestão' }}
            </h2>
            <div v-if="schema?.instructions" v-html="schema.instructions" class="prose prose-sm max-w-none text-slate-600"></div>
            <div v-else class="space-y-1">
              <p>Este formulário foi desenvolvido para apoiar o acompanhamento das entregas definidas durante a <strong>II Jornada de Gestão do HC-UFPE</strong>, permitindo o registro, o monitoramento e a atualização do andamento das ações pactuadas.</p>
              <p>Os formulários respondidos via sistema são armazenados com segurança no banco de dados local da instituição, mantendo a integridade histórica e alimentando o painel executivo em tempo real.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Alerta de Restrição RBAC do Gerente de Projeto -->
      <div
        v-if="authStore.isGerenteProjeto && userProjectName"
        class="bg-blue-50 border-l-4 border-blue-600 p-4 rounded-xl shadow-sm mb-6 flex items-center justify-between gap-4"
      >
        <div class="flex items-center gap-3">
          <span class="text-2xl">🛡️</span>
          <div>
            <p class="text-sm font-bold text-blue-900">
              Acesso de Gerente de Projeto: P{{ authStore.assignedProject }} — {{ userProjectName }}
            </p>
            <p class="text-xs text-blue-700">
              Seu perfil permite operações completas de leitura, gravação, edição e exclusão referentes exclusivamente a este projeto.
            </p>
          </div>
        </div>
      </div>

      <!-- Alerta de Registro Existente Carregado -->
      <div
        v-if="existingRecordLoaded"
        class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-xl shadow-sm mb-6 flex items-center justify-between gap-4"
      >
        <div class="flex items-center gap-3">
          <span class="text-2xl">📝</span>
          <div>
            <p class="text-sm font-bold text-amber-900">
              Registro Local Existente Localizado (#{{ recordId || 'Banco Local' }})
            </p>
            <p class="text-xs text-amber-700">
              Os dados deste bimestre foram carregados para visualização ou atualização. Ao salvar, as novas informações atualizarão o banco de dados com efeito cascata.
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="recordId"
            type="button"
            @click="handleDeleteCurrentRecord"
            class="px-3 py-1.5 bg-red-100 hover:bg-red-200 text-red-700 text-xs font-bold rounded-lg transition cursor-pointer"
          >
            Excluir Registro
          </button>
          <button
            @click="resetFormForNewEntry"
            class="text-xs font-bold text-amber-900 underline hover:text-amber-700 shrink-0 cursor-pointer"
          >
            Limpar campos
          </button>
        </div>
      </div>

      <!-- Alerta de Bimestre Encerrado pelo Administrador com Permissão Mantida -->
      <div
        v-if="form.periodo && isSelectedPeriodClosed"
        class="bg-purple-50 border-l-4 border-purple-600 p-4 rounded-xl shadow-sm mb-6 flex items-center justify-between gap-4"
      >
        <div class="flex items-center gap-3">
          <span class="text-2xl">🔒</span>
          <div>
            <p class="text-sm font-bold text-purple-900">
              Bimestre Encerrado pelo Administrador — Permissões de Leitura, Edição e Exclusão Mantidas
            </p>
            <p class="text-xs text-purple-700">
              Este bimestre foi fechado para novos cadastros. Como este projeto já possui relatório submetido neste período, suas funções de <strong>leitura, atualização e remoção</strong> continuam plenamente ativas para o respectivo gerente do projeto.
            </p>
          </div>
        </div>
      </div>

      <!-- Formulário Principal -->
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Seção 1: Seleção de Projeto e Período -->
        <div class="bg-white rounded-2xl p-6 shadow-md border border-slate-200/90">
          <h3 class="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
            <span class="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-800 text-xs font-extrabold">1</span>
            Projeto e Período Bimestral
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Projeto (bloqueado se for Gerente de Projeto) -->
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Projeto <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.projeto"
                @change="onProjectOrPeriodChange"
                :disabled="authStore.isGerenteProjeto"
                required
                class="w-full bg-slate-50 border border-slate-300 text-slate-800 text-sm rounded-xl p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition cursor-pointer font-medium disabled:opacity-80 disabled:bg-slate-100"
              >
                <option value="" disabled>Selecione um projeto...</option>
                <option v-for="(p, key) in projectsList" :key="key" :value="key">
                  {{ p.code }} — {{ p.short }}
                </option>
              </select>
              <p v-if="selectedProjectMeta" class="mt-2 text-xs font-semibold text-slate-500 flex items-center gap-1.5">
                <span class="text-base">{{ selectedProjectMeta.icon }}</span>
                <span>{{ selectedProjectMeta.name }}</span>
              </p>
            </div>

            <!-- Período -->
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Período Bimestral <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.periodo"
                @change="onProjectOrPeriodChange"
                required
                class="w-full bg-slate-50 border border-slate-300 text-slate-800 text-sm rounded-xl p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition cursor-pointer font-medium"
              >
                <option value="" disabled>Selecione o bimestre...</option>
                <option
                  v-for="(label, key) in periodsList"
                  :key="key"
                  :value="key"
                  :disabled="isPeriodDisabled(key)"
                  :class="isPeriodDisabled(key) ? 'text-slate-400 bg-slate-100 italic' : ''"
                >
                  {{ getPeriodOptionLabel(key, label) }}
                </option>
              </select>
              <p v-if="checkingExisting" class="mt-2 text-xs text-blue-600 font-semibold flex items-center gap-1">
                <svg class="animate-spin w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                Verificando registros locais do bimestre...
              </p>
            </div>
          </div>
        </div>

        <!-- Seção 2: Branching Logic - Entregas E1 e E2 -->
        <div v-if="form.projeto && selectedProjectMeta" class="space-y-6">
          <!-- Card Entrega 1 -->
          <div
            class="bg-white rounded-2xl p-6 shadow-md border-t-4 border border-slate-200/90 transition-all"
            :style="{ borderTopColor: selectedProjectMeta.color }"
          >
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
              <div class="flex items-center gap-2 flex-wrap">
                <span
                  class="px-3 py-1 rounded-full text-xs font-extrabold text-white shadow-sm"
                  :style="{ backgroundColor: selectedProjectMeta.color }"
                >
                  Entrega 1
                </span>
                <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  {{ selectedProjectMeta.code }}
                </span>
                <!-- Tag de Conclusão / Efeito Cascata E1 -->
                <span
                  v-if="cascadeInfo.e1_concluida"
                  class="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs"
                >
                  ✅ Concluída em {{ cascadeInfo.e1_periodo || 'bimestre anterior' }} (efeito cascata)
                </span>
                <span
                  v-else-if="form.ent1_conc === '0'"
                  class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200"
                >
                  ✅ Concluída neste bimestre
                </span>
              </div>

              <!-- Conclusão E1 -->
              <div class="flex items-center gap-3">
                <span class="text-xs font-bold text-slate-700">Entrega Concluída?</span>
                <div class="inline-flex rounded-xl bg-slate-100 p-1 border border-slate-200">
                  <button
                    type="button"
                    @click="form.ent1_conc = '0'"
                    :class="[
                      'px-3 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer',
                      form.ent1_conc === '0'
                        ? 'bg-emerald-600 text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    ]"
                  >
                    Sim
                  </button>
                  <button
                    type="button"
                    @click="form.ent1_conc = '1'"
                    :class="[
                      'px-3 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer',
                      form.ent1_conc === '1'
                        ? 'bg-slate-700 text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    ]"
                  >
                    Não
                  </button>
                </div>
              </div>
            </div>

            <!-- Título da Entrega 1 -->
            <div class="p-4 rounded-xl bg-slate-50 border border-slate-200/80 mb-4">
              <p class="text-xs uppercase font-extrabold text-slate-400 tracking-wider mb-1">Pactuação Oficial</p>
              <p class="text-sm font-bold text-slate-800 leading-snug">
                {{ selectedProjectMeta.ent1_desc }}
              </p>
            </div>

            <!-- Textarea de Evolução E1 -->
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Comentários / Evolução da Entrega 1
                <span v-if="form.ent1_conc !== '0' && !cascadeInfo.e1_concluida" class="text-red-500">*</span>
                <span v-else class="text-slate-400 font-normal lowercase tracking-normal">(opcional após conclusão)</span>
              </label>
              <textarea
                v-model="form.ent1_txt"
                :required="form.ent1_conc !== '0' && !cascadeInfo.e1_concluida"
                rows="4"
                placeholder="Descreva as ações realizadas no período, marcos atingidos ou justificativas..."
                class="w-full bg-slate-50 border border-slate-300 text-slate-800 text-sm rounded-xl p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition font-normal"
              ></textarea>
            </div>
          </div>

          <!-- Card Entrega 2 -->
          <div
            class="bg-white rounded-2xl p-6 shadow-md border-t-4 border border-slate-200/90 transition-all"
            :style="{ borderTopColor: selectedProjectMeta.color2 || selectedProjectMeta.color }"
          >
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
              <div class="flex items-center gap-2 flex-wrap">
                <span
                  class="px-3 py-1 rounded-full text-xs font-extrabold text-white shadow-sm"
                  :style="{ backgroundColor: selectedProjectMeta.color2 || selectedProjectMeta.color }"
                >
                  Entrega 2
                </span>
                <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  {{ selectedProjectMeta.code }}
                </span>
                <!-- Tag de Conclusão / Efeito Cascata E2 -->
                <span
                  v-if="cascadeInfo.e2_concluida"
                  class="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs"
                >
                  ✅ Concluída em {{ cascadeInfo.e2_periodo || 'bimestre anterior' }} (efeito cascata)
                </span>
                <span
                  v-else-if="form.ent2_conc === '0'"
                  class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200"
                >
                  ✅ Concluída neste bimestre
                </span>
              </div>

              <!-- Conclusão E2 -->
              <div class="flex items-center gap-3">
                <span class="text-xs font-bold text-slate-700">Entrega Concluída?</span>
                <div class="inline-flex rounded-xl bg-slate-100 p-1 border border-slate-200">
                  <button
                    type="button"
                    @click="form.ent2_conc = '0'"
                    :class="[
                      'px-3 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer',
                      form.ent2_conc === '0'
                        ? 'bg-emerald-600 text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    ]"
                  >
                    Sim
                  </button>
                  <button
                    type="button"
                    @click="form.ent2_conc = '1'"
                    :class="[
                      'px-3 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer',
                      form.ent2_conc === '1'
                        ? 'bg-slate-700 text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    ]"
                  >
                    Não
                  </button>
                </div>
              </div>
            </div>

            <!-- Título da Entrega 2 -->
            <div class="p-4 rounded-xl bg-slate-50 border border-slate-200/80 mb-4">
              <p class="text-xs uppercase font-extrabold text-slate-400 tracking-wider mb-1">Pactuação Oficial</p>
              <p class="text-sm font-bold text-slate-800 leading-snug">
                {{ selectedProjectMeta.ent2_desc }}
              </p>
            </div>

            <!-- Textarea de Evolução E2 -->
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Comentários / Evolução da Entrega 2
                <span v-if="form.ent2_conc !== '0' && !cascadeInfo.e2_concluida" class="text-red-500">*</span>
                <span v-else class="text-slate-400 font-normal lowercase tracking-normal">(opcional após conclusão)</span>
              </label>
              <textarea
                v-model="form.ent2_txt"
                :required="form.ent2_conc !== '0' && !cascadeInfo.e2_concluida"
                rows="4"
                placeholder="Descreva as ações realizadas no período, marcos atingidos ou justificativas..."
                class="w-full bg-slate-50 border border-slate-300 text-slate-800 text-sm rounded-xl p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition font-normal"
              ></textarea>
            </div>
          </div>

          <!-- Nota Explicativa da Regra de Efeito Cascata -->
          <div class="p-4 rounded-xl bg-blue-50/70 border border-blue-200/80 text-xs text-blue-900 flex items-start gap-3">
            <span class="text-lg shrink-0">ℹ️</span>
            <div>
              <p class="font-bold">Regra de Efeito Cascata na Conclusão:</p>
              <p class="mt-0.5 text-blue-800">
                Ao marcar uma entrega como concluída ("Sim"), seu status permanecerá concluído nos bimestres seguintes deste projeto. Caso cancele a conclusão ("Não"), o cancelamento também se propagará para os bimestres subsequentes.
              </p>
            </div>
          </div>

          <!-- Barra de Ações do Formulário (Status do Formulário REMOVIDO conforme item 3) -->
          <div class="bg-white rounded-2xl p-6 shadow-md border border-slate-200/90 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <span class="text-xs text-slate-500 font-medium">
                Persistência direta no banco de dados local da UGERC / HC-UFPE.
              </span>
            </div>

            <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
              <button
                v-if="recordId"
                type="button"
                @click="handleDeleteCurrentRecord"
                class="px-4 py-2.5 text-xs font-bold text-red-600 hover:text-red-800 hover:bg-red-50 rounded-xl border border-red-200 transition cursor-pointer"
              >
                Excluir
              </button>
              <button
                type="button"
                @click="resetFormForNewEntry"
                class="px-4 py-2.5 text-xs font-bold text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition cursor-pointer"
              >
                Limpar
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-blue-700 hover:bg-blue-600 active:bg-blue-800 text-white text-xs font-extrabold rounded-xl shadow-md transition disabled:opacity-50 cursor-pointer"
              >
                <svg v-if="isSubmitting" class="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>{{ isSubmitting ? 'Gravando no Banco...' : (recordId ? 'Atualizar Formulário' : 'Gravar Acompanhamento') }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Placeholder se ainda não selecionou projeto -->
        <div v-else class="bg-slate-100/80 border-2 border-dashed border-slate-300 rounded-2xl p-12 text-center text-slate-500">
          <span class="text-4xl block mb-2">🎯</span>
          <p class="font-bold text-sm text-slate-700">Selecione o Projeto e o Período acima</p>
          <p class="text-xs text-slate-500 mt-1">
            As entregas pactuadas e os campos de preenchimento serão exibidos automaticamente para acompanhamento.
          </p>
        </div>
      </form>

      <!-- Seção 3: Histórico e Leitura de Formulários Gravados Localmente -->
      <div class="mt-10 bg-white rounded-2xl p-6 shadow-md border border-slate-200/90">
        <div class="flex items-center justify-between border-b pb-3 mb-4">
          <div>
            <h3 class="text-base font-bold text-slate-900 flex items-center gap-2">
              <span class="text-lg">📂</span>
              Formulários Salvos no Banco Local
            </h3>
            <p class="text-xs text-slate-500 mt-0.5">
              Consulte, edite ou exclua os acompanhamentos registrados no sistema.
            </p>
          </div>
          <button
            @click="loadSavedForms"
            class="text-xs font-semibold text-blue-700 hover:text-blue-900 px-3 py-1.5 bg-blue-50 rounded-lg transition cursor-pointer"
          >
            Atualizar Lista
          </button>
        </div>

        <div v-if="isLoadingSavedForms" class="p-6 text-center text-xs text-slate-500">
          Carregando registros...
        </div>
        <div v-else-if="savedForms.length === 0" class="p-6 text-center text-xs text-slate-400">
          Nenhum formulário salvo no banco local para o projeto selecionado.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-600">
            <thead class="bg-slate-50 font-bold uppercase text-[10px] text-slate-500 border-b">
              <tr>
                <th class="py-2.5 px-3">ID</th>
                <th class="py-2.5 px-3">Projeto</th>
                <th class="py-2.5 px-3">Bimestre</th>
                <th class="py-2.5 px-3">Entrega 1</th>
                <th class="py-2.5 px-3">Entrega 2</th>
                <th class="py-2.5 px-3">Responsável</th>
                <th class="py-2.5 px-3 text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in savedForms" :key="item.id" class="hover:bg-slate-50/80 transition-colors">
                <td class="py-2.5 px-3 font-mono font-bold text-slate-800">#{{ item.id }}</td>
                <td class="py-2.5 px-3 font-medium text-slate-800">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800">P{{ item.projeto }}</span>
                </td>
                <td class="py-2.5 px-3 font-semibold">{{ item.var_periodo || `B${Number(item.periodo) + 1}` }}</td>
                <td class="py-2.5 px-3">
                  <span :class="item.ent1_conc === '0' ? 'text-emerald-700 bg-emerald-50' : 'text-slate-600 bg-slate-100'" class="px-2 py-0.5 rounded font-bold text-[10px]">
                    {{ item.ent1_conc === '0' ? 'Concluída' : 'Em andamento' }}
                  </span>
                </td>
                <td class="py-2.5 px-3">
                  <span :class="item.ent2_conc === '0' ? 'text-emerald-700 bg-emerald-50' : 'text-slate-600 bg-slate-100'" class="px-2 py-0.5 rounded font-bold text-[10px]">
                    {{ item.ent2_conc === '0' ? 'Concluída' : 'Em andamento' }}
                  </span>
                </td>
                <td class="py-2.5 px-3 font-mono text-slate-500">{{ item.usuario_registro }}</td>
                <td class="py-2.5 px-3 text-right space-x-2 whitespace-nowrap">
                  <button
                    @click="loadSavedFormIntoEditor(item)"
                    class="px-2.5 py-1 text-[11px] font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-md transition cursor-pointer"
                  >
                    Carregar
                  </button>
                  <button
                    @click="deleteSavedForm(item.id)"
                    class="px-2 py-1 text-[11px] font-bold text-red-600 hover:bg-red-50 rounded-md transition cursor-pointer"
                  >
                    Excluir
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Modal de Agradecimento Institucional Oficial -->
    <div
      v-if="showSuccessModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-fade-in"
    >
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-slate-100 transform transition-all text-center">
        <div class="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-3xl mx-auto mb-4 shadow-inner">
          ✓
        </div>
        <h3 class="text-xl font-extrabold text-slate-900 mb-2">
          Entrega Salva com Sucesso!
        </h3>
        <p class="text-xs font-semibold text-blue-600 mb-4 uppercase tracking-wider">
          Registro Local #{{ savedRecordId }}
        </p>

        <div class="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-xs sm:text-sm text-slate-700 leading-relaxed text-left mb-6">
          <p class="font-bold text-slate-900 mb-1">Agradecimento</p>
          <p>
            {{ acknowledgementText }}
          </p>
        </div>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            @click="handleNewEntryAfterSuccess"
            class="w-full sm:w-auto px-5 py-2.5 bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 text-xs font-bold rounded-xl transition cursor-pointer"
          >
            Preencher Outro Bimestre
          </button>
          <router-link
            :to="{ path: '/entregas', query: { projeto: form.projeto } }"
            class="w-full sm:w-auto px-6 py-2.5 bg-blue-700 hover:bg-blue-600 active:bg-blue-800 text-white text-xs font-extrabold rounded-xl shadow-md transition text-center cursor-pointer"
          >
            Ver no Painel Executivo
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useToast } from 'vue-toastification';
import { useAuthStore } from '../../stores/auth';
import {
  entregasService,
  FormSchemaResponse,
  FormProjectMeta,
  BimestreStatusItem,
} from '../../services/entregasService';

const toast = useToast();
const route = useRoute();
const authStore = useAuthStore();

const schema = ref<FormSchemaResponse | null>(null);
const recordId = ref<string | null>(null);
const existingRecordLoaded = ref(false);
const checkingExisting = ref(false);
const isSubmitting = ref(false);
const showSuccessModal = ref(false);
const savedRecordId = ref('');
const acknowledgementText = ref('');
const isLoadingSavedForms = ref(false);
const savedForms = ref<any[]>([]);

const bimestresStatus = ref<Record<string, BimestreStatusItem>>({});
const isLoadingBimestresStatus = ref(false);

const loadBimestresStatus = async () => {
  isLoadingBimestresStatus.value = true;
  try {
    const proj = form.projeto || (authStore.isGerenteProjeto ? authStore.assignedProject : undefined);
    const data = await entregasService.getBimestresStatus(proj || undefined);
    bimestresStatus.value = data || {};
  } catch (err) {
    console.error('Erro ao carregar status dos bimestres:', err);
  } finally {
    isLoadingBimestresStatus.value = false;
  }
};

const isSelectedPeriodClosed = computed(() => {
  if (!form.periodo || !bimestresStatus.value[form.periodo]) return false;
  return !bimestresStatus.value[form.periodo].ativo;
});

const isPeriodDisabled = (key: string) => {
  const st = bimestresStatus.value[key];
  if (!st) return false;
  return !st.can_fill;
};

const getPeriodOptionLabel = (key: string, label: string) => {
  const st = bimestresStatus.value[key];
  const baseLabel = `B${Number(key) + 1} — ${label}`;
  if (!st) return baseLabel;
  if (!st.ativo) {
    if (st.has_submission) {
      return `${baseLabel} (Encerrado - Edição mantida)`;
    }
    return `${baseLabel} (Inativo para novo preenchimento)`;
  }
  return baseLabel;
};

const cascadeInfo = ref({
  e1_concluida: false,
  e1_periodo: null as string | null,
  e2_concluida: false,
  e2_periodo: null as string | null,
});

const form = reactive({
  projeto: '',
  periodo: '',
  ent1_conc: '1',
  ent1_txt: '',
  ent2_conc: '1',
  ent2_txt: '',
});

const projectsList = computed<Record<string, FormProjectMeta>>(() => {
  return schema.value?.projects || {};
});

const periodsList = computed<Record<string, string>>(() => {
  return schema.value?.periods || {};
});

const selectedProjectMeta = computed<FormProjectMeta | null>(() => {
  if (!form.projeto || !schema.value?.projects) return null;
  return schema.value.projects[form.projeto] || null;
});

const userProjectName = computed(() => {
  if (authStore.assignedProject && schema.value?.projects) {
    return schema.value.projects[authStore.assignedProject]?.name || `Projeto ${authStore.assignedProject}`;
  }
  return '';
});

const checkExistingRecord = async () => {
  if (!form.projeto || !form.periodo) return;

  checkingExisting.value = true;
  try {
    const res = await entregasService.findExistingRecord(form.projeto, form.periodo);

    if (res.cascade_info) {
      cascadeInfo.value = {
        e1_concluida: Boolean(res.cascade_info.e1_concluida),
        e1_periodo: res.cascade_info.e1_periodo || null,
        e2_concluida: Boolean(res.cascade_info.e2_concluida),
        e2_periodo: res.cascade_info.e2_periodo || null,
      };
    } else {
      cascadeInfo.value = { e1_concluida: false, e1_periodo: null, e2_concluida: false, e2_periodo: null };
    }

    if (res.record) {
      recordId.value = res.record.record_id || null;
      form.ent1_conc = res.record.ent1_conc || (cascadeInfo.value.e1_concluida ? '0' : '1');
      form.ent1_txt = res.record.ent1_txt || '';
      form.ent2_conc = res.record.ent2_conc || (cascadeInfo.value.e2_concluida ? '0' : '1');
      form.ent2_txt = res.record.ent2_txt || '';
      existingRecordLoaded.value = Boolean(res.exists);

      if (res.exists) {
        toast.info(`Dados do projeto para o período carregados.`);
      } else if (cascadeInfo.value.e1_concluida || cascadeInfo.value.e2_concluida) {
        toast.info('Status de entrega concluída em bimestre anterior aplicado automaticamente (efeito cascata).');
      }
    } else {
      recordId.value = null;
      existingRecordLoaded.value = false;
      form.ent1_conc = cascadeInfo.value.e1_concluida ? '0' : '1';
      form.ent1_txt = '';
      form.ent2_conc = cascadeInfo.value.e2_concluida ? '0' : '1';
      form.ent2_txt = '';
      if (cascadeInfo.value.e1_concluida || cascadeInfo.value.e2_concluida) {
        toast.info('Status de entrega concluída em bimestre anterior aplicado automaticamente (efeito cascata).');
      }
    }
  } catch (err: any) {
    toast.error('Erro ao verificar registro existente.');
  } finally {
    checkingExisting.value = false;
  }
};

const onProjectOrPeriodChange = () => {
  loadBimestresStatus();
  checkExistingRecord();
  loadSavedForms();
};

const resetFormForNewEntry = () => {
  recordId.value = null;
  existingRecordLoaded.value = false;
  form.ent1_conc = cascadeInfo.value.e1_concluida ? '0' : '1';
  form.ent1_txt = '';
  form.ent2_conc = cascadeInfo.value.e2_concluida ? '0' : '1';
  form.ent2_txt = '';
  toast.info('Campos limpos para novo registro.');
};

const loadSavedForms = async () => {
  isLoadingSavedForms.value = true;
  try {
    const projFilter = authStore.isGerenteProjeto ? authStore.assignedProject : (form.projeto || undefined);
    savedForms.value = await entregasService.listFormularios(projFilter || undefined);
  } catch (err) {
    console.error('Erro ao carregar lista de formulários salvos:', err);
  } finally {
    isLoadingSavedForms.value = false;
  }
};

const loadSavedFormIntoEditor = (item: any) => {
  form.projeto = item.projeto;
  form.periodo = item.periodo;
  form.ent1_conc = item.ent1_conc;
  form.ent1_txt = item.ent1_txt;
  form.ent2_conc = item.ent2_conc;
  form.ent2_txt = item.ent2_txt;
  recordId.value = String(item.id);
  existingRecordLoaded.value = true;
  window.scrollTo({ top: 200, behavior: 'smooth' });
  toast.info(`Formulário #${item.id} carregado para edição.`);
};

const handleDeleteCurrentRecord = async () => {
  if (!recordId.value) return;
  if (confirm(`Tem certeza que deseja excluir o formulário #${recordId.value}?`)) {
    try {
      await entregasService.deleteFormulario(Number(recordId.value));
      toast.success(`Formulário #${recordId.value} excluído com sucesso!`);
      resetFormForNewEntry();
      await loadSavedForms();
      await loadBimestresStatus();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Erro ao excluir formulário.');
    }
  }
};

const deleteSavedForm = async (id: number) => {
  if (confirm(`Tem certeza que deseja excluir o formulário #${id}?`)) {
    try {
      await entregasService.deleteFormulario(id);
      toast.success(`Formulário #${id} excluído com sucesso!`);
      if (recordId.value === String(id)) {
        resetFormForNewEntry();
      }
      await loadSavedForms();
      await loadBimestresStatus();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Erro ao excluir formulário.');
    }
  }
};

const handleSubmit = async () => {
  if (!form.projeto || !form.periodo) {
    toast.warning('Selecione o Projeto e o Período.');
    return;
  }

  // Validação: se a entrega NÃO estiver concluída, o comentário é obrigatório
  if (form.ent1_conc === '1' && !cascadeInfo.value.e1_concluida && !form.ent1_txt.trim()) {
    toast.warning('O comentário da Entrega 1 é obrigatório enquanto a entrega não estiver concluída.');
    return;
  }

  if (form.ent2_conc === '1' && !cascadeInfo.value.e2_concluida && !form.ent2_txt.trim()) {
    toast.warning('O comentário da Entrega 2 é obrigatório enquanto a entrega não estiver concluída.');
    return;
  }

  if (authStore.isGerenteProjeto && authStore.assignedProject) {
    form.projeto = authStore.assignedProject;
  }

  isSubmitting.value = true;
  try {
    const payload = {
      record_id: recordId.value || undefined,
      projeto: form.projeto,
      periodo: form.periodo,
      ent1_conc: form.ent1_conc,
      ent1_txt: form.ent1_txt.trim(),
      ent2_conc: form.ent2_conc,
      ent2_txt: form.ent2_txt.trim(),
    };

    // Submissão unificada que garante criação ou atualização direta no banco local
    const res = await entregasService.submitForm(payload);

    savedRecordId.value = String(res.record_id || res.id || 'OK');
    acknowledgementText.value = res.acknowledgement || schema.value?.acknowledgement || '';
    toast.success('Formulário gravado com sucesso no banco de dados local!');
    showSuccessModal.value = true;
    await loadSavedForms();
    await loadBimestresStatus();
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Erro ao salvar formulário.');
  } finally {
    isSubmitting.value = false;
  }
};

const handleNewEntryAfterSuccess = () => {
  showSuccessModal.value = false;
  resetFormForNewEntry();
};

onMounted(async () => {
  try {
    schema.value = await entregasService.getFormSchema();

    // Se o usuário logado for Gerente de Projeto, pré-seleciona e fixa seu projeto atribuído
    if (authStore.isGerenteProjeto && authStore.assignedProject) {
      form.projeto = authStore.assignedProject;
    } else if (route.query.projeto) {
      form.projeto = String(route.query.projeto);
    }

    if (route.query.periodo && route.query.periodo !== 'all') {
      form.periodo = String(route.query.periodo);
    }

    await loadBimestresStatus();
    if (form.projeto && form.periodo) {
      await checkExistingRecord();
    }
    await loadSavedForms();
  } catch (err) {
    toast.error('Erro ao carregar estrutura do formulário.');
  }
});
</script>
