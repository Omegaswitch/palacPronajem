// velkoprevorskypalac.eu — progressive enhancement only; every page works without this file.
(function () {
  // ---- main menu (mobile) and submenus
  var toggle = document.querySelector(".menu-toggle");
  var menu = document.getElementById("menu");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("open", open);
    });
  }
  document.querySelectorAll(".sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.parentElement;
      var open = !li.classList.contains("open");
      li.classList.remove("closed");
      li.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    document.querySelectorAll(".has-sub.open").forEach(function (li) {
      li.classList.remove("open");
      var b = li.querySelector(".sub-toggle");
      if (b) b.setAttribute("aria-expanded", "false");
    });
    var li = document.activeElement && document.activeElement.closest(".has-sub");
    if (li) {
      if (document.activeElement.closest(".sub")) {
        var top = li.querySelector("a");
        if (top) top.focus();
      }
      li.classList.add("closed");  // focus stays on the item, so :focus-within would keep the submenu open; .closed holds it shut until focus leaves
    }
  });
  document.addEventListener("focusout", function (e) {
    var li = e.target.closest && e.target.closest(".has-sub.closed");
    if (li && !li.contains(e.relatedTarget)) li.classList.remove("closed");
  });
  document.addEventListener("pointerover", function (e) {  // the mouse re-opens it as usual
    var li = e.target.closest && e.target.closest(".has-sub.closed");
    if (li) li.classList.remove("closed");
  });

  // ---- images still downloading develop out of the paper tone once they arrive (see .is-loading)
  document.querySelectorAll("img.ph-img").forEach(function (img) {
    if (img.complete || img.naturalWidth) return;  // already shown (or progressively painting): leave it alone
    img.classList.add("is-loading");
    var done = function () { img.classList.remove("is-loading"); };
    img.addEventListener("load", done, { once: true });
    img.addEventListener("error", done, { once: true });
  });

  // ---- room galleries: each photograph links to its 1600 px file; here it opens in a viewer instead,
  // with previous/next buttons, arrow keys, swipe, and Escape to close (native <dialog>)
  document.querySelectorAll(".room-gallery").forEach(function (list) {
    var links = Array.prototype.slice.call(list.querySelectorAll("a.g-photo"));
    if (!links.length || !window.HTMLDialogElement) return;
    var d = document.createElement("dialog"), i = 0, x0 = null;
    d.className = "viewer";
    d.innerHTML = '<button class="v-close" type="button"></button><button class="v-prev" type="button"></button>' +
      '<img alt=""><button class="v-next" type="button"></button><p class="v-count" aria-live="polite"></p>';
    var img = d.querySelector("img"), count = d.querySelector(".v-count");
    [["v-close", "data-close"], ["v-prev", "data-prev"], ["v-next", "data-next"]].forEach(function (b) {
      d.querySelector("." + b[0]).setAttribute("aria-label", list.getAttribute(b[1]));
    });
    function show(n) {
      i = (n + links.length) % links.length;
      img.src = links[i].getAttribute("href");
      img.alt = links[i].querySelector("img").alt;
      count.textContent = (i + 1) + " / " + links.length;
      new Image().src = links[(i + 1) % links.length].getAttribute("href");  // the next one is ready when asked for
    }
    d.querySelector(".v-close").addEventListener("click", function () { d.close(); });
    d.querySelector(".v-prev").addEventListener("click", function () { show(i - 1); });
    d.querySelector(".v-next").addEventListener("click", function () { show(i + 1); });
    d.addEventListener("click", function (e) { if (e.target === d) d.close(); });
    d.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(i - 1);
      else if (e.key === "ArrowRight") show(i + 1);
    });
    d.addEventListener("pointerdown", function (e) { x0 = e.clientX; });
    d.addEventListener("pointerup", function (e) {
      if (x0 !== null && Math.abs(e.clientX - x0) > 50) show(i + (e.clientX < x0 ? 1 : -1));
      x0 = null;
    });
    d.addEventListener("close", function () { links[i].focus(); });
    document.body.appendChild(d);
    links.forEach(function (a, n) {
      a.addEventListener("click", function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey) return;
        e.preventDefault();
        show(n);
        d.showModal();
      });
    });
  });
})();
