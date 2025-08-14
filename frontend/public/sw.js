self.addEventListener('install', (event) => {
	self.skipWaiting()
})

self.addEventListener('activate', (event) => {
	event.waitUntil(self.clients.claim())
})

// ネットワーク優先、失敗時にキャッシュ（プレーンな例。必要に応じて強化可能）
self.addEventListener('fetch', (event) => {
	const request = event.request
	if (request.method !== 'GET') return
	// API は素通し
	if (new URL(request.url).pathname.startsWith('/api/')) return

	event.respondWith(
		fetch(request).catch(() => caches.match(request))
	)
})


