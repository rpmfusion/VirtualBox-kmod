VERSION=6.1.6
REL=1
RAWHIDE=33
REPOS="32 31 30"

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
rfpkg ci -c && git show
rfpkg srpm && copr-cli build sergiomb/vboxfor23 VirtualBox-kmod-$VERSION-$REL.fc$RAWHIDE.src.rpm
#rfpkg srpm && mock -r fedora-27-x86_64-rpmfusion_free --no-clean --rebuild smplayer-17.5.0-1.fc27.src.rpm
#cp VirtualBox-kmod.spec VirtualBox-kmod.spec.new
#git reset HEAD~1
#git rm kernel-4.10.0-0.rc5.lnkops.v2.patch
echo Press enter to continue; read dummy;
#koji-rpmfusion watch-task
fi

if test $stage -le 1
then
echo STAGE 1
BRANCH1=f$RAWHIDE
BRANCH2=fc$RAWHIDE
koji-rpmfusion tag-build $BRANCH1-free-override VirtualBox-$VERSION-$REL.$BRANCH2
(koji-rpmfusion wait-repo $BRANCH1-free-build --build=VirtualBox-$VERSION-$REL.$BRANCH2 && \
rfpkg push && rfpkg build --nowait ) &
fi

if test $stage -le 2
then
echo STAGE 2
for repo in $REPOS ; do
BRANCH1=f$repo
BRANCH2=fc$repo
echo Press enter tag-build $BRANCH1 to continue; read dummy;
koji-rpmfusion tag-build $BRANCH1-free-override VirtualBox-$VERSION-$REL.$BRANCH2
(koji-rpmfusion wait-repo $BRANCH1-free-build --build=VirtualBox-$VERSION-$REL.$BRANCH2 && \
git checkout $BRANCH1 && git merge master && git push && rfpkg build --nowait; git checkout master) &
done
fi

if test $stage -le 3
then
echo STAGE 3
BRANCH1=el7
BRANCH2=el7
echo Press enter tag-build $BRANCH1 to continue; read dummy;
koji-rpmfusion tag-build el7-free-override VirtualBox-$VERSION-$REL.el7
koji-rpmfusion wait-repo $BRANCH1-free-build --build=VirtualBox-$VERSION-$REL.$BRANCH2
git checkout $BRANCH1 && git merge master && git push && rfpkg build --nowait; git checkout master
fi
echo Finish
