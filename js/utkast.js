/* UTKASTVÄLJARE – bara på branchen "main-f". Tas bort när Jennie valt.
   Lägger en liten väljare nere till vänster som byter rubriktypsnitt.
   Valet sparas (localStorage) och kan länkas: index.html?rubriker=serif */
(function () {
  var options = [
    ['', 'Barlow (som nu)'],
    ['serif', 'Serif (som utkast F)']
  ];
  var KEY = 'utkast-rubriker';
  var root = document.documentElement;

  function known(value) {
    return options.some(function (o) { return o[0] === value; }) ? value : '';
  }
  function read() {
    var fromUrl = new URLSearchParams(location.search).get('rubriker');
    if (fromUrl !== null) return known(fromUrl);
    try { return known(localStorage.getItem(KEY) || ''); } catch (e) { return ''; }
  }
  function apply(value) {
    root.classList.toggle('rubriker-serif', value === 'serif');
    try { localStorage.setItem(KEY, value); } catch (e) { /* privat läge – inget sparas */ }
  }

  // Sätts direkt (innan sidan ritas) så att typsnittet inte hoppar
  apply(read());

  document.addEventListener('DOMContentLoaded', function () {
    var box = document.createElement('div');
    box.className = 'variant-picker';
    box.innerHTML = '<label for="rubriker-select">Rubriker</label><select id="rubriker-select"></select>';
    var select = box.querySelector('select');
    options.forEach(function (o) {
      var option = document.createElement('option');
      option.value = o[0];
      option.textContent = o[1];
      select.appendChild(option);
    });
    select.value = root.classList.contains('rubriker-serif') ? 'serif' : '';
    select.addEventListener('change', function () { apply(select.value); });
    document.body.appendChild(box);
  });
})();
