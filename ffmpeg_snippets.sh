exit 0
# GTX 1080, Apple compatible
ffmpeg  -hwaccel cuda -hwaccel_output_format cuda -y -i <inputfile>.HDR.H.265.mkv -tag:v hvc1 -c:v hevc_nvenc -preset p7 -profile:v main10 -b:v 1620k -multipass fullres -rc-lookahead 32  -vf "scale_cuda=1920:-2:format=p010le" -color_primaries bt2020 -color_trc smpte2084 -colorspace bt2020nc -c:a ac3 -b:a 384k -ar 48000 -movflags +faststart iphone_compatible_xyz.mp4

```
ffmpeg \
  # 1. HARDWARE ACCELERATION (INPUT)
  -hwaccel cuda \                 # Enables hardware-accelerated decoding using Nvidia CUDA
  -hwaccel_output_format cuda \   # Keeps decoded frames in GPU memory to avoid slow CPU-GPU copying
  -y \                            # Automatically overwrites the output file if it already exists
  
  # 2. INPUT FILE
  -i <inputfile>.HDR.H.265.mkv \ # Path to your source HDR video inside an MKV container
  
  # 3. VIDEO CODEC & QUALITY SETTINGS
  -tag:v hvc1 \                  # Sets the hvc1 FourCC tag (strictly required for HEVC playback on Apple devices)
  -c:v hevc_nvenc \              # Uses the Nvidia hardware-accelerated HEVC/H.265 encoder
  -preset p7 \                   # Preset p7 (slowest encoding speed, but delivers the highest NVENC quality)
  -profile:v main10 \            # Main 10 profile (enables 10-bit color depth, essential for HDR)
  -b:v 1620k \                   # Targets a video bitrate of 1620 kbps
  -multipass fullres \           # Enables two-pass encoding at full resolution for optimal bitrate distribution
  -rc-lookahead 32 \             # Analyzes 32 frames ahead to optimize quality in fast-moving scenes
  
  # 4. VIDEO FILTERS & COLOR METADATA
  -vf "scale_cuda=1920:-2:format=p010le" \ # Hardware-resized via GPU to 1920px width, auto height, 10-bit format (p010le)
  -color_primaries bt2020 \      # Sets BT.2020 color primaries (the wide color gamut standard for HDR)
  -color_trc smpte2084 \         # Sets the Transfer Characteristics to SMPTE 2084 (PQ / HDR10 standard)
  -colorspace bt2020nc \         # Sets the BT.2020 non-constant luminance color matrix for accurate colors
  
  # 5. AUDIO SETTINGS
  -c:a ac3 \                     # Encodes the audio stream into Dolby Digital (AC-3) format
  -b:a 384k \                    # Sets the audio bitrate to 384 kbps (great for 5.1 surround or high-quality stereo)
  -ar 48000 \                    # Sets the audio sampling rate to 48 kHz
  
  # 6. OUTPUT & STREAMING OPTIMIZATION
  -movflags +faststart \         # Moves metadata to the front of the file (allows web streaming and instant playback)
  iphone_compatible.mp4          # The final optimized output file name and format
  ```

# RTX 50xx, Apple compatible
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -y -i <inputfile>.HDR.H.265.mkv -tag:v hvc1 -c:v hevc_nvenc -preset p7 -profile:v main10 -b:v 1620k -2pass 1 -vf "scale_cuda=1920:-2:format=p010le" -color_primaries bt2020 -color_trc smpte2084 -colorspace bt2020nc -spatial-aq 1 -temporal-aq 1 -bf 4 -c:a ac3 -b:a 384k -ar 48000 -movflags +faststart iphone_compatible_xyz.mp4

