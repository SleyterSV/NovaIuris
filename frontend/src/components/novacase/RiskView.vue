<template>
<section class="risk-view">
  <h2>Evaluación de riesgos</h2>
  <AnalysisSection v-for="(content, key) in sections" :key="key" :title="key" :content="content" />
</section>
</template>
<script setup>
import { computed } from 'vue'
import AnalysisSection from '@/components/common/AnalysisSection.vue'
const props = defineProps({ risk: { type: Object, default: () => ({}) } })
const sections = computed(() => ({
  'Riesgos procesales': props.risk.procedural,
  'Riesgos probatorios': props.risk.evidentiary,
  'Riesgos jurídicos': props.risk.legal,
  'Riesgos críticos': props.risk.strategic,
  'Valoración cualitativa': props.risk.risk_level,
  'Recomendaciones': props.risk.recommendations
}))
</script>
<style scoped>

/* =========================================================
   BASE
========================================================= */

.risk-view {

    --nova-navy: #0f2747;

    --nova-blue: #2563eb;

    --nova-blue-light: #eff6ff;

    --nova-border: #dbe4ef;

    --nova-text: #334e68;

    --nova-muted: #64748b;

    --nova-bg: #f8fafc;

    display: flex;

    flex-direction: column;

    gap: 28px;

    width: 100%;

    padding: 34px;

    background: #ffffff;

    border: 1px solid var(--nova-border);

    border-radius: 24px;

    box-shadow:
        0 10px 35px rgba(15, 39, 71, 0.06);

    color: var(--nova-text);

    box-sizing: border-box;

}


/* =========================================================
   HEADER
========================================================= */

.risk-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 30px;

    padding-bottom: 26px;

    border-bottom: 1px solid var(--nova-border);

}

.risk-heading {

    max-width: 820px;

}

.eyebrow {

    display: flex;

    align-items: center;

    gap: 10px;

    margin-bottom: 12px;

    color: var(--nova-blue);

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 1.5px;

}

.eyebrow-line {

    width: 28px;

    height: 2px;

    background: var(--nova-blue);

    border-radius: 10px;

}

.risk-header h2 {

    margin: 0;

    color: var(--nova-navy);

    font-size: clamp(1.8rem, 3vw, 2.35rem);

    line-height: 1.15;

    font-weight: 700;

    letter-spacing: -0.04em;

}

.risk-header p {

    max-width: 760px;

    margin: 12px 0 0;

    color: var(--nova-muted);

    font-size: 14px;

    line-height: 1.7;

}

.risk-status {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    flex-shrink: 0;

    padding: 9px 13px;

    border: 1px solid #dbeafe;

    border-radius: 999px;

    background: #f8fbff;

    color: #31577f;

    font-size: 11px;

    font-weight: 600;

}

.status-dot {

    width: 7px;

    height: 7px;

    border-radius: 50%;

    background: #22c55e;

    box-shadow: 0 0 0 4px #dcfce7;

}


/* =========================================================
   OVERVIEW
========================================================= */

.risk-overview {

    display: grid;

    grid-template-columns:
        minmax(0, 2fr)
        auto
        minmax(150px, 1fr)
        minmax(170px, 1fr);

    align-items: center;

    gap: 26px;

    padding: 24px;

    border: 1px solid #dbe7f3;

    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            #f8fbff 0%,
            #ffffff 65%
        );

}

.overview-main {

    display: flex;

    align-items: center;

    gap: 17px;

}

.overview-icon {

    display: grid;

    place-items: center;

    width: 54px;

    height: 54px;

    flex-shrink: 0;

    border: 1px solid #bfdbfe;

    border-radius: 15px;

    background: #eff6ff;

    color: var(--nova-blue);

    font-size: 23px;

}

.overview-label {

    display: block;

    margin-bottom: 3px;

    color: var(--nova-muted);

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.2px;

}

.overview-value {

    display: block;

    margin-bottom: 5px;

    font-size: 1.45rem;

    font-weight: 800;

    letter-spacing: -.02em;

}

.overview-value.high {

    color: #b91c1c;

}

.overview-value.medium {

    color: #b45309;

}

.overview-value.low {

    color: #15803d;

}

.overview-main p {

    margin: 0;

    color: var(--nova-muted);

    font-size: 12px;

    line-height: 1.5;

}

.overview-divider {

    width: 1px;

    height: 58px;

    background: var(--nova-border);

}

.overview-stat {

    display: flex;

    flex-direction: column;

    gap: 7px;

}

