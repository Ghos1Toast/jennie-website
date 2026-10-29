// Jennies Färgsättning & Måleri – meny, galleri-ljusbox och kontaktformulär.
// Sidan fungerar utan JS: menyn syns, bilder öppnas som vanliga länkar och
// formuläret skickas som ett vanligt POST.

(function () {
  'use strict';

  // Pausar alla filmer som spelas av sig själva (används när ljusboxen öppnas)
  function autoVideosPause() {
    Array.prototype.forEach.call(document.querySelectorAll('.autoplay-video'), function (v) { v.pause(); });
  }

  // ---------- Mobilmeny ----------
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.getElementById('site-nav');

  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    };

    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  // ---------- Årtal i footern ----------
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  // ---------- Galleri-ljusbox ----------
  var links = Array.prototype.slice.call(document.querySelectorAll('.gallery-link'));
  var box = document.getElementById('lightbox');

  if (links.length && box && typeof box.showModal === 'function') {
    var img = box.querySelector('img');
    var vid = box.querySelector('.lightbox-video');
    var caption = box.querySelector('figcaption');
    var counter = box.querySelector('.lightbox-count');
    var current = 0;
    var opener = null;

    var show = function (i) {
      current = (i + links.length) % links.length;
      var link = links[current];
      var videoSrc = link.getAttribute('data-video');
      var label = link.getAttribute('data-caption') || '';
      if (videoSrc && vid) {
        // Film: visa videospelaren i stället för bilden
        img.hidden = true;
        img.removeAttribute('src');
        vid.hidden = false;
        var small = link.querySelector('video');
        if (small && small.poster) vid.poster = small.poster;  // stillbild tills filmen hunnit starta
        vid.src = videoSrc;
        vid.setAttribute('aria-label', label ? 'Film: ' + label : 'Film');
        var p = vid.play();
        if (p && p.catch) p.catch(function () {});
      } else {
        if (vid) { vid.pause(); vid.removeAttribute('src'); vid.hidden = true; }
        var thumb = link.querySelector('img');
        img.hidden = false;
        img.src = link.getAttribute('href');
        img.alt = thumb ? thumb.alt : '';
      }
      caption.textContent = label;
      counter.textContent = (current + 1) + ' av ' + links.length;
      // Ladda grannbilderna i förväg så att bläddring går snabbt (inte filmer)
      [current - 1, current + 1].forEach(function (n) {
        var next = links[(n + links.length) % links.length];
        if (!next.hasAttribute('data-video')) new Image().src = next.getAttribute('href');
      });
    };

    // En enda bild: inga pilar
    if (links.length < 2) box.querySelector('.lightbox-nav').hidden = true;

    links.forEach(function (link, i) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        opener = link;
        autoVideosPause();
        show(i);
        box.showModal();
        document.documentElement.classList.add('lightbox-open');
      });
    });

    box.querySelector('[data-lightbox="close"]').addEventListener('click', function () { box.close(); });
    box.querySelector('[data-lightbox="prev"]').addEventListener('click', function () { show(current - 1); });
    box.querySelector('[data-lightbox="next"]').addEventListener('click', function () { show(current + 1); });

    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') show(current - 1);
      if (e.key === 'ArrowRight') show(current + 1);
    });

    // Klick på den mörka bakgrunden stänger
    box.addEventListener('click', function (e) {
      if (e.target === box || e.target.classList.contains('lightbox-figure')) box.close();
    });

    // Svep åt vänster/höger på mobil
    var touchX = null;
    box.addEventListener('touchstart', function (e) { touchX = e.touches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', function (e) {
      if (touchX === null || links.length < 2) return;
      var dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
      touchX = null;
    });

    box.addEventListener('close', function () {
      document.documentElement.classList.remove('lightbox-open');
      img.removeAttribute('src');
      if (vid) { vid.pause(); vid.removeAttribute('src'); vid.hidden = true; }
      if (opener) opener.focus();
    });
  }

  // ---------- Filmer som spelas av sig själva (startsidan och galleriet) ----------
  // Spelar tyst och i loop när filmen syns, pausar när den scrollas bort.
  // Spelar inte automatiskt om besökaren valt "minska rörelse" eller sparläge för data.
  // Varje film har en paus/spela-knapp (WCAG 2.2.2: rörelse längre än 5 s ska gå att pausa).
  var autoVideos = Array.prototype.slice.call(document.querySelectorAll('.autoplay-video'));

  if (autoVideos.length) {
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var saveData = navigator.connection && navigator.connection.saveData;
    var allowAutoplay = !reduceMotion && !saveData;

    var setToggle = function (button, playing) {
      if (!button) return;
      button.setAttribute('aria-label', playing ? 'Pausa filmen' : 'Spela filmen');
      button.classList.toggle('is-paused', !playing);
    };

    var tryPlay = function (video) {
      var p = video.play();
      if (p && p.catch) p.catch(function () { setToggle(video._toggle, false); });
    };

    autoVideos.forEach(function (video) {
      // Knappen ligger bredvid filmen (inte inuti länken)
      var holder = video.closest('.gallery-item, .hero-video-wrap');
      var button = holder ? holder.querySelector('.video-toggle') : null;
      video._toggle = button;
      video._userPaused = !allowAutoplay;
      if (button) {
        button.hidden = false;
        setToggle(button, false);
        button.addEventListener('click', function () {
          if (video.paused) {
            video._userPaused = false;
            tryPlay(video);
          } else {
            video._userPaused = true;
            video.pause();
          }
        });
      }
      video.addEventListener('play', function () { setToggle(button, true); });
      video.addEventListener('pause', function () { setToggle(button, false); });
    });

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          var video = entry.target;
          if (entry.isIntersecting) {
            if (!video._userPaused) {
              if (video.preload === 'none') video.preload = 'auto';
              tryPlay(video);
            }
          } else if (!video.paused) {
            video.pause();
          }
        });
      }, { threshold: 0.4 });
      autoVideos.forEach(function (video) { observer.observe(video); });
    } else if (allowAutoplay) {
      autoVideos.forEach(tryPlay);
    }

    // Pausa alla små filmer medan ljusboxen är öppen
    if (box) {
      box.addEventListener('close', function () {
        autoVideos.forEach(function (video) {
          var r = video.getBoundingClientRect();
          if (!video._userPaused && r.bottom > 0 && r.top < window.innerHeight) tryPlay(video);
        });
      });
    }
  }

  // ---------- Kontaktformulär ----------
  var form = document.getElementById('contact-form');

  if (form && window.fetch) {
    var status = document.getElementById('form-status');
    var button = form.querySelector('button[type="submit"]');

    var setStatus = function (text, ok) {
      status.textContent = text;
      status.className = 'form-status ' + (ok ? 'is-ok' : 'is-error');
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      button.disabled = true;
      setStatus('Skickar …', true);

      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      })
        .then(function (res) {
          if (!res.ok) throw new Error(res.status);
          form.reset();
          setStatus('Tack! Din förfrågan är skickad.', true);
        })
        .catch(function () {
          setStatus('Något gick fel och förfrågan skickades inte. Försök igen, eller ring eller mejla direkt.', false);
        })
        .then(function () {
          button.disabled = false;
        });
    });
  }
})();
