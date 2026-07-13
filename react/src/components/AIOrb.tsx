import * as React from 'react';

export interface AIOrbProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Path to the animated sparkle SVG. Defaults to the bundled KuKi asset. */
  sparkleSrc?: string;
  label?: string;
}

// module-level cache: fetch the source SVG text once, share across every orb instance
let sparkleTextPromise: Promise<string> | null = null;
function loadSparkleText(src: string): Promise<string> {
  if (!sparkleTextPromise) sparkleTextPromise = fetch(src).then((r) => r.text());
  return sparkleTextPromise;
}

let uidCounter = 0;

/** Suffixes every id/keyframe-name in the sparkle SVG so multiple orbs never share one. */
function uniquify(svgText: string, uid: string): string {
  const renames: [string, string][] = [
    ['kf_Vector_3_transform_0', `kf_Vector_3_transform_0_${uid}`],
    ['kf_Vector_3_opacity_0', `kf_Vector_3_opacity_0_${uid}`],
    ['kf_Vector_2_transform_0', `kf_Vector_2_transform_0_${uid}`],
    ['kf_Vector_2_opacity_0', `kf_Vector_2_opacity_0_${uid}`],
    ['kf_Vector_transform_0', `kf_Vector_transform_0_${uid}`],
    ['kf_Vector_opacity_0', `kf_Vector_opacity_0_${uid}`],
    ['Vector_3', `Vector_3_${uid}`],
    ['Vector_2', `Vector_2_${uid}`],
    ['Vector', `Vector_${uid}`],
    ['clip0_83_543', `clip0_83_543_${uid}`],
  ];
  let out = svgText;
  for (const [from, to] of renames) out = out.split(from).join(to);
  return out.replace('width="56" height="56"', 'width="100%" height="100%"');
}

/**
 * Pet AI entry point. The swirling background is a CSS approximation of a shader
 * (blurred rotating conic gradient, screen-blended over a radial base) — no WebGL.
 *
 * The sparkle burst on top is KuKi's real animated asset. It's fetched once and
 * inlined into the DOM (with every id/keyframe-name uniquified per instance)
 * rather than loaded via `<img>` — browsers don't reliably run an SVG's own CSS
 * `@keyframes` when it's embedded as an `<img>`, so the sparkles (which start
 * every loop at `opacity:0`) render permanently invisible in that context.
 */
export const AIOrb = React.forwardRef<HTMLButtonElement, AIOrbProps>(
  ({ sparkleSrc = '/assets/ai-sparkle-animated.svg', label = 'Pet AI', className = '', ...rest }, ref) => {
    const [markup, setMarkup] = React.useState<string>('');
    const uidRef = React.useRef<string>(`aiorb${++uidCounter}_${Math.random().toString(36).slice(2, 7)}`);

    React.useEffect(() => {
      let cancelled = false;
      loadSparkleText(sparkleSrc).then((text) => {
        if (!cancelled) setMarkup(uniquify(text, uidRef.current));
      });
      return () => {
        cancelled = true;
      };
    }, [sparkleSrc]);

    return (
      <button ref={ref} type="button" className={`kuki-ai-orb ${className}`} aria-label={label} {...rest}>
        <span
          className="kuki-ai-orb__sparkle"
          aria-hidden
          dangerouslySetInnerHTML={markup ? { __html: markup } : undefined}
        />
      </button>
    );
  },
);
AIOrb.displayName = 'AIOrb';
