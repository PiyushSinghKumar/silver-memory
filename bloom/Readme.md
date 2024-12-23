# Blooming Effect Script

This script applies a blooming effect to an input image and returns the image with the blooming effect applied.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Required Python packages:
  - `argparse`
  - `numpy`
  - `Imath`
  - `OpenEXR`
  - `torch`
  - `Pillow`

### Usage

To apply the blooming effect to an image, run the script with the following command:

```sh
python blooming.py --input-image <input_image_path> --output-image <output_image_path> [--lambda-param <lambda_value>] [--alpha <alpha_value>] [--constant <constant_value>]
