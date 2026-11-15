# V7: single-panel high-quality physics test

This is an experimental quality baseline for the **existing mung_video project**. V4's 20-pane challenge and V6's slingshot sequence remain untouched.

## Delivered
- One 10 mm thick refractive glass pane in a bespoke photographic stand
- New non-Voronoi radial fracture mesh: 140 interlocking primary pieces + 135 central tiny shards
- Native Blender rigid-body dynamics after staggered fracture release
- Physical collisions with a concrete floor; falling, bouncing and piling fragments
- Cycles with a Poly Haven HDRI for recorded studio-light reflections
- H.264/AAC 720 × 1280, 24 FPS, 3.5 seconds, impact at frame 38
- Mixed prerecorded glass sound effects from existing locally licensed Mixkit sources
- Browser comparison of V6 and V7, including start and first-impact alignment

## Source/licensing
- HDRI: Poly Haven Studio Small 09 (Sergej Majboroda), 1k EXR
  - https://polyhaven.com/a/studio_small_09
  - https://polyhaven.com/license
  - CC0; the HDRI is redistributable
- Real sound recordings: Mixkit, downloaded earlier in V4.
  - https://mixkit.co/free-sound-effects/
  - Source WAV files and the isolated sound mix remain local and excluded from Git.

## Limitations
- This is **not** the 20-glass challenge yet.
- The crack topology is procedurally defined before contact, not computed from true material fracture propagation.
- The prefractured pane is switched to rigid bodies during impact; the post-release dynamics are calculated using Blender rigid-body physics.
- Still a CGI visual prototype. Photorealism cannot be assumed without review on real playback.
- The projectile is animated; the complete momentum transfer between steel and glass is not measured.

## Operation
From the project root, open `OPEN_GLASS_V6_VS_V7.cmd` to view V6 and V7 side by side.

To rebuild with Blender 5.2.3:
1. Run `build_glass_v7_quality.py` in Blender background.
2. Run `run_glass_v7.ps1 -Mode preview` to check frames first.
3. Run `run_glass_v7.ps1 -Mode full` (skips intact PNGs).
4. Run `mix_glass_v7_audio.py`.
5. Run `assemble_glass_v7.py` after all frames are present.

The existing scripts are designed for Windows paths already used by the mung_video project.
