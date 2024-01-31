1. Get your system updates
    
    `$` `sudo apt update`

    `$` `sudo apt upgrade -y`

0. Install the required programs to run kvm.

    `$` `sudo apt install -y bridge-utils qemu-kvm cloud-utils`

0. Verify kvm is installed and working.

    `$` `kvm-ok`

0. Set your net filter config.

    `$` `sudo vi /etc/modules-load.d/br_nf.conf`

    ```
    br_netfilter
    ```

0. Apply the config.

    `$` `sudo modprobe br_netfilter`

    `$` `sudo vi /etc/sysctl.d/10-disable-firewall-on-bridge.conf`

    ```
    net.bridge.bridge-nf-call-ip6tables = 0
    net.bridge.bridge-nf-call-iptables = 0
    net.bridge.bridge-nf-call-arptables = 0
    ```

0. Set the ip forwarding rules.

    `$` `sudo vi /etc/sysctl.d/10-ip-forwarding.conf`

    ```
    net.ipv4.ip_forward = 1
    net.ipv6.conf.default.forwarding = 1
    net.ipv6.conf.all.forwarding = 1
    ```

0. check the bridge to see if it's working 

    `$` `sudo sysctl -a | grep net.bridge.bridge`

0. Make the directory for qemu

    `$` `sudo mkdir -p /etc/qemu/`

0. Allow that bridge via the config file

    `$` `echo "allow br0" | sudo tee /etc/qemu/bridge.conf`

0. Add the bridge to your interface list

    `$` `sudo ip link add name br0 type bridge`

0. Give the bridge an IP address.

    `$` `sudo ip address add 172.16.0.1/24 dev br0`

0. Set the bridge to be up.

    `$` `sudo ip link set br0 up`

0. Make directories for images and logs.

    `$` `sudo mkdir -p /var/log/qemu/`

    `$` `sudo mkdir -p /var/kvm/images`

    `$` `sudo chown student: /var/kvm/images`

0. Change to the image directory.

    `$` `cd /var/kvm/images/`

0. Generate a MAC address 

    `$` `MAC=$(printf "aa:a3:a3:%02x:%02x:%02x\n" $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)))`

    `$` `KEY1=$(cat ~/.ssh/id_rsa.pub)`

0. Set your meta data
 
    `$` `vim meta-data.yaml`

    ```
    instance-id: sean3
    local-hostname: sean3
    ```

0. Set the user data

    `$` `vim user-data.yaml`

    ```
    #cloud-config
    users:
      - name: root
        lock_passwd: false
        plain_text_passwd: 'alta3'
        shell: /bin/bash
      - name: ubuntu
        lock_passwd: false
        plain_text_passwd: 'alta3'
        shell: /bin/bash
        sudo: ['ALL=(ALL) NOPASSWD:ALL']
        groups: sudo
        ssh-authorized-keys:
        - ssh-rsa $KEY1
    ```

0. Set your network configuration

    `$` `vim net-config.yaml`
   
    ```
    version: 2
    ethernets:
        ens3:
          dhcp4: false
          addresses:
          - 172.16.0.5/24
          optional: true
          gateway4: 172.16.0.1
          nameservers:
            addresses: [8.8.8.8]
    ```

0. Download the OVA or, in this case, the VMDK file.

    `$` `wget https://cloud-images.ubuntu.com/releases/22.04/release/ubuntu-22.04-server-cloudimg-amd64.vmdk`

    > If downloading the OVA, you will want to run the below command because you want to get the vmdk out of it.
    
    > `tar -xvf cml2_p_2.6.1-11_amd64-11.ova`

0. Convert to a qcow2.

    `$` `qemu-img convert -O qcow2 /var/kvm/images/ubuntu-22.04-server-cloudimg-amd64.vmdk /var/kvm/images/ubuntu-22.04-server-cloudimg-amd64.img`

0. Generate the cloud-init file. 

    `$` `cloud-localds cloud-init.iso user-data.yaml meta-data.yaml --network-config=net-config.yaml`

0. Enable proper routing.

    `$` `sudo /sbin/iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE`

    `$` `sudo /sbin/iptables -A FORWARD -i ens3 -o br0 -m state  --state RELATED,ESTABLISHED -j ACCEPT`

    `$` `sudo /sbin/iptables -A FORWARD -i br0 -o ens3 -j ACCEPT`

0. Run the image.

    `$` `sudo /usr/bin/qemu-system-x86_64    -enable-kvm    -drive file=/var/kvm/images/ubuntu-22.04-server-cloudimg-amd64.img,if=virtio    -cdrom /var/kvm/images/cloud-init.iso    -display curses    -nographic    -smp cpus=1    -m 1G    -net nic,netdev=tap1,macaddr=$MAC1    -netdev bridge,id=tap1,br=br0   -d int    -D /var/log/qemu/qemu.log`

    > You should now be able to ssh to the IP: `ssh root@172.X.X.X`
