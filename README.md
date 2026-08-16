# Joinery Bench

A cabinetry layout tool for the kitchen at **No. 409 Tara Road, Mangawhai** — and for any
other run of joinery in the house.

Open `index.html` in a browser. No build step, no dependencies, no network calls.

## What it does

Drag cabinetry around a room and get live millimetre feedback. The consented drawing sits
underneath, pinned to the same coordinate grid, so a layout you draw here lands exactly
where it would on site.

- **Plan underlay** — the kitchen region of Studio 4 sheet A08, rendered at 600 dpi and
  registered to the drawing's own millimetre origin. Toggle with **Drawing**, fade with the
  slider.
- **Catalogue** — base cabinets, tall units, overheads, islands, wardrobe joinery,
  bathroom joinery, appliances and fixtures. Click to place.
- **Snapping** — three kinds of line: the edges of anything nearby so units butt up, the
  same edges seen across the room so parallel runs line up, and **centre marks** so an item
  can be centred on another unit, on a wall, or on the room. Whatever it locked onto is
  drawn as a guide while you drag — a long-short-long centre line with a circled crosshair
  means a centre match. Hold `Alt` to place freely at 1 mm.
- **Demolition** — walls printed on the drawing but not modelled by the app (the laundry
  and bathroom walls, say) can be knocked out. Hit **Demo**, drag a box over the wall, and
  that patch of the drawing is removed and hatched the way a demolition sheet marks it.
  Select it and hit 🗑 to put it back. This erases the drawing only; the room model and its
  clearances are untouched.
- **Stretch a whole run** — select any cabinet in a run and drag the grip at either end.
  On release you choose where the extra length goes: spread evenly across the run, or
  loaded into one, two or three specific cabinets. Appliances are held at their fixed
  sizes, gaps are preserved, and cooktops and sinks travel with the unit they sit on.
- **Editable walls** — click any perimeter wall to select it, then delete it with the 🗑
  to open that side right through. Nothing else moves, and **Room shell** shows all four
  sides and puts a deleted one back.
- **Draggable partitions** — grab the scullery wall and slide it. The plan dimensions both
  sides live, so you can see what a walk-in scullery costs the kitchen run before
  committing. Add or delete walls from **Room shell**.
- **Clearances** — every unit reports the clear distance from its working face to whatever
  is straight ahead. Under 900 mm is flagged; 1,200 mm and over reads as comfortable.
  Partitions count as obstacles only where they're solid, so a doorway doesn't read as a
  wall you'd walk into.
- **Perspective view** — switch to **3D** to orbit the room. Fixed viewpoints for the
  dining side, the entry, the scullery end, overhead, and eye level at 1.6 m. Walls
  standing between you and the room drop away so you can always see in. View only;
  editing stays on the plan.
- **In-app guidance** — a walkthrough on first open (reachable any time from **?**), and a
  strip above the canvas that says what you can do right now and speaks up when something
  is wrong.
- **Schedule** — running count and lineal millimetres by item, with a bench-run total.
- **Presets** — the kitchen as consented, the same shell emptied out for a redesign, plus
  blank room, walk-in wardrobe and bathroom starters.

## Shortcuts

| | |
|---|---|
| drag | move an item, or a partition wall |
| `Alt` + drag | ignore snapping, place to 1 mm |
| `R` | rotate 90° |
| arrows | nudge 10 mm (`Shift` for 1 mm) |
| `D` | duplicate |
| `Delete`, or the 🗑 button | remove the selected item, partition or wall |
| `Ctrl`/`Cmd` `Z` | undo (`Shift` to redo) |
| space + drag, or wheel | pan |
| wheel | zoom |

## Where the dimensions came from

Every measurement is traced from the vector geometry of sheet A08 of the approved building
consent set (KDC 260177_PL_ISSUED), not eyeballed from a raster. Scale was confirmed against
the 90 mm framing, which reads as 5.1 pt on the A1 sheet — exactly 1:50.

Origin `(0,0)` is the inner face of the west wall by the inner face of the north wall.

| | |
|---|---|
| Bench run depth | 630 mm |
| Galley walkway, bench face to island | 1,200 mm |
| Island | 900 deep × 3,495 long |
| Wall face to island far edge | 2,730 mm |
| Scullery zone | 2,640 wide × 671 deep |
| Scullery bench | 2,010 × 630 |
| Slider opening | 1,989 mm |
| Kitchen zone | 2,730 × 5,282 mm |

The 2,640 mm printed on the sheet is the scullery's overall width; the bench inside it is
2,010. The scullery is not a full-width wall — it is a 651 return at the west end and a 90
stub at the east, with three 660 **full-height cavity sliders** closing the gap between
them. Because those doors run to the floor, nothing may sit in their track, and the app
flags any cabinet that does.

## The sandbox

`sandbox.html` is a throwaway copy to design in. It opens on the cleared shell with the
drawing underneath, keeps its own browser storage so it can never overwrite the layout
saved in `index.html`, and has a **Reset** button to start again.

It is generated, not hand-edited — after changing `index.html`, run:

```
node make-sandbox.mjs
```

## Saving

**Save** keeps the current layout in this browser. **Export** shows the whole layout as
JSON to copy out, and accepts pasted JSON to load back in. Opened as a local file, Export
also offers a `.json` download.
