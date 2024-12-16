#!/usr/bin/env python3

"""
This script will take in any input image and apply blooming effect to it and return the image with blooming effect.
"""

import argparse
import numpy as np
import Imath
import OpenEXR
import torch
import torch.nn.functional as F
import numpy.typing as npt
from dataclasses import dataclass
from pathlib import Path
from typing import NewType, Any
from PIL import Image

Array_2D = NewType("Array_2D", npt.NDArray[np.float32])

def create_array2d(data: npt.NDArray[np.float32]) -> Array_2D:
    assert data.ndim == 2, "Expected 2-dimensional array"
    return Array_2D(data)

def find_rgb_channels(header: dict) -> list[str]:
    rgb_channels = [
        channel
        for channel in header["channels"].keys()
        if channel.endswith(("R", "G", "B"))
    ]
    rgb_channels.sort(reverse=True)
    if len(rgb_channels) != 3:
        raise ValueError("Check the image, can't find all RGB channels")
    return rgb_channels

@dataclass(frozen=True)
class ExrOutput:
    rgb_channels: dict[str, Array_2D]
    other_channels: dict[str, Array_2D]
    header: dict[str, Any]

def read_exr_image(image_path: Path) -> ExrOutput:
    exr_file = OpenEXR.InputFile(str(image_path))
    header = exr_file.header()
    image_channels = header["channels"].keys()

    rgb_channels = {}
    other_channels = {}
    required_channels = find_rgb_channels(header)

    for channel in image_channels:
        data = exr_file.channel(channel, Imath.PixelType(Imath.PixelType.FLOAT))
        array_data = np.frombuffer(data, dtype=np.float32).reshape(
            header["dataWindow"].max.y + 1, header["dataWindow"].max.x + 1
        )
        if channel in required_channels:
            rgb_channels[channel] = create_array2d(array_data)
        else:
            other_channels[channel] = create_array2d(array_data)
    exr_file.close()

    return ExrOutput(rgb_channels, other_channels, header)

def read_standard_image(image_path: Path) -> dict[str, Array_2D]:
    image = Image.open(image_path).convert("RGB")
    image_np = np.asarray(image, dtype=np.float32) / 255.0  # Normalize to [0, 1]
    return {
        channel: create_array2d(image_np[..., idx])
        for idx, channel in enumerate(["R", "G", "B"])
    }

def write_exr_image(
    output_image_path: Path,
    combined_channels: dict,
    original_other_channels: dict,
    header: dict,
) -> None:
    new_image_channels = {}

    new_image_channels.update(combined_channels)
    new_image_channels.update(original_other_channels)

    new_image_channels = {k: v.tobytes() for k, v in new_image_channels.items()}
    new_image = OpenEXR.OutputFile(str(output_image_path), header)
    new_image.writePixels(new_image_channels)
    new_image.close()
    #also save as jpg
    jpg_path = output_image_path.with_suffix('.jpg')
    print(f"Saving image as {jpg_path}")
    combined_image = np.stack(
        [combined_channels[channel] for channel in ["R", "G", "B"]], axis=-1
    )
    combined_image = np.clip(combined_image * 255, 0, 255).astype(np.uint8)
    output_image = Image.fromarray(combined_image, mode="RGB")
    output_image.save(jpg_path)
    

def write_standard_image(output_image_path: Path, rgb_channels: dict[str, Array_2D]) -> None:
    print(f"Writing image as {output_image_path}")
    combined_image = np.stack(
        [rgb_channels[channel] for channel in ["R", "G", "B"]], axis=-1
    )
    combined_image = np.clip(combined_image * 255, 0, 255).astype(np.uint8)
    output_image = Image.fromarray(combined_image, mode="RGB")
    output_image.save(output_image_path)
    #also save as jpg
    jpg_path = output_image_path.with_suffix('.jpg')
    print(f"Saving image as {jpg_path}")
    output_image.save(jpg_path)

def image_to_tensor(image_array: Array_2D) -> torch.Tensor:
    image_tensor = torch.tensor(image_array, dtype=torch.float32)
    return image_tensor

def create_rgb_tensor(rgb_channels: dict) -> torch.Tensor:
    rgb_tensor = torch.stack(
        [image_to_tensor(image_array) for image_array in rgb_channels.values()]
    )
    return rgb_tensor