.overview-stat span {

    color: var(--nova-muted);

    font-size: 10px;

    font-weight: 700;

    letter-spacing: .8px;

}

.overview-stat strong {

    color: var(--nova-navy);

    font-size: 1.55rem;

    font-weight: 750;

}

.overview-stat strong.success {

    color: #15803d;

}


/* =========================================================
   SECTION HEADING
========================================================= */

.analysis-block {

    display: flex;

    flex-direction: column;

    gap: 20px;

}

.section-heading {

    display: flex;

    justify-content: space-between;

    align-items: flex-end;

}

.section-eyebrow {

    display: block;

    margin-bottom: 6px;

    color: var(--nova-blue);

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.3px;

}

.section-heading h3 {

    margin: 0;

    color: var(--nova-navy);

    font-size: 1.35rem;

    font-weight: 700;

    letter-spacing: -.025em;

}

.section-heading p {

    margin: 7px 0 0;

    color: var(--nova-muted);

    font-size: 13px;

    line-height: 1.6;

}


/* =========================================================
   RISK GRID
========================================================= */

.risk-grid {

    display: grid;

    grid-template-columns:
        repeat(
            2,
            minmax(0, 1fr)
        );

    gap: 18px;

}


/* =========================================================
   METRICS
========================================================= */

.risk-metrics {

    display: grid;

    grid-template-columns:
        repeat(
            4,
            minmax(0, 1fr)
        );

    gap: 14px;

}

.metric-card {

    position: relative;

    display: flex;

    flex-direction: column;

    min-width: 0;

    padding: 20px;

    border: 1px solid var(--nova-border);

    border-radius: 17px;

    background: #ffffff;

    transition:
        transform .25s ease,
        border-color .25s ease,
        box-shadow .25s ease;

}

.metric-card:hover {

    transform: translateY(-3px);

    border-color: #bfdbfe;

    box-shadow:
        0 12px 28px rgba(37, 99, 235, .09);

}

.metric-top {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 10px;

}

.metric-label {

    color: var(--nova-muted);

    font-size: 10px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: .8px;

}

.metric-icon {

    display: grid;

    place-items: center;

    width: 29px;

    height: 29px;

    border: 1px solid #dbeafe;

    border-radius: 9px;

    background: #f8fbff;

    color: var(--nova-blue);

    font-size: 13px;

    font-weight: 700;

}

.metric-icon.success-icon {

    color: #15803d;

    border-color: #bbf7d0;

    background: #f0fdf4;

}

.metric-icon.high {

    color: #b91c1c;

    border-color: #fecaca;

    background: #fef2f2;

}

.metric-icon.medium {

    color: #b45309;

    border-color: #fde68a;

    background: #fffbeb;

}

.metric-icon.low {

    color: #15803d;

    border-color: #bbf7d0;

    background: #f0fdf4;

}

.metric-value {

    margin-top: 16px;

    color: var(--nova-navy);

    font-size: 1.65rem;

    line-height: 1;

    font-weight: 800;

    letter-spacing: -.04em;

}

.metric-value.success {

    color: #15803d;

}

.metric-value.high {

    color: #b91c1c;

}

.metric-value.medium {

    color: #b45309;

}

.metric-value.low {

    color: #15803d;

}

.metric-description {

    margin-top: 8px;

    color: #8a9bad;

    font-size: 11px;

}


/* =========================================================
   SUMMARY
========================================================= */

.risk-summary {

    overflow: hidden;

    border: 1px solid var(--nova-border);

    border-radius: 20px;

    background: #ffffff;

}

.summary-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    padding: 24px;

    border-bottom: 1px solid var(--nova-border);

    background:
        linear-gradient(
            135deg,
            #f8fbff,
            #ffffff
        );

}

.summary-heading h3 {

    margin: 0;

    color: var(--nova-navy);

    font-size: 1.3rem;

    font-weight: 700;

    letter-spacing: -.025em;

}

.summary-heading p {

    margin: 7px 0 0;

    color: var(--nova-muted);

    font-size: 12px;

    line-height: 1.6;

}

.summary-badge {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    flex-shrink: 0;

    padding: 9px 14px;

    border-radius: 999px;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: .8px;

}

.summary-badge.high {

    border: 1px solid #fecaca;

    background: #fef2f2;

    color: #b91c1c;

}

.summary-badge.medium {

    border: 1px solid #fde68a;

    background: #fffbeb;

    color: #b45309;

}

