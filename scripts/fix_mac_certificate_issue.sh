#!/bin/zsh
(security find-certificate -a -p ls /System/Library/Keychains/SystemRootCertificates.keychain && security find-certificate -a -p ls /Library/Keychains/System.keychain) > $HOME/.mac-ca-roots
 export REQUESTS_CA_BUNDLE="$HOME/.mac-ca-roots"
# shellcheck disable=SC1090
source ~/.zshrc