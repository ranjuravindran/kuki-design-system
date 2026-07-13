/**
 * KuKi AI orb sparkle loader.
 *
 * Browsers do NOT reliably run CSS @keyframes animations on SVGs loaded via
 * <img src="...svg">  — this SVG's sparkles start every animation at opacity:0
 * and fade in, so an <img>-embedded copy renders permanently invisible (frozen
 * at its 0% keyframe) in that context. The fix is to inline the SVG directly
 * into the document, where CSS animations always run normally.
 *
 * Inlining verbatim would duplicate ids (id="Vector" etc.) across every orb on
 * the page, which is invalid HTML and lets one orb's #Vector selector leak
 * onto another's. This loader fetches the source SVG once, then for each
 * `<span data-ai-sparkle>` placeholder mints a copy with every id/keyframe
 * name suffixed uniquely before injecting it.
 */
(function (global) {
  let textPromise = null;
  function loadText(src) {
    if (!textPromise) textPromise = fetch(src).then((r) => r.text());
    return textPromise;
  }

  function uniquify(svgText, uid) {
    const renames = [
      ['kf_Vector_3_transform_0', 'kf_Vector_3_transform_0_' + uid],
      ['kf_Vector_3_opacity_0', 'kf_Vector_3_opacity_0_' + uid],
      ['kf_Vector_2_transform_0', 'kf_Vector_2_transform_0_' + uid],
      ['kf_Vector_2_opacity_0', 'kf_Vector_2_opacity_0_' + uid],
      ['kf_Vector_transform_0', 'kf_Vector_transform_0_' + uid],
      ['kf_Vector_opacity_0', 'kf_Vector_opacity_0_' + uid],
      ['Vector_3', 'Vector_3_' + uid],
      ['Vector_2', 'Vector_2_' + uid],
      ['Vector', 'Vector_' + uid],
      ['clip0_83_543', 'clip0_83_543_' + uid],
    ];
    let out = svgText;
    for (const [from, to] of renames) out = out.split(from).join(to);
    // scale to fill its wrapper instead of the source's fixed 56x56
    out = out.replace('width="56" height="56"', 'width="100%" height="100%"');
    return out;
  }

  async function hydrate(root) {
    const scope = root || document;
    const placeholders = scope.querySelectorAll('[data-ai-sparkle]');
    if (!placeholders.length) return;
    let uid = 0;
    for (const el of placeholders) {
      if (el.dataset.aiSparkleDone) continue;
      const src = el.dataset.aiSparkle;
      const text = await loadText(src);
      uid += 1;
      el.innerHTML = uniquify(text, 'orb' + uid + '_' + Math.random().toString(36).slice(2, 7));
      el.dataset.aiSparkleDone = 'true';
    }
  }

  global.hydrateAIOrbs = hydrate;
})(window);
