# sony_pixel_shift_processor
Own rough implementation of processing (assemble) sony pixel-shift RAW files

Usage:

1) Start script
2) When fileopen dialog appear, select FIRST RAW file in batch of 4 files series to be processed.
3) Wait
4) See the processed 16-bit TIFF file (with name of first RAW file + PSMS suffix) in the same folder as RAW files

Limitations:
1) No lens correction made
2) No subpixel edge smoothing filtering
3) ARQ input not supported yet

TO DO (in future may be):
1) Replace opencv module with less space consuming (to make more compact executables)
2) Copy EXIF from RAW to TIFF
3) Add support of ARQ input files (when rawpy and it's libraries will support it and API released)
4) Make Windows single-file executable

Requires:
- Python 2.7.x (64 bit!)
- Rawpy module (to extract bayer image and camera data from shot)
- OpenCV-python module (to process image and save to 16-bit TIFF)
