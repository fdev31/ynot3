# ynot3

A simple image annotation program compatible with x11 and wayland.
Targetting an efficient workflow and minimal dependencies.

- can save to disk or copy to clipboard (requires `xclip` or `wl-copy`).
- copy to clipboard on exit
- unlimited undo
- antialiasing
- snapping for better alignments (override setting `SNAPPING` environment variable, defaults to 8)
- very simple user interface

Supported shapes:

- enumerated bullets
- rectangles
- arrows

## Screenshot

![](https://raw.githubusercontent.com/fdev31/ynot3/main/img/annotated.png)

1. Active tool
    - *(4)* rectangle
    - *(5)* arrow
    - *(6)* enumerated bullet
2. Active color
3. Action buttons
    - *(7)* undo (shorcut: backspace)
    - *(8)* copy to clipboard
    - *(9)* save to `/tmp/annotated.jpg` (override setting `ANNOTATED` environment variable)
    - *(10)* toggle large mode (everything is magnified)
    - *(11)* clear changes (remove all annotations) (shortcut: "c")

## Example usage

### Edit an existing image

`ynote3 ~/Images/example.jpg`

### Edit a screenshot

A simple script for Wyland using `grimshot`:

```bash
#!/bin/sh
FN="/tmp/shot.png"
grimshot save area "${FN}"
exec ynote3 "${FN}"
```
