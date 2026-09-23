import { toKebabCase as u } from "@primeuix/utils/object";
import { defineComponent as p, computed as c, h as l } from "vue";
const d = ([t, o]) => {
  const { key: i, ...e } = o, n = {};
  for (const [s, r] of Object.entries(e))
    n[u(s)] = r;
  return l(t, { key: i, ...n });
}, v = (t) => {
  const o = {
    size: {
      type: [Number, String],
      default: void 0
    },
    color: {
      type: String,
      default: void 0
    },
    spin: {
      type: Boolean,
      default: !1
    }
  };
  return { Icon: p({
    name: t.name.split("-").map((e) => e.charAt(0).toUpperCase() + e.slice(1)).join(""),
    props: o,
    setup(e, { attrs: n }) {
      const s = c(() => e.size ?? 20), r = c(() => ({
        ...e.size && { "--px-icon-size": `${e.size}px` },
        ...e.color && { color: e.color }
      })), a = c(() => ["p-icon", `p-icon-${t.name}`, e.spin && "p-icon-spin"].filter(Boolean));
      return () => l(
        "svg",
        {
          ...t.svg,
          width: s.value,
          height: s.value,
          "aria-hidden": "true",
          ...n,
          style: r.value,
          class: a.value
        },
        t.nodes.map(d)
      );
    }
  }), props: o };
};
export {
  v as createIcon
};
