/* FÄRGVARIANTER – bara på utkastbrancherna. Tas bort när Jennie valt.
   Lägger en liten väljare nere till vänster som byter data-variant på <html>.
   Valet sparas (localStorage) och kan länkas: index.html?variant=skog */
(function () {
  var variants = [
    ['', '1. Nuvarande (main-f)'],
    ['mork-topp', '2. Mörk topp'],
    ['vit-topp', '3. Vit topp, grön mitt'],
    ['grona-band', '4. Gröna band'],
    ['gron-cta', '5. Grönt kontaktband'],
    ['grafit', '6. Grafit'],
    ['skog', '7. Skog'],
    ['natt', '8. Natt'],
    ['salvia', '9. Salvia'],
    ['mossa', '10. Mossa'],
    ['petrol', '11. Petrol'],
    ['hav', '12. Hav'],
    ['ljung', '13. Ljung'],
    ['plommon', '14. Plommon'],
    ['rodfarg', '15. Rödfärg'],
    ['lera', '16. Lera'],
    ['ockra', '17. Ockra'],
    ['granit', '18. Granit'],
    ['omvand', '19. Galen: Omvänd'],
    ['morkt', '20. Galen: Mörkt läge'],
    ['beige', '21. Galen: Bara beige'],
    ['zebra', '22. Galen: Zebra'],
    ['gron-botten', '23. Galen: Grön botten'],
    ['gron-hero', '24. Galen: Grön hero']
  ];
  var KEY = 'farg-variant';
  var root = document.documentElement;

  function known(value) {
    return variants.some(function (v) { return v[0] === value; }) ? value : '';
  }
  function read() {
    var fromUrl = new URLSearchParams(location.search).get('variant');
    if (fromUrl !== null) return known(fromUrl);
    try { return known(localStorage.getItem(KEY) || ''); } catch (e) { return ''; }
  }
  function apply(value) {
    if (value) root.setAttribute('data-variant', value);
    else root.removeAttribute('data-variant');
    try { localStorage.setItem(KEY, value); } catch (e) { /* privat läge – inget sparas */ }
  }

  // Sätts direkt (innan sidan ritas) så att man inte ser fel färger en kort stund
  apply(read());

  document.addEventListener('DOMContentLoaded', function () {
    var box = document.createElement('div');
    box.className = 'variant-picker';
    box.innerHTML =
      '<label for="variant-select">Färgvariant</label>' +
      '<button type="button" data-step="-1" aria-label="Föregående variant">←</button>' +
      '<select id="variant-select"></select>' +
      '<button type="button" data-step="1" aria-label="Nästa variant">→</button>';
    var select = box.querySelector('select');
    variants.forEach(function (v) {
      var option = document.createElement('option');
      option.value = v[0];
      option.textContent = v[1];
      select.appendChild(option);
    });
    select.value = root.getAttribute('data-variant') || '';
    select.addEventListener('change', function () { apply(select.value); });
    box.addEventListener('click', function (e) {
      var step = e.target.getAttribute('data-step');
      if (!step) return;
      var i = (select.selectedIndex + Number(step) + variants.length) % variants.length;
      select.selectedIndex = i;
      apply(select.value);
    });
    document.body.appendChild(box);
  });
})();
