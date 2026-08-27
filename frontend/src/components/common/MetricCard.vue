<template>

    <div class="metric-card">

        <div
            class="metric-icon"
            :style="iconStyle"
        >

            {{ icon }}

        </div>

        <div class="metric-info">

            <span class="metric-title">

                {{ title }}

            </span>

            <strong class="metric-value">

                {{ animatedValue }}

            </strong>

        </div>

    </div>

</template>


<script setup>

import {
    computed,
    ref,
    onMounted,
    watch
} from "vue"


const props = defineProps({

    title: {

        type: String,

        required: true

    },

    value: {

        type: [
            String,
            Number
        ],

        required: true

    },

    icon: {

        type: String,

        default: "📊"

    },

    color: {

        type: String,

        default: "#2563EB"

    }

})


const iconStyle = computed(() => ({

    background: `${props.color}18`,

    color: props.color

}))


const animatedValue = ref(props.value)


function animateNumber(){

    if(

        typeof props.value !== "number"

    ){

        animatedValue.value = props.value

        return

    }


    let current = 0

    const end = props.value


    const step = Math.max(

        1,

        Math.ceil(end / 30)

    )


    const interval = setInterval(() => {

        current += step


        if(current >= end){

            animatedValue.value = end

            clearInterval(interval)

        }else{

            animatedValue.value = current

        }

    }, 20)

}


onMounted(

    animateNumber

)


watch(

    () => props.value,

    animateNumber

)

</script>


<style scoped>

.metric-card {

    position: relative;

    overflow: hidden;

    display: flex;

    align-items: center;

    gap: 18px;

    padding: 22px;

    border-radius: 18px;

    background: #FFFFFF;

    border: 1px solid #E2E8F0;

    box-shadow:
        0 6px 20px rgba(15, 39, 71, 0.05);

    transition:
        transform .25s ease,
        box-shadow .25s ease,
        border-color .25s ease;

}


.metric-card::before {

    content: "";

    position: absolute;

    top: 0;

    left: 0;

    width: 4px;

    height: 100%;

    background: #2563EB;

}


.metric-card:hover {

    transform: translateY(-3px);

    border-color: #BFDBFE;

    box-shadow:
        0 12px 28px rgba(15, 39, 71, 0.08);

}


.metric-icon {

    width: 58px;

    height: 58px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 15px;

    font-size: 1.65rem;

    border: 1px solid #DBEAFE;

    flex-shrink: 0;

    transition: transform .25s ease;

}


.metric-card:hover .metric-icon {

    transform: scale(1.05);

}


.metric-info {

    display: flex;

    flex-direction: column;

    justify-content: center;

    gap: 6px;

    min-width: 0;

    flex: 1;

}


.metric-title {

    color: #64748B;

    font-size: .78rem;

    font-weight: 600;

    text-transform: uppercase;

    letter-spacing: .7px;

}


.metric-value {

    color: #0F2747;

    font-size: 1.25rem;

    font-weight: 700;

    line-height: 1.4;

    word-break: break-word;

}


.metric-card {

    animation:
        metricAppear .45s ease;

}


@keyframes metricAppear {

    from {

        opacity: 0;

        transform: translateY(18px);

    }

    to {

        opacity: 1;

        transform: translateY(0);

    }

}


@media (max-width: 768px) {

    .metric-card {

        padding: 18px;

        gap: 14px;

    }


    .metric-icon {

        width: 52px;

        height: 52px;

        font-size: 1.45rem;

    }


    .metric-value {

        font-size: 1.1rem;

    }

}

</style>