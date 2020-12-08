# Depix

Depix is a tool for recovering passwords from pixelized screenshots.

This implementation works on pixelized images that were created with a linear box filter.

In [this article](https://www.linkedin.com/pulse/recovering-passwords-from-pixelized-screenshots-sipke-mellema) I cover background information on pixelization and similar research.

## Example

`python depix.py -p images/testimages/testimage3_pixels.png -s images/searchimages/debruinseq_notepad_Windows10_closeAndSpaced.png -o output.png`

![image](docs/img/Recovering_prototype_latest.png)

## Usage

* Cut out the pixelated blocks from the screenshot as a single rectangle.
* Paste a [De Bruijn sequence](https://damip.net/article-de-bruijn-sequence) with expected characters in an editor with the same font settings (text size, font, color, hsl).
* Make a screenshot of the sequence. If possible, use the same screenshot tool that was used to create the pixelized image.
* Run `python depix.py -p [pixelated rectangle image] -s [search sequence image] -o output.png`

## Algorithm

The algorithm uses the fact that the linear box filter processes every block separately. For every block it pixelizes all blocks in the search image to check for direct matches.

For most pixelized images Depix manages to find single-match results. It assumes these are correct. The matches of surrounding multi-match blocks are then compared to be geometrically at the same distance as in the pixelized image. Matches are also treated as correct. This process is repeated a couple of times.

After correct blocks have no more geometrical matches, it will output all correct blocks directly. For multi-match blocks, it outputs the average of all matches.

## Misc

### Usage issues

* **Dependency Issues** See: https://github.com/beurtschipper/Depix/issues/12
* 
