import {
  createRouter,
  createWebHistory
} from "vue-router";

// =====================================================
// VISTAS PRINCIPALES
// =====================================================

import Home from "../views/Home.vue";


// =====================================================
// RUTAS
// =====================================================

const routes = [

  // ===================================================
  // HOME / LANDING
  // ===================================================

    {
      path: "/",
      name: "Home",
      component: Home,

      meta: {
        title: "Nova Iuris | Inteligencia Jurídica"
      }
    },

    {
      path: "/mike",
      name: "Mike",
      component: () =>
        import("../views/MikeView.vue"),

      meta: {
        title: "MIKE | Legal Intelligence"
      }
    },

    {
      path: "/novasearch",
      name: "NovaSearch",
      component: () =>
        import("../views/NovaSearchView.vue"),

      meta: {
        title: "Nova Search | Nova Iuris"
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
    component: () => import("../views/NovaCaseView.vue"),

    meta: {
      title: "Nova Case | Nova Iuris"
    }
  },


  // ===================================================
  // NOVA COURT
  // Tribunal multiagente y simulación jurídica
  // ===================================================

  {
    path: "/novacourt",
    name: "NovaCourt",
    component: () =>
      import("../views/NovaCourtView.vue"),

    meta: {
      title: "Nova Court | Nova Iuris"
    }
  },


  // ===================================================
  // PROCESAMIENTO DEL CASO
  // SISTEMA INTERNO EXISTENTE
  // ===================================================

  {
    path: "/process/:projectId",
    name: "Process",
    component: () => import("../views/MainView.vue"),
    props: true,

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
    "Nova Iuris | Inteligencia Jurídica";

});


// =====================================================
// EXPORTACIÓN
// =====================================================

export default router;
