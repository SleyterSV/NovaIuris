import {
  createRouter,
  createWebHistory
} from "vue-router";

// =====================================================
// VISTAS PRINCIPALES
// =====================================================

import MikeView from "../views/MikeView.vue";


// =====================================================
// RUTAS
// =====================================================

const routes = [

  // ===================================================
  // HOME / LANDING
  // ===================================================

    {
      path: "/",
      name: "Mike",
      component: MikeView,

      meta: {
        title: "MYKE | Legal Intelligence"
      }
    },

    {
      path: "/mike",
      redirect: to => ({ path:'/', query:to.query }),

      meta: {
        title: "MYKE | Legal Intelligence"
      }
    },

    {
      path: "/novasearch",
      name: "NovaSearch",
      redirect: to => ({ path:'/', query:{ tool:'search', ...(typeof to.query.q === 'string' ? { q:to.query.q } : {}) } }),

      meta: {
        title: "MYKE | Buscar"
      }
    },

  // ===================================================
  // NOVA SEARCH
  // Búsqueda jurídica inteligente
  // ===================================================




  // ===================================================
  // NOVA CASE
  // Análisis y estructuración de casos
  // ===================================================

  {
    path: "/novacase",
    name: "NovaCase",
    redirect: { path:'/', query:{ tool:'case' } },

    meta: {
      title: "MYKE | Analizar"
    }
  },


  // ===================================================
  // NOVA COURT
  // Tribunal multiagente y simulación jurídica
  // ===================================================

  {
    path: "/novacourt",
    name: "NovaCourt",
    redirect: to => ({ path:'/', query:{ tool:'court', ...(typeof to.query.case_id === 'string' ? { case_id:to.query.case_id } : {}) } }),

    meta: {
      title: "MYKE | Simular"
    }
  },
  { path:'/buscar', redirect:{ path:'/', query:{ tool:'search' } } },
  { path:'/analizar', redirect:{ path:'/', query:{ tool:'case' } } },
  { path:'/simular', redirect:{ path:'/', query:{ tool:'court' } } },
  { path:'/about', name:'AboutMYKE', component:() => import('../views/MainView.vue'), meta:{ title:'Acerca de MYKE' } },


  // ===================================================
  // PROCESAMIENTO DEL CASO
  // SISTEMA INTERNO EXISTENTE
  // ===================================================

  {
    path: "/process/:projectId",
    name: "Process",
    redirect: { path:'/', query:{ tool:'case' } },

    meta: {
      title: "Procesando Caso | Nova Iuris"
    }
  },


  // ===================================================
  // SIMULACIÓN
  // ===================================================

  {
    path: "/simulation/:simulationId",
    name: "Simulation",
    component: () => import("../views/SimulationView.vue"),
    props: true,

    meta: {
      title: "Simulación Jurídica | Nova Iuris"
    }
  },


  // ===================================================
  // EJECUCIÓN DE SIMULACIÓN
  // ===================================================

  {
    path: "/simulation/:simulationId/start",
    name: "SimulationRun",
    component: () => import("../views/SimulationRunView.vue"),
    props: true,

    meta: {
      title: "Ejecutando Simulación | Nova Iuris"
    }
  },


  // ===================================================
  // REPORTES
  // ===================================================

  {
    path: "/report/:reportId",
    name: "Report",
    component: () => import("../views/ReportView.vue"),
    props: true,

    meta: {
      title: "Reporte Jurídico | Nova Iuris"
    }
  },


  // ===================================================
  // INTERACCIÓN CON RESULTADOS
  // ===================================================

  {
    path: "/interaction/:reportId",
    name: "Interaction",
    component: () => import("../views/InteractionView.vue"),
    props: true,

    meta: {
      title: "Análisis Jurídico | Nova Iuris"
    }
  },


  // ===================================================
  // RUTA NO ENCONTRADA
  // ===================================================

  {
    path: "/:pathMatch(.*)*",
    redirect: "/"
  }

];


// =====================================================
// CREACIÓN DEL ROUTER
// =====================================================

const router = createRouter({

  history: createWebHistory(),

  routes,

  scrollBehavior(to, from, savedPosition) {

    if (savedPosition) {
      return savedPosition;
    }

    return {
      top: 0,
      behavior: "smooth"
    };

  }

});


// =====================================================
// TÍTULO DINÁMICO DEL NAVEGADOR
// =====================================================

router.afterEach((to) => {

  document.title =
    to.meta.title ||
    "MYKE | Legal Intelligence";

});


// =====================================================
// EXPORTACIÓN
// =====================================================

export default router;
