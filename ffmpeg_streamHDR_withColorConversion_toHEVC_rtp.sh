```
ffmpeg -re -hwaccel cuda -hwaccel_output_format cuda -i "$1" -tag:v hvc1 \
-vf "scale_cuda=1920:-2:format=p010le,hwdownload,format=p010le,zscale=t=linear:npl=100,tonemap=tonemap=hable:desat=0.5,zscale=t=bt709:p=bt709:m=bt709,format=yuv420p,hwupload_cuda" \
-c:v hevc_nvenc -preset p1 -g 24 -strict_gop 1 -rc cbr -b:v 15M -maxrate:v 15M -bufsize 5M -profile:v main \
-c:a ac3 -ac 2 -b:a 384k -muxrate 16M -flush_packets 0 -f rtp_mpegts -fec prompeg=l=10:d=5 "rtp://239.1.1.1:5004?localport=5004"
```

# To convert from HDR to 8bit, will use CPU (no way to do it on GPU)
