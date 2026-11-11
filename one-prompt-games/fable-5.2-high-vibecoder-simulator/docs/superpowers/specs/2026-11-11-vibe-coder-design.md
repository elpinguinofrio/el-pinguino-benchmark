# Vibe Coder Simulator — design (compressed, 20-minute budget)
Source of truth: ../../../spec.md (approved design). Calls made by the builder, nobody was available to ask:
- No node/npm on this machine -> no Vite. Static ES modules + vendored three.module.min.js (r160), run with `python3 -m http.server`. Still a static build for GitHub Pages.
- Look follows the cursor (no pointer lock) so whack-a-ban clicks are instant; WASD walks, Space leans back.
- Left click = appeal / squeeze penguin / fridge beer. Right click (or Shift+click) = punch. E = throw. Q penguin, B beer, V vape.
- Own lightweight debris physics (instanced, pooled, persistent) instead of Rapier (cannot npm install).
- No post-processing bloom (needs extra vendored addons): additive glow sprites + fog instead.
- Personal touch: the penguin wears a tiny red scarf.
- Cut for time: chair model/spin, grab-and-swing props, depth of field, AO.
