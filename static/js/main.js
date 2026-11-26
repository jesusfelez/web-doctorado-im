// Menú móvil y filtros de búsqueda (profesorado y tesis). Sin dependencias.
(function () {
  var btn = document.getElementById('btnMenu');
  var menu = document.getElementById('menu');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      var ab = menu.classList.toggle('abierto');
      btn.setAttribute('aria-expanded', ab ? 'true' : 'false');
    });
  }

  var norm = function (s) {
    return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  };

  document.querySelectorAll('[data-filtro]').forEach(function (f) {
    var raiz = f.parentElement;
    var items = raiz.querySelectorAll('[data-item]');
    var busca = f.querySelector('[data-busca]');
    var sels = f.querySelectorAll('[data-sel]');
    var contador = raiz.querySelector('[data-contador]');
    var tipo = f.getAttribute('data-filtro');

    function aplicar() {
      var q = norm(busca ? busca.value : '');
      var n = 0;
      items.forEach(function (it) {
        var ok = norm(it.getAttribute('data-texto')).indexOf(q) !== -1;
        sels.forEach(function (s) {
          var campo = s.getAttribute('data-sel');
          var v = s.value;
          if (!v) return;
          var valores = (it.getAttribute('data-' + campo) || '').split(' ');
          if (valores.indexOf(v) === -1) ok = false;
        });
        it.classList.toggle('oculto', !ok);
        if (ok) n++;
      });
      raiz.querySelectorAll('.grupo-inv').forEach(function (g) {
        g.classList.toggle('oculto', !g.querySelector('[data-item]:not(.oculto)'));
      });
      if (contador) {
        var nombre = tipo === 'tesis' ? (n === 1 ? 'tesis' : 'tesis') : (n === 1 ? 'investigador/a' : 'investigadores/as');
        contador.textContent = n + ' ' + nombre;
      }
    }
    if (busca) busca.addEventListener('input', aplicar);
    sels.forEach(function (s) { s.addEventListener('change', aplicar); });
    aplicar();
  });
})();
