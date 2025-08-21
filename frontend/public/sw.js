const APP_SHELL_CACHE = 'app-shell-v2'

self.addEventListener('install', (event) => {
	self.skipWaiting()
	// index.html を事前キャッシュしてナビゲーション時のフォールバックに使う
	event.waitUntil(
		caches.open(APP_SHELL_CACHE).then((cache) => cache.addAll(['/index.html']))
	)
})

self.addEventListener('activate', (event) => {
	event.waitUntil(
		(async () => {
			const keys = await caches.keys()
			await Promise.all(
				keys.filter((key) => key !== APP_SHELL_CACHE).map((key) => caches.delete(key))
			)
			await self.clients.claim()
		})()
	)
})

// ネットワーク優先、失敗時にキャッシュ（プレーンな例。必要に応じて強化可能）
self.addEventListener('fetch', (event) => {
	const request = event.request
	if (request.method !== 'GET') return
	// API は素通し
	if (new URL(request.url).pathname.startsWith('/api/')) return

	// ナビゲーションリクエスト（ページ遷移）は index.html にフォールバック
	if (request.mode === 'navigate') {
		event.respondWith(
			fetch(request)
				.then((response) => {
					if (response && response.status === 404) {
						return caches.match('/index.html')
					}
					return response
				})
				.catch(() => caches.match('/index.html'))
		)
		return
	}

	// 通常のアセットはネットワーク優先、失敗時キャッシュ
	event.respondWith(
		fetch(request).catch(() => caches.match(request))
	)
})


