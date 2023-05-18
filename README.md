# ynot3

A simple image annotation program compatible with x11 and wayland.
Targetting an efficient workflow and minimal dependencies.

- can save to disk or copy to clipboard (requires `xclip` or `wl-copy`).
- copy to clipboard on exit
- unlimited undo
- antialiasing
- very simple user interface

Supported shapes:

- enumerated bullets
- rectangles
- arrows

## Screenshot

![](https://github.com/fdev31/ynot3/blob/0e68c2eca32b6ba8b324b9822a188fa9fce089ec/img/annotated.jpg)

1. Active tool
    - *(4)* rectangle
    - *(5)* arrow
    - *(6)* enumerated bullet
2. Active color
3. Action buttons
    - *(7)* undo
    - *(8)* copy to clipboard
    - *(9)* save to `/tmp/annotated.jpg`
    - *(10)* toggle large mode (everything is magnified)
    - *(11)* clear changes (remove all annotations)

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