.summary-badge.low {

    border: 1px solid #bbf7d0;

    background: #f0fdf4;

    color: #15803d;

}

.badge-dot {

    width: 6px;

    height: 6px;

    border-radius: 50%;

    background: currentColor;

}

.summary-body {

    padding: 28px;

    color: var(--nova-text);

    line-height: 1.8;

}

.summary-footer {

    display: grid;

    grid-template-columns:
        repeat(
            3,
            1fr
        );

    gap: 20px;

    padding: 19px 24px;

    border-top: 1px solid var(--nova-border);

    background: #f8fafc;

}

.summary-item {

    display: flex;

    flex-direction: column;

    gap: 5px;

}

.summary-item span {

    color: var(--nova-muted);

    font-size: 10px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: .6px;

}

.summary-item strong {

    color: var(--nova-navy);

    font-size: 14px;

    font-weight: 750;

}

.summary-item strong.success {

    color: #15803d;

}

.summary-item strong.high {

    color: #b91c1c;

}

.summary-item strong.medium {

    color: #b45309;

}

.summary-item strong.low {

    color: #15803d;

}


/* =========================================================
   DISCLAIMER
========================================================= */

.risk-disclaimer {

    display: flex;

    align-items: flex-start;

    gap: 10px;

    padding: 13px 15px;

    border: 1px solid #e2e8f0;

    border-radius: 12px;

    background: #f8fafc;

}

.disclaimer-icon {

    display: grid;

    place-items: center;

    width: 19px;

    height: 19px;

    flex-shrink: 0;

    border: 1px solid #cbd5e1;

    border-radius: 50%;

    color: #64748b;

    font-size: 11px;

    font-weight: 700;

}

.risk-disclaimer p {

    margin: 0;

    color: #718096;

    font-size: 10px;

    line-height: 1.6;

}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 1100px) {

    .risk-overview {

        grid-template-columns:
            1fr 1fr;

    }

    .overview-divider {

        display: none;

    }

    .risk-metrics {

        grid-template-columns:
            repeat(
                2,
                1fr
            );

    }

}


@media (max-width: 850px) {

    .risk-view {

        padding: 24px;

    }

    .risk-header {

        flex-direction: column;

    }

    .risk-status {

        align-self: flex-start;

    }

    .risk-grid {

        grid-template-columns: 1fr;

    }

}


@media (max-width: 650px) {

    .risk-view {

        gap: 22px;

        padding: 18px;

        border-radius: 18px;

    }

    .risk-overview {

        grid-template-columns: 1fr;

        gap: 18px;

        padding: 18px;

    }

    .risk-metrics {

        grid-template-columns: 1fr;

    }

    .summary-header {

        flex-direction: column;

        align-items: flex-start;

        padding: 19px;

    }

    .summary-body {

        padding: 20px;

    }

    .summary-footer {

        grid-template-columns: 1fr;

        padding: 18px;

    }

}


/* =========================================================
   ANIMACIONES
========================================================= */

.risk-view {

    animation:
        novaFadeIn
        .45s
        ease
        both;

}

.risk-overview {

    animation:
        novaSlideUp
        .45s
        ease
        .05s
        both;

}

.risk-grid > * {

    animation:
        novaSlideUp
        .5s
        ease
        both;

}

.risk-grid > *:nth-child(2) {

    animation-delay: .06s;

}

.risk-grid > *:nth-child(3) {

    animation-delay: .12s;

}

.risk-grid > *:nth-child(4) {

    animation-delay: .18s;

}

.metric-card {

    animation:
        novaSlideUp
        .5s
        ease
        both;

}

.metric-card:nth-child(2) {

    animation-delay: .05s;

}

.metric-card:nth-child(3) {

    animation-delay: .1s;

}

.metric-card:nth-child(4) {

    animation-delay: .15s;

}

.risk-summary {

    animation:
        novaSlideUp
        .55s
        ease
        both;

}

@keyframes novaFadeIn {

    from {

        opacity: 0;

    }

    to {

        opacity: 1;

    }

}

@keyframes novaSlideUp {

    from {

        opacity: 0;

        transform: translateY(12px);

    }

    to {

        opacity: 1;

        transform: translateY(0);

    }

}


/* =========================================================
   REDUCE MOTION
========================================================= */

@media (prefers-reduced-motion: reduce) {

    .risk-view,
    .risk-overview,
    .risk-grid > *,
    .metric-card,
    .risk-summary {

        animation: none;

    }

    .metric-card {

        transition: none;

    }

}

</style>