```
ffmpeg \
  # 1. HARDWARE ACCELERATION (INPUT)
  -hwaccel cuda \                 # Enables hardware-accelerated decoding using Nvidia CUDA
  -hwaccel_output_format cuda \  # Keeps decoded frames in GPU memory to avoid slow CPU-GPU copying
  -y \                            # Automatically overwrites the output file if it already exists
  
  # 2. INPUT FILE
  -i  <inputfile>.HDR.H.265.mkv \ # Path to your source 4K HDR movie file
  
  # 3. VIDEO CODEC & QUALITY SETTINGS
  -tag:v hvc1 \                  # Sets the hvc1 FourCC tag (strictly required for HEVC playback on Apple devices)
  -c:v hevc_nvenc \              # Uses the Nvidia hardware-accelerated HEVC/H.265 encoder
  -preset p7 \                   # Preset p7 (slowest encoding speed, but delivers the highest NVENC quality)
  -profile:v main10 \            # Main 10 profile (enables 10-bit color depth, essential for HDR)
  -b:v 1620k \                   # Targets a video bitrate of 1620 kbps
  -2pass 1 \                     # Enables 2-pass rate control mode for NVENC to improve bitrate distribution
  
  # 4. VIDEO FILTERS & COLOR METADATA
  -vf "scale_cuda=1920:-2:format=p010le" \ # Hardware-resized via GPU to 1920px width, auto height, 10-bit format (p010le)
  -color_primaries bt2020 \      # Sets BT.2020 color primaries (the wide color gamut standard for HDR)
  -color_trc smpte2084 \         # Sets the Transfer Characteristics to SMPTE 2084 (PQ / HDR10 standard)
  -colorspace bt2020nc \         # Sets the BT.2020 non-constant luminance color matrix for accurate colors
  
  # 5. ADVANCED NVENC OPTIMIZATIONS
  -spatial-aq 1 \                # Enables Spatial Adaptive Quantization (adjusts quality based on frame complexity)
  -temporal-aq 1 \               # Enables Temporal Adaptive Quantization (reduces compression artifacts in moving scenes)
  -bf 4 \                        # Sets the number of consecutive B-frames to 4 for better compression efficiency
  
  # 6. AUDIO SETTINGS
  -c:a ac3 \                     # Encodes the audio stream into Dolby Digital (AC-3) format
  -b:a 384k \                    # Sets the audio bitrate to 384 kbps (great for 5.1 surround or high-quality stereo)
  -ar 48000 \                    # Sets the audio sampling rate to 48 kHz
  
  # 7. OUTPUT & STREAMING OPTIMIZATION
  -movflags +faststart \         # Moves metadata to the front of the file (allows web streaming and instant playback)
  iphone_compatible_xyz.mp4      # The final optimized output file name
```

```
# ==============================================================================
# ENCODER ARCHITECTURE COMPARISON: COMMAND 1 vs COMMAND 2
# ==============================================================================
# These commands look similar but trigger fundamentally different NVENC pipelines.
#
# 1. Rate Control Conflict (-multipass vs -2pass):
#    Command 1 utilizes NVENC's native hardware multipass (-multipass fullres) 
#    combined with lookahead (-rc-lookahead 32). This lets the GPU scan ahead 32 
#    frames within a single encoding pass to optimize bits for high-motion scenes.
#    Command 2 utilizes FFmpeg's legacy driver-level two-pass control (-2pass 1). 
#    Crucially, enabling '-2pass 1' implicitly disables lookahead processing in 
#    NVENC, changing how the bitrate budget is calculated.
#
# 2. Adaptive Quantization (AQ) vs Presets:
#    Command 2 explicitly activates spatial-aq and temporal-aq. This shifts bits 
#    away from high-frequency or fast-moving areas where the human eye cannot 
#    spot artifacts, preserving quality in flat zones (like skies). Command 1 
#    omits these flags, relying solely on the rigid defaults of the 'p7' preset.
#
# 3. GOP and Frame Topology:
#    Command 2 hardcodes B-frames (-bf 4) to increase compression efficiency 
#    for static scenes, while Command 1 allows the encoder to dynamically 
#    determine the optimal B-frame structure.
#
# SUMMARY: Command 1 is optimized for modern hardware-driven lookahead efficiency. 
# Command 2 relies on traditional multi-pass logic and strict psychoacoustic tuning.
# ==============================================================================


```
