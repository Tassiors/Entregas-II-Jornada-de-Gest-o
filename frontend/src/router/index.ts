import { createRouter, createWebHistory, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import PainelEntregas from '../views/entregas/PainelEntregas.vue';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Configuracoes from '../views/Configuracoes.vue';
import Exemplos from '../views/Exemplos.vue';
import Pacientes from '../views/Pacientes.vue';

const routes = [
  {
    path: '/',
    name: 'Entregas',
    component: PainelEntregas,
  },
  {
    path: '/entregas',
    name: 'PainelEntregas',
    component: PainelEntregas,
  },
  {
    path: '/home',
    name: 'Início',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'LoginLayout' },
  },
  {
    path: '/componentes',
    name: 'Componentes',
    component: Exemplos,
  },
  {
    path: '/exemplo',
    name: 'Exemplo',
    component: Pacientes,
    meta: { requiresAuth: true },
  },
  {
    path: '/configuracoes',
    name: 'Configuracoes',
    component: Configuracoes,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  linkActiveClass: 'bg-paper-active-link',
  linkExactActiveClass: 'bg-paper-active-link',
});

router.beforeEach((to, _from, next: NavigationGuardNext) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;