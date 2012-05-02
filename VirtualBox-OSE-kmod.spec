# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%define buildforkernels newest

# In prerelease builds (such as betas), this package has the same
# major version number, while the kernel module abi is not guarranteed
# to be stable. This is so that we force the module update in sync with
# userspace.
#global prerel beta3
%global prereltag %{?prerel:_%(awk 'BEGIN {print toupper("%{prerel}")}')}

# Allow only root to access vboxdrv regardless of the file mode
# use only for debugging!
%bcond_without hardening

Name:           VirtualBox-OSE-kmod
Version:        4.1.12
Release:        1%{?dist}.4

Summary:        Kernel module for VirtualBox-OSE
Group:          System Environment/Kernel
License:        GPLv2 or CDDL
URL:            http://www.virtualbox.org/wiki/VirtualBox
# This filters out the XEN kernel, since we don't run on XEN
Source1:        VirtualBox-OSE-kmod-1.6.4-kernel-variants.txt
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%global AkmodsBuildRequires %{_bindir}/kmodtool, VirtualBox-OSE-kmodsrc = %{version}%{?prereltag}, xz, time
BuildRequires:  %{AkmodsBuildRequires}

# needed for plague to make sure it builds for i586 and i686
ExclusiveArch:  i686 x86_64

# get the proper build-sysbuild package from the repo, which
# tracks in all the kernel-devel packages
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} --filterfile %{SOURCE1} 2>/dev/null) }


%description
Kernel module for VirtualBox-OSE


%prep
%setup -T -c
tar --use-compress-program xz -xf %{_datadir}/%{name}-%{version}/%{name}-%{version}.tar.xz

# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} --filterfile %{SOURCE1} 2>/dev/null

# This is hardcoded in Makefiles
# Kto zisti, preco tu nefunguje %%without hardening ma u mna nanuk
%{?with_hardening:find %{name}-%{version} -name Makefile |xargs sed 's/-DVBOX_WITH_HARDENING//' -i}

for kernel_version in %{?kernel_versions} ; do
    cp -al %{name}-%{version} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    for module in vbox{drv,guest}; do
        make VBOX_USE_INSERT_PAGE=1 %{?_smp_mflags} -C "${kernel_version##*___}" SUBDIRS="${PWD}/_kmod_build_${kernel_version%%___*}/${module}"  modules
    done
    cp _kmod_build_${kernel_version%%___*}/{vboxdrv/Module.symvers,vboxnetadp}
    cp _kmod_build_${kernel_version%%___*}/{vboxdrv/Module.symvers,vboxnetflt}
    cp _kmod_build_${kernel_version%%___*}/{vboxguest/Module.symvers,vboxsf}
    cp _kmod_build_${kernel_version%%___*}/{vboxguest/Module.symvers,vboxvideo}
    for module in vbox{netadp,netflt,sf,video,pci}; do
        make VBOX_USE_INSERT_PAGE=1 %{?_smp_mflags} -C "${kernel_version##*___}" SUBDIRS="${PWD}/_kmod_build_${kernel_version%%___*}/${module}"  modules
    done
done


%install
rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT

