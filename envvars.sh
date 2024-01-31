#!/bin/bash
# This script should ALWAYS be run with command `source envvars.sh`, otherwise the env's will set for new sessions but not the current one. 
set_env_var() {
    local var_name=$1
    local var_value=$2
    local profile_file=$3

    eval export $var_name=\"$var_value\"

    if ! grep -q "export $var_name=" $profile_file; then
        echo "export $var_name=\"$var_value\"" >> $profile_file
    fi
}

main() {
    local profile_file="$HOME/.bashrc"
    # We need to add the actual IP address below. We'll also need to ensure accuracy of topo.yml location
    set_env_var "CML_HOST" "<ip address of CML server, wherever that'll be>" "$profile_file"  
    set_env_var "CML_USERNAME" "admin" "$profile_file"
    set_env_var "CML_PASSWORD" "alta3123" "$profile_file"
    set_env_var "CML_LAB_FILE" "$HOME/topo.yml" "$profile_file"
    set_env_var "CML_VERIFY_CERT" "false" "$profile_file"

}


main
