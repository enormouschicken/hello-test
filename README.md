# Joinery Bench

A cabinetry layout tool for the kitchen at **No. 409 Tara Road, Mangawhai** — and for any
other run of joinery in the house.

Open `index.html` in a browser. No build step, no dependencies, no network calls.

## What it does

Drag cabinetry around a room and get live millimetre feedback. The consented drawing sits
underneath, pinned to the same coordinate grid, so a layout you draw here lands exactly
where it would on site.

- **Plan underlay** — the kitchen region of Studio 4 sheet A08, rendered at 600 dpi and
  registered to the drawing's own millimetre origin. Toggle with **Plan**, fade with the
  slider.
- **Catalogue** — base cabinets, tall units, overheads, islands, wardrobe joinery,
  bathroom joinery, appliances and fixtures. Click to place.
- **Snapping** — cabinet edges snap to walls, partitions and each other. Hold `Alt` while
  dragging to place freely at 1 mm.
- **Clearances** — every unit reports the clear distance from its working face to whatever
  is straight ahead. Under 900 mm is flagged; 1,200 mm and over reads as comfortable.
- **Schedule** — running count and lineal millimetres by item, with a bench-run total.
- **Presets** — the kitchen as consented, the same shell emptied out for a redesign, plus
  blank room, walk-in wardrobe and bathroom starters.

## Shortcuts

| | |
|---|---|
| drag | move |
| `R` | rotate 90° |
| arrows | nudge 10 mm (`Shift` for 1 mm) |
| `D` | duplicate |
| `Delete` | remove |
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
| Scullery | 2,640 wide × 671 deep |
| Kitchen zone | 2,730 × 5,282 mm |

The 2,640 mm scullery width matches the dimension string printed on the sheet, which
confirms the trace.

## Saving

**Save** keeps the current layout in this browser. **Export** shows the whole layout as
JSON to copy out, and accepts pasted JSON to load back in. Opened as a local file, Export
also offers a `.json` download.
