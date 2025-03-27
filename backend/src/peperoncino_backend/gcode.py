import collections
import typing

import vpype as vp

from peperoncino_backend.consts import MAX_FILE_LINES


def convert_svg_to_gcode(input_path, output_path, quantization=0.15):
    svg: vp.Document = vp.read_multilayer_svg(input_path, quantization=quantization)
    while svg.segment_count() > MAX_FILE_LINES:  # ~1 line per segment
        quantization += 0.05
        svg = vp.read_multilayer_svg(input_path, quantization=quantization)

    # svg.fit_page_size_to_content()
    # Scale it to fit 400x250mm preserving the aspect ratio
    with open(output_path, "w") as fs:
        gwrite(
            svg,
            output=fs,
            zero_align=True,
            linesort=True,
            invert_x=True,
            offset_x=15,
            offset_y=20,
            # fit_page=True,
        )


"""
The following functions are taken from the package vpype-gcode at https://github.com/plottertools/vpype-gcode, modified to work without the CLI, and only for what is needed in the context of this project.
The original license is included:
```
MIT License

Copyright (c) 2020 David Olsen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS ORh
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
"""


def invert_axis(
    document: vp.Document,
    invert_x: bool,
    invert_y: bool,
) -> vp.Document:
    """Inverts none, one or both axis of the document.
    This applies a relative scale operation with factors of 1 or -1
    on the two axis to all layers. The inversion happens relative to
    the center of the bounds.
    """

    bounds = document.bounds()

    if not bounds:
        return document

    origin = (
        0.5 * (bounds[0] + bounds[2]),
        0.5 * (bounds[1] + bounds[3]),
    )

    document.translate(-origin[0], -origin[1])
    document.scale(-1 if invert_x else 1, -1 if invert_y else 1)
    document.translate(origin[0], origin[1])

    return document


def write_template(
    template: str | None, document, current_layer, output, **context_vars: typing.Any
):
    """Expend a user-provided template using `format()`-style substitution."""
    if template is None:
        return
    dicts = [context_vars, document.metadata]
    if current_layer is not None:
        dicts.append(current_layer.metadata)

    try:
        output.write(template.format_map(collections.ChainMap(*dicts)))
    except KeyError as exc:
        raise KeyError(
            f"key {exc.args[0]!r} not found in context variables or properties"
        )


def gwrite(
    document,
    output: typing.TextIO,
    *,
    offset_x=0.0,
    offset_y=0.0,
    scale_x=1.0,
    scale_y=1.0,
    invert_x=False,
    invert_y=False,
    zero_align=True,
    linesort=True,
    fit_page=False,
):
    document_start = "G21\nG17\nG90\n"
    document_end = "M2\n"
    segment_first = "G00 X{x:.4f} Y{y:.4f}\n"
    segment = "G01 X{x:.4f} Y{y:.4f}\n"
    unit = "mm"

    unit_scale = vp.convert_length(unit)

    if zero_align:
        min_x, min_y, _, _ = document.bounds()
        document.translate(-min_x, -min_y)

    document.scale(scale_x / unit_scale, scale_y / unit_scale)

    if invert_x or invert_y:
        document = invert_axis(document, invert_x, invert_y)

    document.translate(offset_x, offset_y)

    if fit_page:
        _, _, max_x, max_y = document.bounds()
        if max_x > 270 or max_y > 200:
            if max_x / max_y > 27 / 20:
                scale = 270 / max_x
            else:
                scale = 200 / max_y

            document.scale(scale, scale)

    current_layer: vp.LineCollection | None = None

    filename = output.name
    write_template(
        document_start,
        document=document,
        current_layer=current_layer,
        output=output,
        filename=filename,
    )

    last_x = 0
    last_y = 0
    xx = 0
    yy = 0

    for layer_index, (layer_id, layer) in enumerate(document.layers.items()):
        current_layer = layer  # used by write_template()

        for lines_index, line in enumerate(layer):
            for segment_index, seg in enumerate(line):
                x = seg.real
                y = seg.imag
                dx = x - last_x
                dy = y - last_y
                idx = int(round(x - xx))
                idy = int(round(y - yy))
                xx += idx
                yy += idy
                if segment_index == 0:
                    seg_write = segment_first
                else:
                    seg_write = segment

                write_template(
                    seg_write,
                    document=document,
                    current_layer=current_layer,
                    output=output,
                    x=x,
                    y=y,
                    dx=dx,
                    dy=dy,
                    _x=-x,
                    _y=-y,
                    _dx=-dx,
                    _dy=-dy,
                    ix=xx,
                    iy=yy,
                    idx=idx,
                    idy=idy,
                    index=segment_index,
                    index1=segment_index + 1,
                    segment_index=segment_index,
                    segment_index1=segment_index + 1,
                    lines_index=lines_index,
                    lines_index1=lines_index + 1,
                    layer_index=layer_index,
                    layer_index1=layer_index + 1,
                    layer_id=layer_id,
                    filename=filename,
                )

                last_x = x
                last_y = y

        current_layer = None

    write_template(
        document_end,
        document=document,
        current_layer=current_layer,
        output=output,
        filename=filename,
    )
