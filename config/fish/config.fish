pyfiglet -s -f thick $(fastfetch -s os --format json | jq -r '.[0].result.name') && fastfetch -l none

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end
