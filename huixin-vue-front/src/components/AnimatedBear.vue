<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { DotLottieVue, type DotLottieVueInstance } from '@lottiefiles/dotlottie-vue'
import wavingBear from '@/assets/Lottie/Waving Bear.lottie?url'

const animationSrc = wavingBear
const bearPlayer = ref<DotLottieVueInstance | null>(null)
const isPlaying = ref(false)
let cleanupCompleteListener: (() => void) | null = null
let fallbackTimer: number | null = null
let waitFrame = 0

const getInstance = () => bearPlayer.value?.getDotLottieInstance()

const handleComplete = () => {
	isPlaying.value = false
	if (fallbackTimer) {
		clearTimeout(fallbackTimer)
		fallbackTimer = null
	}
}

const bindCompletionListener = (instance: any) => {
	const listenerSources = [
		instance,
		instance?.animationItem,
		instance?.player
	].filter(Boolean)

	for (const source of listenerSources) {
		if (typeof source?.addEventListener === 'function') {
			source.addEventListener('complete', handleComplete)
			return () => source.removeEventListener('complete', handleComplete)
		}
		if (typeof source?.on === 'function' && typeof source?.off === 'function') {
			source.on('complete', handleComplete)
			return () => source.off('complete', handleComplete)
		}
	}

	return null
}

const estimateDuration = (instance: any) => {
	if (!instance) return null
	if (typeof instance.duration === 'number' && instance.duration > 0) {
		return instance.duration * 1000
	}
	if (typeof instance.getDuration === 'function') {
		return instance.getDuration(false) * 1000
	}
	const animationItem = instance.animationItem
	if (animationItem) {
		if (typeof animationItem.getDuration === 'function') {
			return animationItem.getDuration(false) * 1000
		}
		if (animationItem.totalFrames && animationItem.frameRate) {
			return (animationItem.totalFrames / animationItem.frameRate) * 1000
		}
	}
	return null
}

const configureInstance = (instance: any) => {
	if (!instance) return
	if (typeof instance.setLoop === 'function') {
		instance.setLoop(false)
	} else if (typeof instance.loop !== 'undefined') {
		instance.loop = false
	}
	if (!cleanupCompleteListener) {
		cleanupCompleteListener = bindCompletionListener(instance)
	}
}

const playFromStart = () => {
	const instance = getInstance()
	if (!instance || isPlaying.value) return
	isPlaying.value = true
	configureInstance(instance)
	if (typeof instance.stop === 'function') {
		instance.stop()
	}
	if (typeof instance.setFrame === 'function') {
		instance.setFrame(0)
	}
	instance.play()

	const duration = estimateDuration(instance)
	const timeout = duration && duration > 0 ? duration : 4000
	if (fallbackTimer) {
		clearTimeout(fallbackTimer)
	}
	fallbackTimer = window.setTimeout(() => {
		isPlaying.value = false
		fallbackTimer = null
	}, timeout + 50)
}

const handleMouseEnter = () => {
	playFromStart()
}

onMounted(async () => {
	await nextTick()
	// 等待动画实例渲染完成
	const waitForInstance = () => {
		const instance = getInstance()
		if (!instance) {
			waitFrame = requestAnimationFrame(waitForInstance)
			return
		}
		if (waitFrame) {
			cancelAnimationFrame(waitFrame)
			waitFrame = 0
		}
		configureInstance(instance)
		playFromStart()
	}

	waitForInstance()
})

onBeforeUnmount(() => {
	if (waitFrame) {
		cancelAnimationFrame(waitFrame)
	}
	if (cleanupCompleteListener) {
		cleanupCompleteListener()
	}
	if (fallbackTimer) {
		clearTimeout(fallbackTimer)
	}
})
</script>

<template>
	<div
		class="animated-bear"
		@mouseenter="handleMouseEnter"
	>
		<DotLottieVue
			ref="bearPlayer"
			class="bear-animation"
			:src="animationSrc"
			:autoplay="false"
			:loop="false"
		/>
	</div>
</template>

<style scoped>
.animated-bear {
	display: flex;
	align-items: flex-end;
	justify-content: flex-start;
	width: 100%;
	cursor: pointer;
}

