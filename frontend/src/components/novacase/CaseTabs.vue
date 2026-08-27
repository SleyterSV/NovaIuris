<template>

<section class="case-tabs">

    <div class="tabs-header">

        <button

            v-for="tab in tabs"

            :key="tab.id"

            @click="activeTab = tab.id"

            :class="[

                'tab-button',

                {

                    active:

                    activeTab === tab.id

                }

            ]"

        >

            <span class="tab-icon">

                {{ tab.icon }}

            </span>

            {{ tab.label }}

        </button>

    </div>

    <div class="tabs-content">

        <slot

            :name="activeTab"

        />

    </div>

</section>

</template>

<script setup>

import { ref, watch } from "vue"

const props = defineProps({

    defaultTab: {

        type: String,

        default: "report"

    }

})

const emit = defineEmits([

    "change"

])

const tabs = [

    {

        id: "report",

        label: "Informe",

        icon: "📄"

    },

    {

        id: "analysis",

        label: "Análisis",

        icon: "⚖️"

    },

    {

        id: "evidence",

        label: "Evidencia",

        icon: "📑"

    },

    {

        id: "risk",

        label: "Riesgos",

        icon: "⚠️"

    },

    {

        id: "counter",

        label: "Contraargumentos",

        icon: "🛡️"

    },

    {

        id: "strategy",

        label: "Estrategia",

        icon: "🎯"

    }

]

const activeTab = ref(

    props.defaultTab

)

watch(

    activeTab,

    (value)=>{

        emit(

            "change",

            value

        )

    }

)

</script>

<style scoped>

.case-tabs{

    margin-top:32px;

    border-radius:22px;

    background:linear-gradient(

        180deg,

        rgba(18,26,40,.97),

        rgba(13,19,30,.98)

    );

    border:1px solid rgba(255,255,255,.05);

    box-shadow:

        0 20px 50px rgba(0,0,0,.30);

    overflow:hidden;

}

.tabs-header{

    display:flex;

    align-items:center;

    gap:10px;

    padding:18px;

    overflow-x:auto;

    scrollbar-width:none;

    border-bottom:

        1px solid rgba(255,255,255,.05);

}

.tabs-header::-webkit-scrollbar{

    display:none;

}

.tab-button{

    display:flex;

    align-items:center;

    gap:10px;

    white-space:nowrap;

    border:none;

    cursor:pointer;

    padding:12px 22px;

    border-radius:14px;

    background:transparent;

    color:#94A3B8;

    font-size:.95rem;

    font-weight:600;

    transition:

        all .25s ease;

}

.tab-button:hover{

    background:

        rgba(78,168,255,.08);

    color:white;

}

.tab-button.active{

    background:

        linear-gradient(

            135deg,

            #2563EB,

            #3B82F6

        );

    color:white;

    box-shadow:

        0 10px 30px rgba(

            37,

            99,

            235,

            .30

        );

}

.tab-icon{

    display:flex;

    align-items:center;

    justify-content:center;

    width:24px;

    height:24px;

    font-size:16px;

}

.tabs-content{

    padding:32px;

    min-height:500px;

}

@media(max-width:900px){

    .tabs-header{

        padding:12px;

    }

    .tab-button{

        padding:10px 18px;

        font-size:.90rem;

    }

    .tabs-content{

        padding:22px;

    }

}

</style>