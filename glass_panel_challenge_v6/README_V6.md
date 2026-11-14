# V6 quality shot — single continuous camera

This is a **3.5-second 720 × 1280 proof** for glass-run visual quality, built on the V5 one-pane test and kept separate from V4's finished 20-pane video.

## Implemented
- Continuous 3D shot from a drawn-back slingshot, release, following steel ball, to one glass pane.
- Replaced basic straight timber bars with a contoured hardwood fork, dark elastic bands, curved caps, handle texture, and padded leather pouch.
- Replaced the empty-fracture frame: the entire prefractured pane remains visible at the impact frame before the interior fragments fly and the outer fragments release later.
- 96 major refractive glass fragments and 185 smaller 3D chips, with deterministic speed/gravity/spin and delayed outer breakaway.
- The projectile continues through the pane, falls under an art-directed gravity arc, bounces against the floor, then rolls to rest. This corrects the former hovering-ball ending.
- Less harsh white reflections, shallow camera focus, neutral studio lights, and physically thick refractive surfaces.
- Licensed real sound clips mixed locally (tension, flight, breaking glass, falling pieces).

## Important limits
- Still a procedural art-directed animation, not measured breakage; glass fragment movement is keyed rather than a physically solved stress simulation.
- This is **one pane only**; there is no V6 20-pane full challenge yet. The original V4 complete challenge remains unchanged.
- Larger outer glass polygons still have a recognizably cellular fracture pattern; fully irregular cracking and breakage require a more advanced fracture system.
- Licensed original Mixkit WAV files and isolated audio mix are excluded from Git. The combined audio is embedded into the finished MP4.

## View
Run `OPEN_GLASS_V5_VS_V6.cmd` from the project root to compare earlier V5 single-pane footage with the improved V6 release-and-impact shot. Use the first-impact button for synchronized collision viewing.

## Render
Installed Blender: 5.2.3 LTS, GPU Cycles, 48 samples, 84 frames at 24 FPS. Output H.264/AAC 720 × 1280 MP4. All PNG frames must decode before video assembly.
