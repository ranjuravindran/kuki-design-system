/**
 * KuKi squircle utility — CSS approximation of Figma's native corner smoothing.
 *
 * Figma's exact "corner smoothing" algorithm isn't public in a portable form, so
 * instead of reverse-engineering it we draw each corner as a true superellipse
 * (Lamé curve): |x/r|^n + |y/r|^n = 1. n=2 is a plain circle; higher n pulls the
 * curve toward a "squarer" shape while staying perfectly smooth (continuous
 * curvature, no flat-to-round seam) — which is the actual visual property people
 * mean by "squircle". smoothing 0..1 maps to n = 2..5, so smoothing=0.6 (Figma's
 * default we used) lands at n=3.8, a close visual match to Figma's own default.
 *
 * Usage: add `data-squircle="RADIUS_PX"` (optionally `data-squircle-smoothing="0..1"`,
 * default 0.6) to any element, then call `initSquircles()` once after content is in
 * the DOM. A ResizeObserver keeps the clip-path in sync if the element resizes.
 */
(function (global) {
  function superellipseCorner(r, n, steps) {
    const pts = [];
    for (let i = 0; i <= steps; i++) {
      const t = (Math.PI / 2) * (i / steps);
      const x = Math.pow(Math.cos(t), 2 / n) * r;
      const y = Math.pow(Math.sin(t), 2 / n) * r;
      pts.push([x, y]);
    }
    return pts;
  }

  function squirclePathD(w, h, r, n, steps) {
    r = Math.min(r, w / 2, h / 2);
    if (r <= 0.5) return `M0 0 H${w} V${h} H0 Z`;
    const corner = superellipseCorner(r, n, steps || 8);

    const tr = corner.map(([x, y]) => [w - r + x, r - y]).reverse();
    const br = corner.map(([x, y]) => [w - r + x, h - r + y]);
    const bl = corner.map(([x, y]) => [r - x, h - r + y]).reverse();
    const tl = corner.map(([x, y]) => [r - x, r - y]);

    const all = [[r, 0], ...tr.slice(1), ...br.slice(1), ...bl.slice(1), ...tl.slice(1)];
    let d = `M${all[0][0].toFixed(2)} ${all[0][1].toFixed(2)}`;
    for (let i = 1; i < all.length; i++) d += ` L${all[i][0].toFixed(2)} ${all[i][1].toFixed(2)}`;
    return d + ' Z';
  }

  function apply(el) {
    const r = parseFloat(el.dataset.squircle);
    if (!r || r <= 0) return;
    const smoothing = el.dataset.squircleSmoothing ? parseFloat(el.dataset.squircleSmoothing) : 0.6;
    const n = 2 + Math.max(0, Math.min(1, smoothing)) * 3;
    const w = el.clientWidth;
    const h = el.clientHeight;
    if (!w || !h) return;
    const d = squirclePathD(w, h, r, n);
    el.style.clipPath = `path('${d}')`;
  }

  function initSquircles(root) {
    const scope = root || document;
    const els = scope.querySelectorAll('[data-squircle]');
    els.forEach((el) => {
      apply(el);
      if (!el.__squircleObserved) {
        el.__squircleObserved = true;
        new ResizeObserver(() => apply(el)).observe(el);
      }
    });
  }

  global.initSquircles = initSquircles;
  global.__kukiSquirclePathD = squirclePathD;
})(window);