for kernel_version in %{?kernel_versions}; do
    install -d ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
    install _kmod_build_${kernel_version%%___*}/*/*.ko ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
done

%{?akmod_install}


%check
# If we built modules, check if it was everything the kmodsrc package provided
MODS=$(find $(ls -d $RPM_BUILD_ROOT/lib/modules/* |head -n1) -name '*.ko' -exec basename '{}' \; |wc -l)
DIRS=$(ls %{name}-%{version} |wc -l)
[ $MODS = $DIRS ] || [ $MODS = 0 ]


%changelog
* Wed May 02 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.12-1.4
- rebuild for updated kernel

* Sun Apr 22 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.12-1.3
- rebuild for updated kernel

* Sat Apr 14 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.12-1.2
- reuilt for updated kernel

* Fri Apr 13 2012 Sérgio Basto <sergio@serjux.com> - 4.1.12-1.1
- New release

* Thu Apr 12 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.10-2.2
- rebuild for updated kernel

* Wed Apr 4 2012 Sérgio Basto <sergio@serjux.com> - 4.1.10-2.1
- Need to create akmod too. 

* Wed Apr 4 2012 Sérgio Basto <sergio@serjux.com> - 4.1.10-1.1
- New release, for new kernel version major release.

* Tue Apr 03 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.11
- rebuild for updated kernel

* Wed Mar 21 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.10
- rebuild for updated kernel

* Wed Mar 21 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.9
- rebuild for updated kernel

* Sun Mar 18 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.8
- rebuild for updated kernel

* Thu Mar 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.7
- rebuild for updated kernel

* Sat Mar 03 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.6
- rebuild for updated kernel

* Thu Mar 01 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.5
- rebuild for updated kernel

* Wed Feb 22 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.4
- rebuild for updated kernel

* Wed Feb 15 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.3
- rebuild for updated kernel

* Thu Feb 09 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.2
- rebuild for updated kernel

* Mon Feb 6 2012 Sérgio Basto <sergio@serjux.com> - 4.1.8-1
- New release.
- added time package to AkmodsBuildRequires

* Fri Feb 03 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.6-1.6
- rebuild for updated kernel

* Tue Jan 24 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.6-1.5
- rebuild for updated kernel

* Sun Jan 15 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.6-1.4
- rebuild for updated kernel

* Mon Jan 09 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.6-1.3
- rebuild for updated kernel

* Wed Jan 04 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.6-1.2
- rebuild for updated kernel

* Sat Dec 24 2011 Sérgio Basto <sergio@serjux.com> - 4.1.6-1.1
- New release

* Fri Dec 23 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.1.2-2.3
- rebuild for updated kernel

* Sat Dec 17 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.1.2-2.2
- rebuild for updated kernel

* Wed Dec 14 2011 Sérgio Basto <sergio@serjux.com> - 4.1.2-2.2
- re-add vboxpci and check, because kernel updates have fixed vboxpci compile.

* Mon Nov 28 2011 Sérgio Basto <sergio@serjux.com> - 4.1.2-1.1
- Update to new version
- remove %clean from spec 
- we had remove vboxpci from build because fails to compile with latest F15 kernel, so need hack
  %check to not fail, temporally I hope.

* Wed Nov 23 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.13
- rebuild for updated kernel

* Sun Nov 13 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.12
- rebuild for updated kernel

* Wed Nov 02 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.11
- rebuild for updated kernel

* Sun Oct 30 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.10
- rebuild for updated kernel

* Wed Oct 19 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.9
- rebuild for updated kernel

* Fri Oct 07 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.8
- rebuild for updated kernel

* Sat Sep 03 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.7
- rebuild for updated kernel

* Wed Aug 17 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.6
- rebuild for updated kernel

* Sun Jul 31 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.5
- rebuild for updated kernel

* Tue Jul 12 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.0.4-2.4
- Rebuild for updated kernel

* Wed Jun 15 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.0.4-2.3
- rebuild for updated kernel

* Sat Jun 04 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.0.4-2.2
- rebuild for updated kernel

* Sat May 28 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.0.4-2.1
- rebuild for updated kernel

* Sat May 28 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.0.4-2
- rebuild for F15 release kernel

* Mon Apr 04 2011 Lubomir Rintel <lkundrak@v3.sk> - 4.0.4-1
- New release

* Mon Feb 14 2011 Lubomir Rintel <lkundrak@v3.sk> - 4.0.2-2
- Fix module symbol versioning

* Sat Feb 05 2011 Lubomir Rintel <lkundrak@v3.sk> - 4.0.2-1
- New release

* Tue Jan 11 2011 Lubomir Rintel <lkundrak@v3.sk> - 3.2.10-2
- Fix build with 2.6.37

* Tue Nov 16 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.10-1
- New release

* Mon Jul 12 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.6-1
- New release

* Fri Jun 18 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.4-1
- New release

* Mon May 10 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.0-1
- Release

* Mon May 10 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.0-0.2.beta2
- Beta 2

* Thu Apr 29 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.0-0.1.beta1
- Beta

* Fri Mar 26 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.1.6-1
- New release

* Wed Feb 17 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.1.4-1
- New release

* Tue Jan 26 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.1.2-1
- New release

* Sun Dec 06 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.1.0-1
- stable

* Tue Nov 24 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.1.0-0.1.beta2
- Bump to beta2

* Thu Nov 12 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.1.0-0.1.beta1
- Bump to beta

* Sun Nov 01 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.10-1
- Version bump

* Wed Oct 07 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.8-1
- Version bump

* Mon Aug 17 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.6-1
- Update to 3.0.6, re-enable hardening

* Mon Aug 17 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.4-4
- Source package is now xz-compressed

* Sat Aug 15 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.4-2
- Make it possible to disable hardening, do so by default

* Sun Aug 09 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.4-1
- New release
- Check that we build all modules present

* Tue Aug 04 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.2-2
- Add netadp bmodule (Vlastimil Holer, #744)

* Sun Jul 12 2009 Jonathan Dieter <jdieter@gmail.com> - 3.0.2-1
- New release

* Fri Jul 03 2009 Jonathan Dieter <jdieter@gmail.com> - 3.0.0-1
- New release

* Thu Jul 02 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.2.4-2
- Enable the DRM module

* Fri Jun 05 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 2.2.4-1.1
- rebuild for final F11 kernel

* Sun May 31 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.2.4-1
- New release

* Sun May 03 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.2.2-1
- New release

* Sat Apr 25 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.2.0-1
- New release

* Fri Apr 24 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.1.4-2
- Fix akmod requires

* Sat Mar 14 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.1.4-1
- Update to 2.1.4
- Enable VBOX_USE_INSERT_PAGE (VirtualBox #3403)
- Use packed source code tarball

* Sat Jan 24 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.1.2-1
- Update to 2.1.2

* Sun Jan 11 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 2.1.0-2
- Cosmetic fixes
- Fix build of standalone akmod

* Tue Dec 30 2008 Lubomir Rintel <lkundrak@v3.sk> - 2.1.0-1
- New upstream version

* Tue Sep 02 2008 Lubomir Rintel <lkundrak@v3.sk> - 1.6.4-2
- Use the VirtualBox-OSE build-time generated source tree

* Tue Sep 02 2008 Lubomir Rintel <lkundrak@v3.sk> - 1.6.4-1
- New upstream version, don't build for Xen needlessly

* Sat Mar 08 2008 Till Maas <opensource till name> - 1.5.6-3
- rewrite to a kmodspec for rpmfusion

* Fri Mar 07 2008 Lubomir Kundrak <lkundrak@redhat.com> - 1.5.6-2
- Fix build by passing kernel source tree path to make

* Sun Feb 24 2008 Till Maas <opensource till name> - 1.5.6-1
- update to new version

* Sun Jan 20 2008 Till Maas <opensource till name> - 1.5.4-1
- initial spec, split out from VirtualBox-OSE spec
