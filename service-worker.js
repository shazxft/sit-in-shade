self.addEventListener("install", e => {
  e.waitUntil(
    caches.open("shadeseat").then(c =>
      c.addAll(["/", "/static/app.js"])
    )
  );
});

self.addEventListener("fetch", e => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});

