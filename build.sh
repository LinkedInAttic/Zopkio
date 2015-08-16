#!/bin/bash
set -e  # fail early.  fail fast.
set -x  # show your work.

# assumptions:
## user is zopkio_pubnub
## destination is /opt/pubnub/zopkio_pubnub, and we're cd'd into that dir.

dest=/opt/pubnub/zopkio_pubnub
[ ! -e ${dest} ] && (echo ${dest} not found.; exit 1)

## $PWD is the extracted tarball given to pn-build-svc. i.e. the git checkout.

if [ -e requirements.txt ]; then
    virtualenv ${dest}
    . ${dest}/bin/activate
    pip install -r requirements.txt
fi

# cleanups
[ -e .git ] && rm -rf .git*
rm -f *.md
rm -rf tests unittests
rm -rf ops