def check_kernel(kernel: torch.Tensor):
    center_pixel = kernel[kernel.shape[-2] // 2, kernel.shape[-1] // 2]
    if torch.abs(center_pixel - 1) < 1e-6:
        raise ValueError(
            "Center pixel of the kernel is too close to 1, the kernel will not have any effect"
        )

def create_2d_kernel(
    kernel_radius: int,
    lambda_param: float,
    constant: float,
) -> torch.Tensor:
    xx, yy = torch.meshgrid(
        torch.arange(-kernel_radius, kernel_radius),
        torch.arange(-kernel_radius, kernel_radius),
        indexing="ij",
    )
    distance = torch.sqrt(xx**2 + yy**2)
    kernel = torch.exp(-lambda_param * distance)
    kernel = kernel + constant
    kernel = kernel / kernel.sum()
    check_kernel(kernel)
    return kernel

def process_rgb_tensor(rgb_tensor: torch.Tensor, kernel: torch.Tensor) -> torch.Tensor:
    # Compute padding of rgb_tensor so that rgb_tensor has the same dimensions as kernel.
    w_padding = (kernel.shape[-1] - rgb_tensor.shape[-1]) // 2
    h_padding = (kernel.shape[-2] - rgb_tensor.shape[-2]) // 2
    padded = F.pad(
        rgb_tensor, (w_padding, w_padding, h_padding, h_padding), "constant", 0
    )
    assert (
        padded.shape[-2:] == kernel.shape[-2:]
    ), "Padded image and kernel shape mismatch"

    # Compute the convolution via element-wise multiplication in FFT domain.
    rfft_rgb_tensor = torch.fft.rfft2(padded)
    rfft_kernel = torch.fft.rfft2(torch.fft.fftshift(kernel))
    result = torch.fft.irfft2(rfft_rgb_tensor * rfft_kernel)

    # Remove padding again.
    result = result[..., h_padding:-h_padding, w_padding:-w_padding]
    return result

def process_image(
    original_rgb_channels: dict,
    kernel: torch.Tensor
) -> dict:
    try:
        rgb_tensor = create_rgb_tensor(original_rgb_channels)
        processed_rgb_tensor = process_rgb_tensor(rgb_tensor, kernel)
        processed_rgb_channels = {}
        for key, value in zip(original_rgb_channels.keys(), processed_rgb_tensor):
            processed_rgb_channels[key] = create_array2d(value.cpu().numpy())

    except Exception as e:
        raise RuntimeError(f"Failed to process image: {e}")

    return processed_rgb_channels

def add_processed_channel_to_original(
    processed_rgb_channels: dict,
    original_rgb_channels: dict,
    alpha: float,
) -> dict:

    combined_rgb_channels = {
        channel: create_array2d(
            (1 - alpha) * original_rgb_channels[channel]
            + alpha * processed_rgb_channels[channel]
        )
        for channel in original_rgb_channels
    }

    return combined_rgb_channels

def parse_arguments():
    parser = argparse.ArgumentParser(description="Apply blooming effect to an image")
    parser.add_argument(
        "--input-image",
        "-i",
        type=Path,
        help="Path to the input image",
        required=True,
    )
    parser.add_argument(
        "--output-image",
        "-o",
        type=Path,
        help="Path to the output image",
        required=True,
    )
    parser.add_argument(
        "--lambda-param",
        "-l",
        type=float,
        help="Lambda parameter for the kernel for strength of curve",
        default=0.1,
    )
    parser.add_argument(
        "--alpha",
        "-a",
        type=float,
        help="Alpha value for combining the processed image with original image",
        default=0.5,
    )
    parser.add_argument(
        "--constant",
        "-c",
        type=float,
        help="Constant value to be added to the kernel",
        default=0.01,
    )

    return parser.parse_args()

def main():

    args = parse_arguments()

    try:
        if args.input_image.suffix.lower() == ".exr":
            exr_output = read_exr_image(args.input_image)
            original_rgb_channels = exr_output.rgb_channels
            original_other_channels = exr_output.other_channels
            header = exr_output.header

            kernel_radius = max(header["dataWindow"].max.x, header["dataWindow"].max.y) + 1
            kernel = create_2d_kernel(kernel_radius, args.lambda_param, args.constant)

            processed_rgb_channels = process_image(
                original_rgb_channels=original_rgb_channels,
                kernel=kernel            
            )

            combined_rgb_channels = add_processed_channel_to_original(
                processed_rgb_channels=processed_rgb_channels,
                original_rgb_channels=original_rgb_channels,
                alpha=args.alpha,
            )

            write_exr_image(
                output_image_path=args.output_image,
                combined_channels=combined_rgb_channels,
                original_other_channels=original_other_channels,
                header=header,
            )

        elif args.input_image.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            original_rgb_channels = read_standard_image(args.input_image)

            kernel_radius = max(original_rgb_channels["R"].shape) + 1
            kernel = create_2d_kernel(kernel_radius, args.lambda_param, args.constant)

            processed_rgb_channels = process_image(
                original_rgb_channels=original_rgb_channels,
                kernel=kernel,
            )

            combined_rgb_channels = add_processed_channel_to_original(
                processed_rgb_channels=processed_rgb_channels,
                original_rgb_channels=original_rgb_channels,
                alpha=args.alpha,
            )

            write_standard_image(output_image_path=args.output_image, rgb_channels=combined_rgb_channels)

        else:
            raise ValueError("Unsupported image format. Only EXR, PNG, JPG, and JPEG are supported.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()