VERSION=7.1.12
REL=1
RAWHIDE=43
REPOS="f42 f41 el9"

if [ -z "$1" ]
then
      stage=0
else
      stage=$1
fi

git checkout master
git pull

if test $stage -le 0
then
echo STAGE 0
rpmdev-bumpspec -n $VERSION -c "Update to $VERSION" VirtualBox-kmod.spec
echo "checking patches"
rfpkg prep
echo Press enter to build on copr or n to skip; read dummy;
if [[ "$dummy" != "n" ]]; then
rfpkg copr-build sergiomb/vboxfor23
fi
#rfpkg srpm && mock -r fedora-27-x86_64-rpmfusion_free --no-clean --rebuild smplayer-17.5.0-1.fc27.src.rpm
#cp VirtualBox-kmod.spec VirtualBox-kmod.spec.new
#git reset HEAD~1
#git rm kernel-4.10.0-0.rc5.lnkops.v2.patch
#koji-rpmfusion watch-task
fi

if test $stage -le 1; then
echo STAGE 1
rfpkg ci -c && git show
fi
if test $stage -le 2; then
echo STAGE 2
BRANCH1=f$RAWHIDE
BRANCH2=fc$RAWHIDE
echo "koji-rpmfusion tag-build $BRANCH1-free-override VirtualBox-$VERSION-$REL.$BRANCH2"
echo "koji-rpmfusion wait-repo $BRANCH1-free-build --build=VirtualBox-$VERSION-$REL.$BRANCH2 && "
echo "git checkout master && rfpkg build --nowait "
echo Press enter tag-build rawhide to continue or n to skip; read dummy;
if [[ "$dummy" != "n" ]]; then
echo koji-rpmfusion tag-build $BRANCH1-free-override VirtualBox-$VERSION-$REL.$BRANCH2
git checkout master && rfpkg push
koji-rpmfusion tag-build $BRANCH1-free-override VirtualBox-$VERSION-$REL.$BRANCH2
(koji-rpmfusion wait-repo $BRANCH1-free-build --build=VirtualBox-$VERSION-$REL.$BRANCH2 && \
git checkout master && rfpkg build --nowait ) &
fi
fi

if test $stage -le 3; then
echo STAGE 3
for repo in $REPOS ; do
BRANCH1=$repo
BRANCH2=$repo
if [[ $repo == f* ]]; then
    BRANCH2=fc${repo:1}
fi
echo "koji-rpmfusion tag-build $BRANCH1-free-override VirtualBox-$VERSION-$REL.$BRANCH2"
echo "koji-rpmfusion wait-repo $BRANCH1-free-build --build=VirtualBox-$VERSION-$REL.$BRANCH2 &&"
echo "git checkout $BRANCH1 && rfpkg build --nowait; git checkout master"
echo Press enter tag-build $BRANCH1 to continue or n to skip; read dummy;
if [[ "$dummy" != "n" ]]; then
echo koji-rpmfusion tag-build $BRANCH1-free-override VirtualBox-$VERSION-$REL.$BRANCH2
git checkout $BRANCH1 && git merge master && git push
koji-rpmfusion tag-build $BRANCH1-free-override VirtualBox-$VERSION-$REL.$BRANCH2
(koji-rpmfusion wait-repo $BRANCH1-free-build --build=VirtualBox-$VERSION-$REL.$BRANCH2 && \
git checkout $BRANCH1 && rfpkg build --nowait; git checkout master) &
fi
done
fi

echo Finish
