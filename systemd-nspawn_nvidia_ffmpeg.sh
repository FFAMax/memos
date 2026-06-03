debootstrap --arch=amd64 --components=main --variant=minbase noble /var/lib/machines/ubuntu24-ffmpeg http://archive.ubuntu.com/ubuntu/
apt install curl wget nvidia-driver-575-open cuda-opencl-12-9  cuda-nvtx-12-9  cuda-nvrtc-12-9  cuda-nvcc-12-9 cuda-cccl-12-9  cuda-crt-12-9 cuda-command-line-tools-12-9  cuda-nvcc-12-9
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
dpkg -i cuda-keyring_1.1-1_all.deb

# В общем, там такая история, что установить сразу пакеты и все необходимые при бутстрапе нельзя. Нужно накатить минимальный образ, дальше зайти в сам контейнер и уже изнутри контейнера устанавливать пакеты, иначе зависимости не разрулятся.
# Проверено с GTX 1080Ti

systemd-nspawn -D /var/lib/machines/ubuntu24-ffmpeg/ \
  --bind=/mnt/hostdir:/root/localdir \
  --bind=/dev/nvidia0 \
  --bind=/dev/nvidiactl \
  --bind=/dev/nvidia-uvm \
  --bind=/dev/nvidia-uvm-tools \
  --bind-ro=/usr/lib/x86_64-linux-gnu/libcuda.so.1 \
  --bind-ro=/usr/lib/x86_64-linux-gnu/libnvcuvid.so.1 \
  --bind-ro=/usr/lib/x86_64-linux-gnu/libnvidia-encode.so.1 \
  --bind-ro=/usr/lib/x86_64-linux-gnu/libnvidia-ptxjitcompiler.so.1
