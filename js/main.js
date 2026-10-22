// Jennies Färgsättning & Måleri – meny, galleri-ljusbox och kontaktformulär.
// Sidan fungerar utan JS: menyn syns, bilder öppnas som vanliga länkar och
// formuläret skickas som ett vanligt POST.

(function () {
  'use strict';

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
    var caption = box.querySelector('figcaption');
    var counter = box.querySelector('.lightbox-count');
    var current = 0;
    var opener = null;

    var show = function (i) {
      current = (i + links.length) % links.length;
      var link = links[current];
      var thumb = link.querySelector('img');
      img.src = link.getAttribute('href');
      img.alt = thumb ? thumb.alt : '';
      caption.textContent = link.getAttribute('data-caption') || '';
      counter.textContent = (current + 1) + ' av ' + links.length;
    };

    links.forEach(function (link, i) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        opener = link;
        show(i);
        box.showModal();
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

    box.addEventListener('close', function () {
      img.removeAttribute('src');
      if (opener) opener.focus();
    });
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
