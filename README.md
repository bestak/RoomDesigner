# Room Planner 565 × 356

A small single-file tool for planning one real room: a draggable top-down plan, a live 3D view, and checks that tell you when a layout doesn't work.

![Room planner showing the plan, the 3D view in evening light, and the checks panel](docs/screenshot.png)

## Use it

Open `room.html` in a browser. There's no build step and nothing to install. The 3D view loads three.js from a CDN, so it needs an internet connection; the plan and checks work without it.

## What it does

- **Plan:** drag, rotate and resize furniture in centimetres. Pieces snap to walls, and each one shows the space it needs in front.
- **3D:** simple models of each piece, with Day, Evening, Night and Main light modes. Lamps, the ceiling pendant, the TV and LED strips give off real light.
- **Styles:** one menu recolours the whole room (wood, fabrics, rugs, bedding, curtains) across 20 colour schemes.
- **Checks:**
  - Overlaps, pieces blocking the door swing, and furniture in the way of the curtains.
  - A 60 cm walking path from the door to every piece you use.
  - Feng shui: the bed and the main desk placed so you can see who's coming.
  - Lighting: every place you use is lit without the ceiling light.
- **Layouts:** ready-made suggestions plus your own, saved in the browser. Use Export / import to move them between browsers or back them up as JSON.

## How it's built

Everything lives in `room.html`:

- **`<script id="core">`:** the room, the furniture catalogue, the layouts and all checks. It has no DOM access, so it can run on its own in Node.
- **Main script:** the SVG plan, the side panel, and the three.js scene.

Room and furniture sizes are the real measurements of one room. For another room, change `ROOM`, `DOOR`, `EDOOR` and `WINDOWS` at the top of the core script. The built-in layouts are placed for this room and won't fit anywhere else.
