# Card Video Direction

## Goal

Create a three-second seamless-feeling motion companion for every tarot card while preserving the original illustration as the visual authority.

## Generation contract

- Use the same card image as both MiniMax first frame and last frame.
- Use MiniMax start-end-frame interpolation (`Hailuo-02`).
- Keep the camera locked. Do not zoom, pan, rotate, crop, or reframe.
- Animate only secondary details: clouds, mist, water, fabric edges, petals, lantern light, hair ornaments, small particles, and restrained breathing.
- Preserve faces, hands, costumes, architecture, card symbolism, composition, and color palette.
- Add no text, calligraphy, symbols, objects, people, borders, logos, or watermarks.
- Avoid morphing, melting, flicker, anatomy changes, scene cuts, and large character movement.

## Delivery contract

- MP4, H.264, no audio.
- `768 x 1152`, vertical `2:3`.
- Exactly `3.000` seconds at `30 fps`.
- Frame 0 and frame 89 show the original card artwork.
- Stable filename matching the card image stem, for example `00-fool.mp4`.

The local post-processing step retimes the full generated interpolation to three seconds and overlays the original artwork on the first and final output frames.