.animated-bear:hover {
	cursor: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1024 1024'><path fill='%238E96A6' d='M643.008 354.24l-0.384-2.752-0.256-2.176a189.504 189.504 0 0 0-7.872-31.232l-14.336-46.208a654.912 654.912 0 0 1-9.472-33.408l-1.728-7.04-1.088-2.56c-26.496-58.88-64-106.56-101.12-109.248l-3.072-0.128c-1.6 0-3.072 0-4.352 0.128l-1.152 0.064 0.064 0.768 0.32 1.92c2.88 16.384 12.8 38.848 34.688 80l17.472 32.704c31.616 60.032 39.616 81.536 36.992 109.184-3.712 38.72-58.88 42.176-67.328 4.224-13.184-59.264-60.544-119.68-122.88-162.56-51.52-35.52-101.312-48.768-111.488-40.64l-5.12 4.096c-13.696 11.648-14.208 16-9.6 24.128 4.16 7.232 12.096 16.128 24.768 27.776l3.584 3.264c8.192 7.36 42.88 36.544 50.368 43.136 44.8 39.168 73.024 72.512 90.112 113.536 15.36 36.928 27.072 89.088 31.168 134.528 2.112 23.168 2.048 43.264-0.512 58.688-4.992 29.632-20.352 52.224-52.992 46.016l-6.784-1.408c-21.888-4.992-33.28-13.44-93.504-64l-18.56-15.488c-7.68-6.4-15.552-12.608-23.488-18.688-38.976-29.376-61.248-36.48-71.04-28.736-26.88 21.44-21.12 42.368 26.752 86.528l3.648 3.328c12.096 10.944 24.704 21.44 43.52 36.224l45.12 35.2c60.288 47.36 80.256 66.56 97.088 95.808 42.304 73.472 49.408 142.784 35.392 200.64l-1.92 7.168c-1.792 6.656-3.648 11.776-5.248 15.36a34.112 34.112 0 0 1-63.488-24.96l1.6-4.224c0.896-2.56 1.856-5.696 2.688-9.344 10.112-41.728 4.864-93.184-28.16-150.592-11.84-20.48-32.448-39.04-95.36-88.064l-25.792-20.096a896.128 896.128 0 0 1-51.264-42.56c-77.952-70.592-98.56-136.832-27.072-193.792 43.712-34.816 92.672-19.136 154.624 27.648 8.064 6.08 16.128 12.544 25.6 20.352l37.696 31.36c8.96 7.36 16.128 13.248 22.08 17.92l2.432 1.792-0.064-2.112a262.784 262.784 0 0 0-0.576-9.024l-0.384-4.8c-3.52-38.976-13.76-84.48-26.24-114.496-12.16-29.184-34.432-55.488-72.064-88.32l-47.232-40.448-3.712-3.2c-19.84-17.792-33.024-32.32-41.984-48-23.168-40.448-11.968-81.088 31.36-115.584 40.704-32.384 112.192-14.912 179.776 29.056l6.912 4.608-0.128-1.792C426.88 81.536 452.48 52.48 500.16 51.264L504.128 51.2c46.72 0.32 86.144 25.472 119.04 68.608l1.536 2.112 1.536-1.408c10.752-9.28 24.96-14.912 42.24-16l4.096-0.192c49.28-0.96 85.312 37.632 109.44 98.368l2.432 6.464 2.304 0.512a46.72 46.72 0 0 1 12.48 5.12l2.368 1.408c71.36 46.848 100.928 110.08 95.488 184.96-2.752 38.4-13.44 75.328-32.832 123.136l-20.48 48.512-5.056 12.16a256.512 256.512 0 0 0-6.656 18.56c-8.96 29.056-16.064 62.592-21.376 99.712a1309.44 1309.44 0 0 0-11.264 205.44l0.64 21.568 0.256 6.592a34.112 34.112 0 0 1-68.16 3.648l-0.64-16.128c-2.112-71.04 0.512-152.64 11.584-230.72 5.76-40.448 13.568-77.44 23.68-110.272 2.56-8.064 5.76-16.64 10.048-27.328l20.864-49.472c19.072-45.76 29.056-78.72 31.36-110.208 1.92-27.904-2.624-52.288-15.488-74.112l-1.472-2.368 0.192 1.856c4.288 43.52 3.2 68.16-10.688 87.68l-1.792 2.432c-22.528 28.992-68.736 6.784-60.16-28.992 16.448-67.84-28.544-211.008-65.728-210.24-4.032 0.064-3.2-1.408-3.2 2.368l-0.128 2.688c-0.64 8.576 0.832 20.288 4.288 35.648l0.64 2.752 0.192 0.384c15.04 37.76 26.496 77.824 32.064 109.248l1.728 10.368 0.96 7.808c4.992 44.288-59.968 52.48-67.456 10.368z' /></svg>") 24 24, pointer;
}

.bear-animation {
  margin: 0 auto;
	width: clamp(190px, 22vw, 250px);
	height: clamp(190px, 22vw, 250px);
}

@media (max-width: 768px) {
	.animated-bear {
		margin-top: 16px;
		justify-content: center;
	}

	.bear-animation {
		width: clamp(160px, 44vw, 220px);
		height: clamp(160px, 44vw, 220px);
	}
}
</style>
